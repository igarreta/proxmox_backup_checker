# Proxmox Backup Checker
This project will check the repository of the backups of a Proxmox server and will check if the backups are reliable.
It will be written in Python 3.13 inside a docker container, and will be run as a cron job.

## Backup location
The backup disk is mounted in /mnt/backup_usb1/ as read only

## Check process
These checks will be performed:
1. Check if the backup disk is mounted and accesible. If not, send an alert and stop.
2. Check if the backup disk has at least 200 GB of free space. If not, send an alert.
3. For each directory in the list, check if a new backup has been created in the last number of days as specified in the configuration file. If not, send an alert.
4. If specified in the configuration file, copy the last backups of each directory to OneDrive to the specified folder using rclone

## Configuration

The configuration file (`config.json`) will be a JSON file with the following structure:

```json
{
  "email": "user@example.com",
  "log_level": "INFO",
  "log_file": "/var/log/proxmox_backup_checker.log",
  "backup_dir_list": [
    {
      "name": "homeassistant",
      "backup_dir": "/mnt/backup_usb1/homeassistant",
      "days": 7,
      "min_size_gb": 1.0,
      "onedrive_dir": "/mnt/onedrive/"
    }
  ]
}
```

### Configuration Options

- `email`: (string) Email address to send alerts to (required)
- `log_level`: (string) Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file`: (string) Path to log file
- `backup_dir_list`: (array) List of backup directories to monitor
  - `name`: (string) Short name/identifier for the backup (required)
  - `backup_dir`: (string) Path to the backup directory (required)
  - `days`: (int) Maximum age in days for the backup (required)
  - `min_size_gb`: (float) Minimum expected backup size in GB (Optional)
  - `onedrive_dir`: (string, optional) If specified, backup will be copied to this OneDrive directory


## Notification
Send email when process is completed with a summary of the results.
Include total size of each backup directory and latest file date.

## Alert Process

If errors are detected, alerts will be sent through multiple channels :
1. Email (using SendGrid).  
2. Pushover notifications (low priority)

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




