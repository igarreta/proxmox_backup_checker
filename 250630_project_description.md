# Proxmox Backup Checker
This project will check backup repositories and will check if the backups are reliable.
It will be written in Python 3.13 and will be run as a daily cron job.
As this will be run by cron and do not have interaction with the user, it will not be run inside a docker container.

## General instructions
Use general and project CLAUDE.md files for general instructions. 

## Backup location
Backup repositories may be mounted as read only. They may be external USB disk that could disconnect.

## Check process (backup_check_list)
These checks will be performed:
1. Check if the backup directories (backup_dir) from backup_check_list are mounted and accessible. If not, send an alert and do not check the unaccessible locations.
2. Check if the each of the backup directories (backup_dir) from backup_check_list have at least min_free_space_gb of free space. If not, send an alert.
3. For each backup in backup_check_list, check the total size of the files that have been modified in the last number of days as specified in backup_check_list. Calculate the total size by adding all files in the backup directory (not subdirectories) that have been modified within the specified number of days based on their last modified date. If the total size is less than the minimum size specified in backup_check_list, or if non have been modified, send an alert indicating the backup name and the total size.
4. File searches are limited to the backup directory itself - do not look into subdirectories. 

## cron job
The cron job will be run daily at 6:00 AM by the server main cron.

Example cron entry:
```bash
# Daily backup check at 6:00 AM
0 6 * * * cd /home/rsi/proxmox_backup_checker && uv run python main.py
```


## Configuration
The configuration file (`var/config.yaml`) will be a YAML file with the following structure.
It will be used for non secret settings. All secrets are stored in ~/etc/.
```yaml
from_email: sender@example.com # email to send notifications from (optional, default from ~/var/sendgrid.env)
to_email: # list of emails to send notifications to (optional, default from ~/var/sendgrid.env)
  - user@example.com
log_level: INFO # logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_file: log/proxmox_backup_checker.log # path to log file relative to project root (optional, default log/proxmox_backup_checker.log)
min_free_space: 100 GB# minimum free space in GB for the backup directory (optional, default 100 GB)
backup_check_list: # list of backups to check
  - name: proxmox # short name/identifier for the backup (required)
    backup_dir: /mnt/backup_usb1/vm-containers/dump # path to the backup directory (required)
    days: 8 # maximum age in days for the backup (required)
    min_size: 10 GB # minimum expected backup size in GB (optional, default 1 KB)
  - name: homeassistant # short name/identifier for the backup (required)
    backup_dir: /mnt/backup_usb1/homeassistant # path to the backup directory (required)
    days: 1 # maximum age in days for the backup (required)
    min_size: 30 GB # minimum expected backup size in GB (optional, default 1 KB)
  - name: proxmox-config
    backup_dir: /mnt/backup_usb1/proxmox-config/daily
    days: 1
    min_size: 10 KB

```

### Configuration file location
The configuration file will be located at `var/config.yaml` relative to project root.

### Configuration integrity
The configuration file will be validated against a schema. If the configuration is not valid, the program will exit with an critical error.

## Notification
Send email when process is completed with a summary of the results, including:
- Timestamp
- List of backups checked
- Total size for each backup checked
- List of errors
- Total time taken

## Error handling
If a backup directory is not mounted, include it in the summary and continue.
Do not retry in any case.

## Metrics
Do not save metrics.

## Alert Process
If errors are detected, alerts will be sent through multiple channels :
1. Email (using SendGrid): all alerts and notifications
2. Pushover notifications (low priority): only critical alerts, indicating unreachable backup directories or backups with less than min_size.

Each alert will include:
- Timestamp
- Alert level (INFO, WARNING, ERROR, CRITICAL)
- Affected backup  name
- Detailed error message
- Relevant metrics (backup size, age, etc.)

Send only one alert per session, including all the errors detected.

## Logging
Logging follows predefined logging instructions (CLAUDE.md)

## Documentation
Provide a README.md file with instructions on how to install and run the project. 
Include example configuration file.

