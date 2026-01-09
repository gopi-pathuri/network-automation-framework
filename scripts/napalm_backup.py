#!/usr/bin/env python3
"""
Network Device Backup Script using NAPALM
Author: Network Automation Team
Description: Automated backup of network device configurations
"""

import yaml
import logging
import os
import sys
from datetime import datetime
from napalm import get_network_driver
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/napalm_backup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_device_inventory(inventory_file='config/devices.yml'):
    """
    Load device inventory from YAML file
    
    Args:
        inventory_file: Path to device inventory file
    
    Returns:
        List of device dictionaries
    """
    try:
        with open(inventory_file, 'r') as f:
            inventory = yaml.safe_load(f)
        logger.info(f"Successfully loaded {len(inventory['devices'])} devices from inventory")
        return inventory['devices']
    except FileNotFoundError:
        logger.error(f"Inventory file {inventory_file} not found")
        sys.exit(1)
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        sys.exit(1)

def backup_device_config(device):
    """
    Backup device configuration using NAPALM
    
    Args:
        device: Device dictionary with connection parameters
    
    Returns:
        Dictionary with backup status and file path
    """
    device_type = device.get('device_type', 'cisco_ios')
    hostname = device.get('host')
    
    # Map Netmiko device types to NAPALM drivers
    driver_map = {
        'cisco_ios': 'ios',
        'cisco_xe': 'ios',
        'cisco_nxos': 'nxos',
        'cisco_xr': 'iosxr',
        'arista_eos': 'eos',
        'juniper': 'junos',
        'juniper_junos': 'junos'
    }
    
    napalm_driver = driver_map.get(device_type, 'ios')
    
    try:
        logger.info(f"Connecting to {hostname} using NAPALM driver: {napalm_driver}")
        
        # Get the NAPALM driver
        driver = get_network_driver(napalm_driver)
        
        # Connect to the device
        device_conn = driver(
            hostname=hostname,
            username=device['username'],
            password=device['password'],
            optional_args={'secret': device.get('secret', device['password'])}
        )
        
        device_conn.open()
        
        # Get device facts
        facts = device_conn.get_facts()
        logger.info(f"Connected to {facts.get('hostname', hostname)} - Model: {facts.get('model', 'Unknown')}")
        
        # Get running configuration
        config = device_conn.get_config()
        
        # Create backup directory structure
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_base_dir = 'backups'
        device_backup_dir = os.path.join(backup_base_dir, hostname)
        os.makedirs(device_backup_dir, exist_ok=True)
        
        # Save running configuration
        running_config_file = os.path.join(device_backup_dir, f"{hostname}_running_{timestamp}.cfg")
        with open(running_config_file, 'w') as f:
            f.write(config['running'])
        
        logger.info(f"Running configuration saved to {running_config_file}")
        
        # Save startup configuration if available
        if 'startup' in config and config['startup']:
            startup_config_file = os.path.join(device_backup_dir, f"{hostname}_startup_{timestamp}.cfg")
            with open(startup_config_file, 'w') as f:
                f.write(config['startup'])
            logger.info(f"Startup configuration saved to {startup_config_file}")
        
        # Save device facts
        facts_file = os.path.join(device_backup_dir, f"{hostname}_facts_{timestamp}.json")
        with open(facts_file, 'w') as f:
            json.dump(facts, f, indent=2)
        
        logger.info(f"Device facts saved to {facts_file}")
        
        # Get interface information
        interfaces = device_conn.get_interfaces()
        interfaces_file = os.path.join(device_backup_dir, f"{hostname}_interfaces_{timestamp}.json")
        with open(interfaces_file, 'w') as f:
            json.dump(interfaces, f, indent=2)
        
        logger.info(f"Interface information saved to {interfaces_file}")
        
        # Close connection
        device_conn.close()
        
        return {
            'status': 'success',
            'hostname': hostname,
            'backup_dir': device_backup_dir,
            'timestamp': timestamp,
            'files': {
                'running_config': running_config_file,
                'facts': facts_file,
                'interfaces': interfaces_file
            }
        }
    
    except Exception as e:
        logger.error(f"Failed to backup {hostname}: {str(e)}")
        return {
            'status': 'failed',
            'hostname': hostname,
            'error': str(e)
        }

def compare_configs(device, current_backup, previous_backup=None):
    """
    Compare current backup with previous backup
    
    Args:
        device: Device hostname
        current_backup: Path to current backup file
        previous_backup: Path to previous backup file
    
    Returns:
        Comparison results
    """
    if not previous_backup:
        return "No previous backup available for comparison"
    
    try:
        with open(current_backup, 'r') as f:
            current_config = f.read()
        
        with open(previous_backup, 'r') as f:
            previous_config = f.read()
        
        if current_config == previous_config:
            logger.info(f"No configuration changes detected for {device}")
            return "No changes detected"
        else:
            logger.warning(f"Configuration changes detected for {device}")
            return "Changes detected"
    
    except Exception as e:
        logger.error(f"Failed to compare configurations: {str(e)}")
        return f"Comparison failed: {str(e)}"

def main():
    """
    Main function to orchestrate device backups
    """
    print("\n=== Network Device Backup Tool ===")
    print("Using NAPALM for automated configuration backups\n")
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # Load device inventory
    devices = load_device_inventory()
    
    print(f"Loaded {len(devices)} device(s) from inventory\n")
    
    # Backup each device
    results = []
    for device in devices:
        logger.info(f"\n{'='*50}")
        logger.info(f"Backing up device: {device['host']}")
        logger.info(f"{'='*50}")
        
        result = backup_device_config(device)
        results.append(result)
    
    # Summary report
    print("\n" + "="*50)
    print("Backup Summary")
    print("="*50)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count
    
    print(f"Total devices: {len(results)}")
    print(f"Successful backups: {success_count}")
    print(f"Failed backups: {failed_count}")
    
    if success_count > 0:
        print("\nSuccessful backups:")
        for result in results:
            if result['status'] == 'success':
                print(f"  - {result['hostname']}: Backed up to {result['backup_dir']}")
    
    if failed_count > 0:
        print("\nFailed backups:")
        for result in results:
            if result['status'] == 'failed':
                print(f"  - {result['hostname']}: {result['error']}")
    
    logger.info("Backup process completed")
    
    # Return exit code
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
