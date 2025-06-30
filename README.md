# Proxmox Backup Checker

A Python-based monitoring solution for Proxmox backup directories that ensures backups are reliable, recent, and properly sized. The tool runs in a Docker container and can be scheduled as a cron job.

## Features

- ✅ Monitors backup directories for recent backups
- ✅ Verifies minimum backup size requirements
- ✅ Checks disk space availability
- ✅ Sends alerts via Email and Pushover
- ✅ Optional OneDrive backup synchronization
- ✅ Detailed logging
- ✅ Docker container support

## Prerequisites

- Python 3.8+
- Docker (for containerized deployment)
- SendGrid API key (for email notifications)
- Pushover API token and user key (for push notifications, optional)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/proxmox_backup_checker.git
   cd proxmox_backup_checker
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example configuration:
   ```bash
   cp config.example.json config.json
   ```

## Configuration

Edit the `config.json` file with your settings. See [Project Description](250630%20proyect%20description.md) for detailed configuration options.

## Usage

### Run directly:
```bash
python3 main.py --config config.json
```

### Run with Docker:
```bash
docker build -t proxmox-backup-checker .
docker run -v $(pwd)/config.json:/app/config.json proxmox-backup-checker
```

### Run as a cron job:
```
0 3 * * * cd /path/to/proxmox_backup_checker && docker run --rm -v $(pwd)/config.json:/app/config.json proxmox-backup-checker
```

## Logging

Logs are written to both console and the specified log file. The default log file location is `/var/log/proxmox_backup_checker.log`.

## Alerting

The system sends alerts through:
- Email (using SendGrid)
- Pushover notifications (low priority)

## License

MIT

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Support

For support, please open an issue in the GitHub repository.
