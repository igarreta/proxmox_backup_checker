# Proxmox Backup Checker
This project will check backup repositories and will check if the backups are reliable.
It will be written in Python 3.13 and will be run as a daily cron job.
As this will be run by cron and do not have interaction with the user, it will not be run inside a docker container.

## General instructions
Use general and project CLAUDE.md files for general instructions. 

## Backup location
Backup repositories may be mounted as read only. They may be external USB disk that could disconnect, and mounted on this server by a samba share.

## Check process (backup_check_list)
These checks will be performed:
1. Check if the backup directories (backup_dir) from backup_check_list are mounted and accessible. If not, send an alert and stop.
2. Check if the backup directories (backup_dir) from backup_check_list have at least min_free_space_gb of free space. If not, send an alert.
3. For each backup in backup_check_list, check if files have been modified in the last number of days as specified in the configuration file. Calculate the total size by adding all files in the backup directory (not subdirectories) that have been modified within the specified number of days based on their last modified date. If the total size is less than the minimum size specified in the configuration file, send an alert.
4. Calculate the total size of all files in each backup directory for reporting purposes (files modified within the 'days' period only).
5. File searches are limited to the backup directory itself - do not look into subdirectories. 

## cron job
The cron job will be run daily at 6:00 AM by the server main cron.

Example cron entry:
```bash
# Daily backup check at 6:00 AM
0 6 * * * cd /home/rsi/proxmox_backup_checker && uv run python main.py
```


## Configuration
The configuration file (`var/config.yaml`) will be a YAML file with the following structure:
```yaml
from_email: sender@example.com # email to send notifications from
to_email: # list of emails to send notifications to 
  - user@example.com
log_level: INFO # logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_file: log/proxmox_backup_checker.log # path to log file relative to project root
min_free_space_gb: 200 # minimum free space in GB for the backup directory
backup_check_list: # list of backups to check
  - name: proxmox # short name/identifier for the backup (required)
    backup_dir: /mnt/backup_usb1/vm-containers/dump # path to the backup directory (required)
    days: 8 # maximum age in days for the backup (required)
    min_size: 10 GB # minimum expected backup size in GB (optional)
  - name: homeassistant # short name/identifier for the backup (required)
    backup_dir: /mnt/backup_usb1/homeassistant # path to the backup directory (required)
    days: 1 # maximum age in days for the backup (required)
    min_size: 30 GB # minimum expected backup size in GB (optional)
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
1. Email (using SendGrid): all alerts
2. Pushover notifications (low priority): only critical alerts

Each alert will include:
- Timestamp
- Alert level (INFO, WARNING, ERROR, CRITICAL)
- Affected backup  name
- Detailed error message
- Relevant metrics (backup size, age, etc.)

Send only one alert per session, with all the errors detected.

## Logging
Logging follows predefined logging instructions (CLAUDE.md)

## Documentation
Provide a README.md file with instructions on how to install and run the project. 
Include example configuration file.





