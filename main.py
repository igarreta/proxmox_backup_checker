#!/usr/bin/env python3
"""
Proxmox Backup Checker - Main Application Entry Point

A production-ready backup monitoring system that validates backup repositories,
checks file freshness, and sends comprehensive notifications via email and Pushover.

This script is designed to run as a daily cron job at 6:00 AM.
"""

import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any

# Add python_utils to path for imports
sys.path.append(str(Path(__file__).parent / "python_utils"))

from python_utils import (
    setup_backup_logging,
    parse_config_file,
    AppConfig,
    EmailNotifier,
    PushoverNotifier,
    send_critical_backup_alert
)

from src.backup_checker import BackupChecker
from src.notification_manager import NotificationManager


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    start_time = time.time()
    logger = None
    
    try:
        # Initialize logging first
        logger = setup_backup_logging(
            app_name="proxmox_backup_checker",
            log_dir="log",
            log_level="INFO",
            redirect_streams=True,
            rotation="weekly_4"
        )
        
        logger.info("=" * 80)
        logger.info("Proxmox Backup Checker Starting")
        logger.info("=" * 80)
        
        # Load and validate configuration
        config_path = Path("var/config.yaml")
        if not config_path.exists():
            logger.critical(f"Configuration file not found: {config_path}")
            logger.critical("Please create var/config.yaml from the example template")
            return 1
        
        logger.info(f"Loading configuration from {config_path}")
        try:
            config = parse_config_file(str(config_path))
            logger.info(f"Configuration loaded successfully:")
            logger.info(f"  - {len(config.backup_check_list)} backup(s) to check")
            logger.info(f"  - Email recipients: {len(config.to_email)}")
            logger.info(f"  - Pushover priority: {config.pushover_priority}")
            logger.info(f"  - Min free space: {config.min_free_space}")
            logger.info(f"  - Log level: {config.log_level}")
        
        except Exception as e:
            logger.critical(f"Configuration validation failed: {e}")
            logger.critical("Please check var/config.yaml for errors")
            return 1
        
        # Initialize components
        logger.info("Initializing backup checker and notification manager")
        
        backup_checker = BackupChecker(logger=logger)
        notification_manager = NotificationManager(
            config=config,
            logger=logger
        )
        
        # Perform backup checks
        logger.info("Starting backup validation process")
        check_results = backup_checker.run_all_checks(config.backup_check_list, config.min_free_space)
        
        # Calculate execution time
        duration = time.time() - start_time
        logger.info(f"Backup checks completed in {duration:.2f} seconds")
        
        # Process results and send notifications
        logger.info("Processing results and sending notifications")
        notification_success = notification_manager.send_notifications(check_results, duration)
        
        # Final status summary
        total_backups = len(config.backup_check_list)
        successful_backups = sum(1 for result in check_results if result.get('success', False))
        failed_backups = total_backups - successful_backups
        
        logger.info("=" * 80)
        logger.info("BACKUP CHECK SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total backups checked: {total_backups}")
        logger.info(f"Successful: {successful_backups}")
        logger.info(f"Failed: {failed_backups}")
        logger.info(f"Duration: {duration:.2f} seconds")
        logger.info(f"Notifications sent: {'✓' if notification_success else '✗'}")
        
        if failed_backups > 0:
            logger.warning(f"{failed_backups} backup(s) failed validation")
            for result in check_results:
                if not result.get('success', False):
                    logger.warning(f"  - {result['name']}: {result.get('error', 'Unknown error')}")
        else:
            logger.info("All backups passed validation ✓")
        
        logger.info("=" * 80)
        logger.info("Proxmox Backup Checker Completed")
        logger.info("=" * 80)
        
        # Return appropriate exit code
        return 1 if failed_backups > 0 else 0
        
    except KeyboardInterrupt:
        if logger:
            logger.warning("Application interrupted by user")
        else:
            print("Application interrupted by user", file=sys.stderr)
        return 1
        
    except Exception as e:
        error_msg = f"Critical application error: {e}"
        error_details = traceback.format_exc()
        
        if logger:
            logger.critical(error_msg)
            logger.critical(f"Error details:\n{error_details}")
        else:
            print(error_msg, file=sys.stderr)
            print(f"Error details:\n{error_details}", file=sys.stderr)
        
        # Send critical alert via Pushover if possible
        try:
            send_critical_backup_alert(
                f"Proxmox Backup Checker CRASHED: {error_msg}",
                logger=logger
            )
        except Exception:
            pass  # Don't let notification errors mask the original error
        
        return 1


if __name__ == "__main__":
    sys.exit(main())