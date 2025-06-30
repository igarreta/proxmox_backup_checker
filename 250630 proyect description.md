# Proxmox Backup Checker
This project will check the repository of the backups of a Proxmox server and will check if the backups are reliable.
It will be written in Python 3.13 inside a docker container, and will be run as a daily cron job.

## Backup location
The backup disk is mounted in /mnt/backup_usb1/ as read only. It is an external USB disk that may disconnect, and mounted on this server by a samba share.

## Check process
These checks will be performed:
1. Check if the backup disk is mounted and accesible. If not, send an alert and stop.
2. Check if the backup disk has at least 200 GB of free space. If not, send an alert.
3. For each directory in the list, check if a new backup has been created in the last number of days as specified in the configuration file. If not, send an alert.
4. If rclone_path is specified, copy the last backups of each directory to the specified rclone directory using rclone. Delete previous backups in the rclone directory. Check not to upload more than 200 MB per directory (send alert by email if exceeded). Check if rclone is installed and configured.

## Configuration
The configuration file (`config.json`) will be a JSON file with the following structure:
```json
{
  "email": ["user@example.com"],
  "log_level": "INFO",
  "log_file": "/var/log/proxmox_backup_checker.log",
  "backup_dir_list": [
    {
      "name": "homeassistant",
      "backup_dir": "/mnt/backup_usb1/homeassistant",
      "days": 7,
      "min_size_gb": 1.0,
      "rclone_path": "onedrive:/homeassistant"
    }
  ]
}
```

### Configuration file location
The configuration file will be located at `var/config.json` relative to project root.

### Configuration integrity
The configuration file will be validated against a schema. If the configuration is not valid, the program will exit with an critical error.

### Configuration Options

- `email`: (array of strings) Email addresses to send alerts to (required)
- `log_level`: (string) Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: (string) Path to log file
- `backup_dir_list`: (array) List of backup directories to monitor
  - `name`: (string) Short name/identifier for the backup (required)
  - `backup_dir`: (string) Path to the backup directory (required)
  - `days`: (int) Maximum age in days for the backup (required)
  - `min_size_gb`: (float, optional) If specified, minimum expected backup size in GB 
  - `rclone_path`: (string, optional) If specified, backup will be copied to this rclone directory


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





