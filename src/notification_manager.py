"""
Notification Manager - Coordinates email and Pushover notifications

Handles all notification logic including email summaries and Pushover alerts
with appropriate priority levels and content formatting.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import sys

# Add python_utils to path for imports
sys.path.append(str(Path(__file__).parent.parent / "python_utils"))

from python_utils import (
    EmailNotifier,
    PushoverNotifier,
    AppConfig,
    bytes_to_human_readable
)


class NotificationManager:
    """
    Manages all notifications for backup check results.
    
    Coordinates email summaries and Pushover alerts based on check results
    and configuration settings.
    """
    
    def __init__(self, config: AppConfig, logger: Optional[logging.Logger] = None):
        """
        Initialize NotificationManager.
        
        Args:
            config: Application configuration
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize notifiers
        self.email_notifier = EmailNotifier(logger=self.logger)
        self.pushover_notifier = PushoverNotifier(
            title="Proxmox Backup Monitor",
            logger=self.logger
        )
    
    def send_notifications(self, check_results: List[Dict[str, Any]], duration: float) -> bool:
        """
        Send all appropriate notifications based on check results.
        
        Args:
            check_results: List of backup check results
            duration: Total execution time in seconds
            
        Returns:
            bool: True if all notifications sent successfully
        """
        self.logger.info("Preparing notifications")
        
        # Categorize results
        successful_backups = [r for r in check_results if r.get('success', False)]
        failed_backups = [r for r in check_results if not r.get('success', False)]
        
        # Extract critical failures (treat ALL backup failures as critical)
        critical_failures = []
        for result in failed_backups:
            critical_failures.append({
                'backup_name': result['name'],
                'error': result.get('error', 'Unknown error')
            })
        
        self.logger.info(f"Notification summary:")
        self.logger.info(f"  - Total backups: {len(check_results)}")
        self.logger.info(f"  - Successful: {len(successful_backups)}")
        self.logger.info(f"  - Failed: {len(failed_backups)}")
        self.logger.info(f"  - Critical failures: {len(critical_failures)}")
        
        notification_success = True
        
        # Send email summary (always)
        email_success = self._send_email_summary(check_results, duration)
        if email_success:
            self.logger.info("✓ Email summary sent successfully")
        else:
            self.logger.error("✗ Failed to send email summary")
            notification_success = False
        
        # Send Pushover alerts for critical failures only
        if critical_failures:
            pushover_success = self._send_pushover_alerts(critical_failures, check_results, duration)
            if pushover_success:
                self.logger.info("✓ Pushover critical alerts sent successfully")
            else:
                self.logger.error("✗ Failed to send Pushover alerts")
                notification_success = False
        else:
            # Send low-priority summary if all backups passed
            # if len(failed_backups) == 0:
            #     pushover_success = self._send_pushover_summary(check_results, duration)
            #     if pushover_success:
            #         self.logger.info("✓ Pushover summary sent successfully")
            #     else:
            #         self.logger.warning("Failed to send Pushover summary (non-critical)")
        
        return notification_success
    
    def _send_email_summary(self, check_results: List[Dict[str, Any]], duration: float) -> bool:
        """
        Send comprehensive email summary of all backup checks.
        
        Args:
            check_results: List of backup check results
            duration: Total execution time in seconds
            
        Returns:
            bool: True if email sent successfully
        """
        self.logger.debug("Generating email summary")
        
        try:
            # Generate email content
            subject, content = self._create_email_content(check_results, duration)
            
            # Send email
            success = self.email_notifier.send_email(
                to_emails=self.config.to_email,
                subject=subject,
                content=content
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending email summary: {e}")
            return False
    
    def _send_pushover_alerts(self, critical_failures: List[Dict[str, str]], 
                            check_results: List[Dict[str, Any]], duration: float) -> bool:
        """
        Send Pushover alerts for critical backup failures.
        
        Args:
            critical_failures: List of critical failure details
            check_results: Complete check results
            duration: Execution duration
            
        Returns:
            bool: True if alerts sent successfully
        """
        self.logger.debug(f"Sending Pushover alerts for {len(critical_failures)} critical failures")
        
        try:
            # Create alert message
            failed_count = len([r for r in check_results if not r.get('success', False)])
            total_count = len(check_results)
            
            if len(critical_failures) == 1:
                # Single critical failure
                failure = critical_failures[0]
                message = f"CRITICAL: Backup '{failure['backup_name']}' failed\n{failure['error']}"
                title = f"Backup Alert: {failure['backup_name']}"
            else:
                # Multiple critical failures
                failure_list = "\n".join([f"• {f['backup_name']}: {f['error']}" for f in critical_failures])
                message = f"CRITICAL: {len(critical_failures)} backup failures detected\n\n{failure_list}"
                title = f"Multiple Backup Failures ({len(critical_failures)})"
            
            # Add summary
            message += f"\n\nSummary: {failed_count}/{total_count} backups failed ({duration:.1f}s)"
            
            # Send with normal priority for critical issues
            success = self.pushover_notifier.send(
                message=message,
                title=title,
                priority=0  # Normal priority for critical failures
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending Pushover alerts: {e}")
            return False
    
    def _send_pushover_summary(self, check_results: List[Dict[str, Any]], duration: float) -> bool:
        """
        Send low-priority Pushover summary when all backups pass.
        
        Args:
            check_results: List of backup check results
            duration: Execution duration
            
        Returns:
            bool: True if summary sent successfully
        """
        self.logger.debug("Sending Pushover success summary")
        
        try:
            success = self.pushover_notifier.send_backup_summary(
                total_backups=len(check_results),
                successful_backups=len([r for r in check_results if r.get('success', False)]),
                failed_backups=len([r for r in check_results if not r.get('success', False)]),
                duration=duration,
                priority=self.config.pushover_priority  # Use configured priority (default: -1)
            )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending Pushover summary: {e}")
            return False
    
    def _create_email_content(self, check_results: List[Dict[str, Any]], duration: float) -> tuple[str, str]:
        """
        Create email subject and content for backup check results.
        
        Args:
            check_results: List of backup check results
            duration: Execution duration
            
        Returns:
            Tuple of (subject, content)
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Count results
        total_backups = len(check_results)
        successful_backups = len([r for r in check_results if r.get('success', False)])
        failed_backups = total_backups - successful_backups
        
        # Create subject
        if failed_backups > 0:
            subject = f"⚠️ Backup Check Alert - {failed_backups}/{total_backups} Failed"
        else:
            subject = f"✅ Backup Check Success - All {total_backups} Passed"
        
        # Create content
        content_lines = [
            "PROXMOX BACKUP CHECK REPORT",
            "=" * 50,
            f"Timestamp: {timestamp}",
            f"Duration: {duration:.2f} seconds",
            f"Total backups checked: {total_backups}",
            f"Successful: {successful_backups}",
            f"Failed: {failed_backups}",
            "",
            "BACKUP DETAILS",
            "=" * 50
        ]
        
        # Add details for each backup
        for i, result in enumerate(check_results, 1):
            status = "✅ PASSED" if result.get('success', False) else "❌ FAILED"
            backup_name = result.get('name', 'Unknown')
            backup_dir = result.get('backup_dir', 'Unknown')
            
            content_lines.append(f"{i}. {backup_name} - {status}")
            content_lines.append(f"   Directory: {backup_dir}")
            
            # Add backup info if available
            backup_info = result.get('info', {}).get('backup', {})
            if backup_info:
                file_count = backup_info.get('file_count', 0)
                total_size = backup_info.get('total_size_human', 'Unknown')
                content_lines.append(f"   Files: {file_count}, Size: {total_size}")
            
            # Add space info if available
            space_info = result.get('info', {}).get('space', {})
            if space_info:
                free_space = space_info.get('free_human', 'Unknown')
                usage_percent = space_info.get('usage_percent', 0)
                content_lines.append(f"   Free space: {free_space} ({100-usage_percent:.1f}% free)")
            
            # Add error details if failed
            if not result.get('success', False):
                error = result.get('error', 'Unknown error')
                content_lines.append(f"   ❌ Error: {error}")
            
            content_lines.append("")  # Empty line between backups
        
        # Add summary section
        if failed_backups > 0:
            content_lines.extend([
                "FAILED BACKUPS SUMMARY",
                "=" * 50
            ])
            
            for result in check_results:
                if not result.get('success', False):
                    backup_name = result.get('name', 'Unknown')
                    error = result.get('error', 'Unknown error')
                    content_lines.append(f"• {backup_name}: {error}")
            
            content_lines.append("")
        
        # Add footer
        content_lines.extend([
            "=" * 50,
            "Generated by Proxmox Backup Checker",
            f"Report time: {timestamp}"
        ])
        
        content = "\n".join(content_lines)
        
        return subject, content