# Proxmox Backup Checker
This project will check the repository of the backups of a Proxmox server and will check if the backups are reliable.
Will also make copies of some directories to a remote storage.
It will be written in Python 3.13 inside a docker container, and will be run as a daily cron job.

## Backup location
The Proxmox backup disk is mounted in /mnt/backup_usb1/ as read only. It is an external USB disk that may disconnect, and mounted on this server by a samba share.

## Check process (backup_check_list)
These checks will be performed:
1. Check if the directories listed in check_dir_list are mounted and accesible. If not, send an alert and stop.
2. Check if the backup disk has at least 200 GB of free space. If not, send an alert.
3. For each directory in the list, check if a new backup has been created in the last number of days as specified in the configuration file. If not, send an alert.


## Backup copy process (backup_copy_list)
1. Check if rclone is installed and configured.
2. For each directory in the list, copy all files less than the specified number of days old to the specified rclone directory using rclone. First check that the total size of the files to copy is less than the specified maximum size. If days == 0 or not defined, copy all files. Include files in subdirectories.
3. Keep the number of backups indicated in retention_days, retention_weeks and retention_months. No retention if not defined.


## Configuration
The configuration file (`config.yaml`) will be a YAML file with the following structure:
```yaml
email:
  - user@example.com
log_level: INFO
log_file: /var/log/proxmox_backup_checker.log
check_dir_list:
  - /mnt/backup_usb1/ 
  - /mnt/hassio
backup_check_list:
  - name: homeassistant
    backup_dir: /mnt/backup_usb1/homeassistant
    days: 7
    min_size_gb: 1.0
  - name: vms
    backup_dir: /mnt/backup_usb1/vms
    days: 7
    min_size_gb: 10.0
backup_copy_list:
  - name: homeassistant_copy
    source_dir: /mnt/hassio
    rclone_path: onedrive:/GR_SRV03/backup/homeassistant
    max_size_mb: 200
    days: 1
    retention_days: 7
    retention_weeks: 4
    retention_months: 12

```

### Configuration file location
The configuration file will be located at `var/config.yaml` relative to project root.

### Configuration integrity
The configuration file will be validated against a schema. If the configuration is not valid, the program will exit with an critical error.

### Configuration Options

- `email`: (array of strings) Email addresses to send alerts to (required)
- `log_level`: (string) Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: (string) Path to log file
- `check_dir_list`: (array) List of directories to check the backups
  - `name`: (string) Short name/identifier for the backup (required)
  - `backup_dir`: (string) Path to the backup directory (required)
  - `days`: (int) Maximum age in days for the backup (required)
  - `min_size_gb`: (float, optional) If specified, minimum expected backup size in GB 
  - `rclone_path`: (string, optional) If specified, backup will be copied to this rclone directory
- `backup_copy_list`: (array) List of  directories to backup
  - `name`: (string) Short name/identifier for the backup (required)
  - `source_dir`: (string) Path to the backup directory (required)
  - `rclone_path`: (string, optional) If specified, backup will be copied to this rclone directory
  - `max_size_mb`: (int, optional) Maximum size in MB for the backup (required)
  - `days`: (int, optional) Maximum age in days for the backup 
  - `retention_days`: (int, optional) Number of days to keep the backup 
  - `retention_weeks`: (int, optional) Number of weeks to keep the backup 
  - `retention_months`: (int, optional) Number of months to keep the backup 


## Notification
Send email when process is completed with a summary of the results.
Include total size of each backup directory and latest file date.

## Alert Process
If errors are detected, alerts will be sent through multiple channels :
1. Email (using SendGrid), all alerts
2. Pushover notifications (low priority), only critical alerts

Each alert will include:
- Timestamp
- Alert level (INFO, WARNING, ERROR, CRITICAL)
- Affected backup directory
- Detailed error message
- Relevant metrics (backup size, age, etc.)

## Logging
Logging follows predefined logging instructions

## Documentation
Provide a README.md file with instructions on how to install and run the project. 
Include example configuration file.





