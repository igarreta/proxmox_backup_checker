# Proxmox Backup Checker

A comprehensive Python-based backup monitoring system designed to validate backup integrity, check storage availability, and provide reliable notifications for Proxmox and other backup systems.

## Features

🔍 **Backup Validation**
- Directory accessibility checking
- File age verification with configurable time windows
- Minimum size validation with human-readable units
- Free space monitoring with customizable thresholds

📧 **Multi-Channel Notifications**
- Professional email reports via SMTP
- Push notifications via Pushover (critical alerts only)
- Detailed summaries with backup status and metrics

⚙️ **Robust Configuration**
- YAML-based configuration with validation
- Size units parsing (KB, MB, GB, TB)
- Flexible backup definitions per directory
- Environment-based secrets management

📊 **Professional Logging**
- Rotating log files with configurable retention
- Multiple logging formats and rotation schedules
- Stdout/stderr redirection for cron compatibility
- Comprehensive error tracking and debugging

## Installation

### Prerequisites

- Python 3.13+
- Virtual environment support (`venv` or `uv`)
- SMTP server access for email notifications
- Pushover account for push notifications (optional)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd proxmox_backup_checker
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create configuration directories**:
   ```bash
   mkdir -p var log
   mkdir -p ~/etc  # For secrets
   ```

## Configuration

### 1. Backup Configuration (`var/config.yaml`)

Create your backup configuration file:

```yaml
# Email settings (optional, overrides ~/etc/grsrv03.env defaults)
to_email:
  - admin@example.com
  - backup-admin@example.com

# Pushover settings
pushover_priority: -1  # -2 to 2, default -1 (low priority)

# Logging settings
log_level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
log_file: log/proxmox_backup_checker.log

# Storage settings
min_free_space: 100 GB  # Minimum free space required

# Backup definitions
backup_check_list:
  - name: proxmox-vms
    backup_dir: /mnt/backup_usb1/vm-containers/dump
    days: 8          # Check files modified within 8 days
    min_size: 10 GB  # Minimum expected backup size

  - name: homeassistant
    backup_dir: /mnt/backup_usb1/homeassistant
    days: 1
    min_size: 30 GB

  - name: proxmox-config
    backup_dir: /mnt/backup_usb1/proxmox-config/daily
    days: 1
    min_size: 10 KB
```

### 2. SMTP Configuration (`~/etc/grsrv03.env`)

Configure email notifications:

```bash
# SMTP server settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FROM_EMAIL=your-email@gmail.com
TO_EMAIL=admin@example.com
SMTP_TOKEN=your-app-password
```

### 3. Pushover Configuration (`~/etc/pushover.env`)

Configure push notifications (optional):

```bash
# Pushover API credentials
PUSHOVER_TOKEN=your-30-char-app-token
PUSHOVER_USER=your-30-char-user-key
```

## Usage

### Manual Execution

Run the backup checker manually:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run backup check
python main.py

# Or using uv (if available)
uv run python main.py
```

### Automated Execution (Cron)

Add to your crontab for daily execution:

```bash
# Edit crontab
crontab -e

# Add daily backup check at 6:00 AM
0 6 * * * cd /home/rsi/proxmox_backup_checker && /home/rsi/proxmox_backup_checker/.venv/bin/python main.py
```

### Example Output

**Successful run:**
```
=== BACKUP MONITORING STARTED ===
Configuration loaded: 3 backups to check
✅ proxmox-vms: 15.2 GB (3 files, last modified 2 hours ago)
✅ homeassistant: 2.1 GB (1 file, last modified 30 minutes ago)  
✅ proxmox-config: 45.2 KB (5 files, last modified 1 hour ago)
All backups validated successfully
Email summary sent to 2 recipients
=== BACKUP MONITORING COMPLETED in 12.34s ===
```

**With issues detected:**
```
=== BACKUP MONITORING STARTED ===
Configuration loaded: 3 backups to check
❌ proxmox-vms: Directory not accessible
✅ homeassistant: 2.1 GB (1 file, last modified 30 minutes ago)
❌ proxmox-config: 2.1 KB - Below minimum size (10 KB required)
2 issues detected - sending alerts
Email alert sent, Pushover notification sent
=== BACKUP MONITORING COMPLETED in 8.91s ===
```

## Configuration Reference

### Size Units

Supported size units (case insensitive):
- `B` - Bytes
- `KB` - Kilobytes (1,024 bytes)
- `MB` - Megabytes (1,024² bytes)
- `GB` - Gigabytes (1,024³ bytes)
- `TB` - Terabytes (1,024⁴ bytes)

Examples: `1.5 GB`, `500MB`, `10 kb`, `2TB`

### Backup Check Process

For each backup in `backup_check_list`, the system:

1. **Accessibility Check**: Verifies the backup directory is mounted and readable
2. **Free Space Check**: Ensures available space meets `min_free_space` requirement
3. **File Age Check**: Scans for files modified within the specified `days` period
4. **Size Validation**: Calculates total size of recent files vs `min_size` requirement

### Notification Levels

**Email Notifications** (all events):
- Successful backup validation summaries
- Error reports with detailed failure information
- System status and execution metrics

**Pushover Notifications** (critical issues only):
- Backup directories not accessible
- Backups below minimum size requirements
- System failures preventing backup validation

### Pushover Priority Levels

- `-2`: No notification (silent)
- `-1`: Low priority (quiet, default for critical alerts)
- `0`: Normal priority
- `1`: High priority (bypass quiet hours)
- `2`: Emergency (requires acknowledgment, retry until confirmed)

## Logging

### Log Files

Default log location: `log/proxmox_backup_checker.log`

### Log Rotation

- **Default**: Weekly rotation on Monday at midnight
- **Retention**: 4 backup files (4 weeks of history)
- **Alternative**: Daily (`daily_7`) or Monthly (`monthly_12`) rotation available

### Log Levels

- `DEBUG`: Detailed execution information
- `INFO`: Normal operation status (default)
- `WARNING`: Non-critical issues
- `ERROR`: Serious problems that don't stop execution
- `CRITICAL`: Fatal errors that prevent operation

## Troubleshooting

### Common Issues

**"Configuration file not found"**
```bash
# Create example configuration
mkdir -p var
cp var/example_config.yaml var/config.yaml
# Edit var/config.yaml with your settings
```

**"SMTP config file not found"**
```bash
# Create SMTP configuration
mkdir -p ~/etc
cat > ~/etc/grsrv03.env << EOF
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
FROM_EMAIL=your-email@gmail.com
TO_EMAIL=admin@example.com
SMTP_TOKEN=your-app-password
EOF
```

**"Directory not accessible"**
- Check if backup drives are mounted
- Verify directory paths in configuration
- Check file permissions for backup directories

**"Pushover notifications not working"**
- Verify `~/etc/pushover.env` exists with valid credentials
- Check Pushover token and user key (both 30 characters)
- Test with Pushover website or mobile app first

### Debug Mode

Enable debug logging for troubleshooting:

```yaml
# In var/config.yaml
log_level: DEBUG
```

### Testing Configuration

Test your configuration without waiting for cron:

```bash
# Test configuration validation
python -c "from python_utils import parse_config_file; print('✅ Config valid')" 2>/dev/null || echo "❌ Config invalid"

# Test email configuration  
python -c "from python_utils import EmailNotifier; EmailNotifier()" 2>/dev/null || echo "❌ Email config invalid"

# Test pushover configuration
python -c "from python_utils import PushoverNotifier; p=PushoverNotifier(); print(f'Valid: {p._valid_credentials}')"
```

## Development

### Project Structure

```
proxmox_backup_checker/
├── README.md                 # This file
├── main.py                  # Main application (to be implemented)
├── requirements.txt         # Python dependencies
├── var/
│   ├── config.yaml         # Main configuration
│   └── example_config.yaml # Example configuration
├── log/                    # Log files (auto-created)
├── python_utils/           # Utility library
│   ├── size_utils.py      # Size parsing and formatting
│   ├── email_utils.py     # SMTP email notifications
│   ├── filesystem_utils.py # File and disk operations
│   ├── validation_utils.py # Configuration validation
│   ├── pushover_utils.py  # Push notifications
│   └── logging_utils.py   # Logging with rotation
└── .venv/                 # Virtual environment
```

### Dependencies

- `pydantic>=2.11.7` - Configuration validation
- `PyYAML>=6.0.2` - YAML configuration parsing
- `python-dotenv>=1.1.1` - Environment variable management
- `requests>=2.31.0` - HTTP requests for Pushover API

### Testing

The python_utils library includes comprehensive test coverage:

```bash
# Test individual components
python -c "from python_utils import parse_size_to_bytes; print(parse_size_to_bytes('10 GB'))"

# Test configuration loading
python -c "from python_utils import parse_config_file; config = parse_config_file('var/example_config.yaml'); print('✅ Config loaded')"

# Test complete workflow simulation
python -c "
from python_utils import *
logger = setup_backup_logging('test')
config = parse_config_file('var/example_config.yaml')
print(f'✅ {len(config.backup_check_list)} backups configured')
"
```

## License

This project is licensed under the terms specified in the LICENSE file.

## Support

For issues, questions, or contributions:

1. Check the troubleshooting section above
2. Review log files for detailed error information
3. Verify configuration file syntax and credentials
4. Test individual components as shown in the testing section

## Security Notes

- Store all credentials in `~/etc/` directory with appropriate permissions (`chmod 600`)
- Use application-specific passwords for email (not your main password)
- Regularly rotate API keys and passwords
- Monitor log files for unauthorized access attempts
- Consider using environment variables in production deployments