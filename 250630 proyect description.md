# Proxmox Backup Checker
This project will check backups repositories and will check if the backups are reliable.
Will also make copies of some directories to a remote storage.
It will be written in Python 3.13 and will be run as a daily cron job inside a docker container.

## General instructions
Use general and project CLAUDE.md files for general instructions. 

## Backup location
Backup repositories may be mounted as read only. They may be external USB disk that could disconnect, and mounted on this server by a samba share.

## Check process (backup_check_list)
These checks will be performed:
1. Check if the directories listed in check_dir_list are mounted and accessible. If not, send an alert and stop.
2. Check if the backup disk has at least 200 GB of free space. If not, send an alert.
3. For each directory in the list, check if a new backup has been created in the last number of days as specified in the configuration file. This backup must be at least the minimum size specified in the configuration file (adding all the files created in the specified number of days, including subdirectories). If not, send an alert.


## Backup copy process (backup_copy_list)
1. Check if rclone is installed and configured.
2. For each directory in the list, copy all files less than the specified number of days old to the specified rclone directory using rclone. If days == 0 or not defined, copy all files. Include files in subdirectories. First check that the total size of the files to copy is less than the specified maximum size. 
3. Keep the number of backups indicated in retention_days, retention_weeks and retention_months. No retention if not defined.
4. Make directories for daily, weekly and monthly backups. Within each, make a directory for each backup. The directory name will be the timestamp of the backup. This is intended to be run daily. A second backup on the same day will be copied to the same directory.

## cron job
Give a cron example for the job.

## Configuration
The configuration file (`config.yaml`) will be a YAML file with the following structure:
```yaml
email: # list of emails to send notifications to 
  - user@example.com
log_level: INFO # logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
log_file: log/proxmox_backup_checker.log # path to log file relative to project root
check_dir_list: # list of directories to check availability
  - /mnt/backup_usb1/ 
  - /mnt/hassio
backup_check_list: # list of backups to check
  - name: homeassistant # short name/identifier for the backup (required)
    backup_dir: /mnt/backup_usb1/homeassistant # path to the backup directory (required)
    days: 7 # maximum age in days for the backup (required)
    min_size_gb: 1.0 # minimum expected backup size in GB (optional)
  - name: vms
    backup_dir: /mnt/backup_usb1/vms
    days: 7
    min_size_gb: 10.0
backup_copy_list: # list of directories to copy to remote storage
  - name: homeassistant_copy # short name/identifier for the backup (required)
    source_dir: /mnt/hassio # path to the source directory (required)
    rclone_path: onedrive:/GR_SRV03/backup/homeassistant # path to the rclone directory (required)
    max_size_mb: 200 # maximum size in MB for the backup (optional)
    days: 1 # maximum age in days of the files to be copied (optional)
    retention_days: 7 # number of days to keep the backup (optional)
    retention_weeks: 4 # number of weeks to keep the backup (optional)
    retention_months: 12 # number of months to keep the backup (optional)

```

### Configuration file location
The configuration file will be located at `var/config.yaml` relative to project root.

### Configuration integrity
The configuration file will be validated against a schema. If the configuration is not valid, the program will exit with an critical error.

## Notification
Send email when process is completed with a summary of the results.
Include total size for each backup and copy name and latest file date.

## Error handling
If an directory is not mounted, include it in the summary and continue.


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

## Logging
Logging follows predefined logging instructions (CLAUDE.md)

## Documentation
Provide a README.md file with instructions on how to install and run the project. 
Include example configuration file.





