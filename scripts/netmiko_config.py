#!/usr/bin/env python3
"""
Network Device Configuration Script using Netmiko
Author: Network Automation Team
Description: Automates configuration deployment to network devices
"""

import yaml
import logging
from netmiko import ConnectHandler
from datetime import datetime
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/netmiko_config.log'),
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

def load_configuration(config_file):
    """
    Load configuration commands from file
    
    Args:
        config_file: Path to configuration file
    
    Returns:
        List of configuration commands
    """
    try:
        with open(config_file, 'r') as f:
            commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        logger.info(f"Loaded {len(commands)} configuration commands")
        return commands
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found")
        return []

def configure_device(device, commands):
    """
    Configure a network device using Netmiko
    
    Args:
        device: Device dictionary with connection parameters
        commands: List of configuration commands
    
    Returns:
        Configuration output or None if failed
    """
    try:
        logger.info(f"Connecting to {device['host']}...")
        
        connection = ConnectHandler(**device)
        
        # Enter enable mode
        connection.enable()
        
        # Enter configuration mode and send commands
        logger.info(f"Sending {len(commands)} commands to {device['host']}")
        output = connection.send_config_set(commands)
        
        # Save configuration
        save_output = connection.save_config()
        
        logger.info(f"Configuration completed successfully on {device['host']}")
        
        connection.disconnect()
        
        return {
            'status': 'success',
            'output': output,
            'save_output': save_output
        }
    
    except Exception as e:
        logger.error(f"Failed to configure {device['host']}: {str(e)}")
        return {
            'status': 'failed',
            'error': str(e)
        }

def backup_configuration(device):
    """
    Backup device configuration before making changes
    
    Args:
        device: Device dictionary with connection parameters
    
    Returns:
        Configuration backup or None if failed
    """
    try:
        connection = ConnectHandler(**device)
        connection.enable()
        
        # Get running configuration
        config = connection.send_command('show running-config')
        
        # Create backup directory if it doesn't exist
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # Save backup with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_dir}/{device['host']}_{timestamp}.cfg"
        
        with open(backup_file, 'w') as f:
            f.write(config)
        
        logger.info(f"Configuration backed up to {backup_file}")
        connection.disconnect()
        
        return backup_file
    
    except Exception as e:
        logger.error(f"Failed to backup configuration from {device['host']}: {str(e)}")
        return None

def main():
    """
    Main function to orchestrate device configuration
    """
    print("\n=== Network Device Configuration Tool ===")
    print("Using Netmiko for automated configuration deployment\n")
    
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('backups', exist_ok=True)
    
    # Load device inventory
    devices = load_device_inventory()
    
    # Load configuration commands
    config_file = input("Enter configuration file path (e.g., config/vlan_config.txt): ")
    commands = load_configuration(config_file)
    
    if not commands:
        logger.error("No configuration commands loaded. Exiting.")
        return
    
    # Ask for confirmation
    print(f"\nReady to configure {len(devices)} device(s) with {len(commands)} command(s)")
    confirm = input("Do you want to proceed? (yes/no): ")
    
    if confirm.lower() != 'yes':
        logger.info("Configuration cancelled by user")
        return
    
    # Configure each device
    results = []
    for device in devices:
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing device: {device['host']}")
        logger.info(f"{'='*50}")
        
        # Backup configuration first
        backup_file = backup_configuration(device)
        
        # Apply configuration
        result = configure_device(device, commands)
        result['device'] = device['host']
        result['backup'] = backup_file
        results.append(result)
    
    # Summary report
    print("\n" + "="*50)
    print("Configuration Summary")
    print("="*50)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    failed_count = len(results) - success_count
    
    print(f"Total devices: {len(results)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    
    if failed_count > 0:
        print("\nFailed devices:")
        for result in results:
            if result['status'] == 'failed':
                print(f"  - {result['device']}: {result['error']}")
    
    logger.info("Configuration process completed")

if __name__ == "__main__":
    main()
