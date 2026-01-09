# Network Automation Framework

Automated network device configuration and backups using Python Netmiko and NAPALM. Ansible playbooks for VLAN deployments and configuration drift detection across simulated switching environments.

## 🚀 Features

### Python Automation Scripts
- **Netmiko Configuration Management**: Automated deployment of network device configurations
- **NAPALM Backup System**: Automated configuration backups with device facts collection
- **Multi-vendor Support**: Compatible with Cisco IOS, NXOS, Arista EOS, and Juniper devices
- **Comprehensive Logging**: Detailed execution logs for troubleshooting

### Ansible Playbooks
- **VLAN Deployment**: Standardized VLAN configuration across switching infrastructure
- **Configuration Drift Detection**: Automated detection of unauthorized configuration changes
- **Backup Integration**: Built-in configuration backup before changes
- **Verification Tasks**: Post-deployment verification and reporting

## 📁 Project Structure

```
network-automation-framework/
├── scripts/
│   ├── netmiko_config.py       # Network device configuration script
│   └── napalm_backup.py        # Automated backup script
├── playbooks/
│   ├── vlan_deployment.yml     # VLAN deployment playbook
│   └── config_drift_detection.yml  # Drift detection playbook
├── config/
│   ├── devices.yml             # Device inventory file
│   └── vlan_config.txt         # Sample VLAN configuration
├── logs/                       # Execution logs
├── backups/                    # Configuration backups
├── reports/                    # Verification reports
└── requirements.txt            # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Ansible 2.9+
- Network device access (SSH)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/gopi-pathuri/network-automation-framework.git
cd network-automation-framework
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Ansible collections**
```bash
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install ansible.netcommon
```

4. **Configure device inventory**
Edit `config/devices.yml` with your device information:
```yaml
devices:
  - host: 192.168.1.1
    device_type: cisco_ios
    username: admin
    password: yourpassword
    secret: yourenablepassword
```

## 📖 Usage

### Python Scripts

#### Network Configuration with Netmiko
```bash
cd scripts
python netmiko_config.py
```
Features:
- Loads device inventory from YAML
- Backs up configurations before changes
- Applies configuration commands
- Saves configurations automatically
- Generates summary reports

#### Automated Backups with NAPALM
```bash
python napalm_backup.py
```
Features:
- Multi-vendor configuration backups
- Device facts collection
- Interface information gathering
- Organized backup directory structure
- Timestamped backup files

### Ansible Playbooks

#### VLAN Deployment
```bash
cd playbooks
ansible-playbook -i inventory vlan_deployment.yml
```

Run specific tasks:
```bash
# Backup only
ansible-playbook vlan_deployment.yml --tags backup

# VLAN configuration only
ansible-playbook vlan_deployment.yml --tags vlan_config

# Verification only
ansible-playbook vlan_deployment.yml --tags verify
```

#### Configuration Drift Detection
```bash
ansible-playbook config_drift_detection.yml
```

Run specific stages:
```bash
# Collect current configurations
ansible-playbook config_drift_detection.yml --tags collect

# Compare with baseline
ansible-playbook config_drift_detection.yml --tags compare

# Generate reports
ansible-playbook config_drift_detection.yml --tags report
```

## 📊 Output and Reports

### Directory Structure
```
backups/
├── 192.168.1.1/
    └── switch1_interfaces_timestamp.json
reports/
└── switch1_drift_timestamp.txt
drift_reports/
└── SUMMARY_timestamp.txt```

## 🔧 Configuration Files

### Device Inventory (config/devices.yml)
```yaml
devices:
  - host: 192.168.1.1
    device_type: cisco_ios
    username: admin
    password: password
    secret: secret
  - host: 192.168.1.2
    device_type: cisco_nxos
    username: admin
    password: password
```

### Ansible Inventory
```ini
[switches]
switch1 ansible_host=192.168.1.1 ansible_network_os=ios
switch2 ansible_host=192.168.1.2 ansible_network_os=nxos

[switches:vars]
ansible_connection=network_cli
ansible_user=admin
ansible_password=yourpassword
ansible_become=yes
ansible_become_method=enable
ansible_become_password=yoursecret
```

## 🎯 Key Benefits

✅ **Reduced Manual Effort**: Automated configuration deployment reduces deployment time by 80%

✅ **Standardization**: Ensures consistent VLAN deployment across all switches

✅ **Configuration Drift Detection**: Identifies unauthorized changes quickly

✅ **Backup Automation**: Scheduled backups prevent configuration loss

✅ **Multi-vendor Support**: Works with Cisco, Arista, and Juniper devices

✅ **Comprehensive Logging**: Detailed logs for audit and troubleshooting

## 🔐 Security Considerations

- Store credentials in environment variables or use Ansible Vault
- Use SSH keys instead of passwords where possible
- Implement role-based access control
- Review logs regularly for unauthorized access
- Keep backup files secure with appropriate permissions

## 📚 Dependencies

- **netmiko**: SSH connections to network devices
- **napalm**: Network automation and programmability abstraction layer
- **pyyaml**: YAML file parsing
- **ansible**: Automation platform
- **paramiko**: SSH protocol library

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available for educational and professional use.

## 👨‍💻 Author

Gopi Pathuri
- GitHub: [@gopi-pathuri](https://github.com/gopi-pathuri)

## 🙏 Acknowledgments

- Netmiko and NAPALM communities
- Ansible network automation team
- Network engineering community

---

**Note**: This framework is designed for simulated and lab environments. Always test in non-production environments before deploying to production networks.
