"""
Backup Checker - Core backup validation logic

Performs comprehensive backup validation including directory accessibility,
free space checking, and backup freshness validation.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sys

# Add python_utils to path for imports
sys.path.append(str(Path(__file__).parent.parent / "python_utils"))

from python_utils import (
    is_directory_accessible,
    get_disk_usage,
    get_files_modified_within_days,
    parse_size_to_bytes,
    bytes_to_human_readable,
    check_minimum_free_space,
    BackupCheckConfig
)


class BackupChecker:
    """
    Core backup validation engine.
    
    Performs comprehensive checks on backup repositories including:
    - Directory accessibility and mount status
    - Free space validation
    - Backup freshness and size validation
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize BackupChecker.
        
        Args:
            logger: Optional logger instance for detailed logging
        """
        self.logger = logger or logging.getLogger(__name__)
    
    def check_directory_accessibility(self, backup_dir: str) -> Tuple[bool, str]:
        """
        Check if backup directory is accessible and mounted.
        
        Args:
            backup_dir: Path to backup directory
            
        Returns:
            Tuple of (is_accessible, error_message)
        """
        self.logger.debug(f"Checking accessibility of {backup_dir}")
        
        try:
            if not is_directory_accessible(backup_dir):
                error_msg = f"Directory not accessible or not mounted: {backup_dir}"
                self.logger.warning(error_msg)
                return False, error_msg
            
            self.logger.debug(f"Directory accessible: {backup_dir}")
            return True, ""
            
        except Exception as e:
            error_msg = f"Error checking directory accessibility {backup_dir}: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def check_free_space(self, backup_dir: str, min_free_space: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if backup directory has sufficient free space.
        
        Args:
            backup_dir: Path to backup directory
            min_free_space: Minimum free space requirement (e.g., "100 GB")
            
        Returns:
            Tuple of (has_sufficient_space, error_message, space_info)
        """
        self.logger.debug(f"Checking free space for {backup_dir} (min: {min_free_space})")
        
        try:
            # Parse minimum space requirement
            min_bytes = parse_size_to_bytes(min_free_space)
            
            # Check free space using python_utils
            has_space, message = check_minimum_free_space(backup_dir, min_bytes)
            
            # Get detailed disk usage information
            total, used, free = get_disk_usage(backup_dir)
            
            space_info = {
                'total_bytes': total,
                'used_bytes': used,
                'free_bytes': free,
                'total_human': bytes_to_human_readable(total),
                'used_human': bytes_to_human_readable(used),
                'free_human': bytes_to_human_readable(free),
                'min_required_human': bytes_to_human_readable(min_bytes),
                'usage_percent': round((used / total) * 100, 1) if total > 0 else 0
            }
            
            if has_space:
                self.logger.debug(f"Sufficient free space: {space_info['free_human']} available")
                return True, "", space_info
            else:
                self.logger.warning(f"Insufficient free space: {message}")
                return False, message, space_info
                
        except Exception as e:
            error_msg = f"Error checking free space for {backup_dir}: {e}"
            self.logger.error(error_msg)
            return False, error_msg, {}
    
    def check_backup_freshness(self, backup_config: BackupCheckConfig) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if backup files are fresh and meet size requirements.
        
        Args:
            backup_config: Backup configuration with directory, days, and min_size
            
        Returns:
            Tuple of (is_valid, error_message, backup_info)
        """
        backup_dir = backup_config.backup_dir
        days = backup_config.days
        min_size = backup_config.min_size
        
        self.logger.debug(f"Checking backup freshness for {backup_dir} (max age: {days} days, min size: {min_size})")
        
        try:
            # Get files modified within specified days (only in backup directory, not subdirectories)
            # Function returns list of tuples: (filename, size_bytes, modification_timestamp)
            recent_files = get_files_modified_within_days(backup_dir, days, include_subdirs=False, logger=self.logger)
            
            if not recent_files:
                error_msg = f"No files found modified within {days} days in {backup_dir}"
                self.logger.warning(error_msg)
                backup_info = {
                    'file_count': 0,
                    'total_size_bytes': 0,
                    'total_size_human': "0 B",
                    'oldest_file': None,
                    'newest_file': None,
                    'min_required_human': backup_config.min_size
                }
                return False, error_msg, backup_info
            
            # Calculate total size of recent files
            total_size = 0
            file_details = []
            
            for file_path, file_size, modified_time in recent_files:
                total_size += file_size
                
                file_details.append({
                    'path': str(file_path),
                    'size_bytes': file_size,
                    'size_human': bytes_to_human_readable(file_size),
                    'modified_time': modified_time
                })
            
            # Sort files by modification time for reporting
            file_details.sort(key=lambda x: x['modified_time'], reverse=True)
            
            backup_info = {
                'file_count': len(file_details),
                'total_size_bytes': total_size,
                'total_size_human': bytes_to_human_readable(total_size),
                'files': file_details[:5],  # Keep only 5 most recent for reporting
                'oldest_file': file_details[-1] if file_details else None,
                'newest_file': file_details[0] if file_details else None,
                'min_required_human': backup_config.min_size
            }
            
            # Check if total size meets minimum requirement
            min_size_bytes = backup_config.get_min_size_bytes()
            
            if total_size < min_size_bytes:
                error_msg = (f"Backup size {bytes_to_human_readable(total_size)} is below "
                           f"minimum requirement {backup_config.min_size}")
                self.logger.warning(error_msg)
                return False, error_msg, backup_info
            
            self.logger.info(f"Backup validation passed: {len(file_details)} files, "
                           f"total size {bytes_to_human_readable(total_size)}")
            return True, "", backup_info
            
        except Exception as e:
            error_msg = f"Error checking backup freshness for {backup_dir}: {e}"
            self.logger.error(error_msg)
            return False, error_msg, {}
    
    def run_all_checks(self, backup_configs: List[BackupCheckConfig], min_free_space: str) -> List[Dict[str, Any]]:
        """
        Run all backup validation checks for the provided configurations.
        
        Args:
            backup_configs: List of backup configurations to validate
            min_free_space: Global minimum free space requirement
            
        Returns:
            List of dictionaries containing check results for each backup
        """
        self.logger.info(f"Starting validation of {len(backup_configs)} backup(s)")
        
        results = []
        
        for i, backup_config in enumerate(backup_configs, 1):
            backup_name = backup_config.name
            backup_dir = backup_config.backup_dir
            
            self.logger.info(f"[{i}/{len(backup_configs)}] Validating backup: {backup_name}")
            self.logger.info(f"  Directory: {backup_dir}")
            self.logger.info(f"  Max age: {backup_config.days} days")
            self.logger.info(f"  Min size: {backup_config.min_size}")
            
            result = {
                'name': backup_name,
                'backup_dir': backup_dir,
                'success': True,
                'errors': [],
                'warnings': [],
                'info': {}
            }
            
            # Step 1: Check directory accessibility
            accessible, access_error = self.check_directory_accessibility(backup_dir)
            if not accessible:
                result['success'] = False
                result['errors'].append(f"Directory not accessible: {access_error}")
                result['error'] = access_error
                self.logger.error(f"  ✗ Accessibility check failed: {access_error}")
                
                # Skip further checks for inaccessible directories
                results.append(result)
                continue
            else:
                self.logger.info("  ✓ Directory accessible")
            
            # Step 2: Check free space
            has_space, space_error, space_info = self.check_free_space(backup_dir, min_free_space)
            if not has_space:
                result['success'] = False
                result['errors'].append(f"Insufficient free space: {space_error}")
                self.logger.error(f"  ✗ Free space check failed: {space_error}")
            else:
                self.logger.info(f"  ✓ Sufficient free space: {space_info.get('free_human', 'Unknown')}")
            
            result['info']['space'] = space_info
            
            # Step 3: Check backup freshness and size
            is_fresh, freshness_error, backup_info = self.check_backup_freshness(backup_config)
            if not is_fresh:
                result['success'] = False
                result['errors'].append(f"Backup validation failed: {freshness_error}")
                self.logger.error(f"  ✗ Backup freshness check failed: {freshness_error}")
            else:
                file_count = backup_info.get('file_count', 0)
                total_size = backup_info.get('total_size_human', '0 B')
                self.logger.info(f"  ✓ Backup validation passed: {file_count} files, {total_size}")
            
            result['info']['backup'] = backup_info
            
            # Set overall error message if any checks failed
            if not result['success']:
                result['error'] = '; '.join(result['errors'])
            
            results.append(result)
            
            # Log summary for this backup
            status = "✓ PASSED" if result['success'] else "✗ FAILED"
            self.logger.info(f"  {status}")
        
        # Log overall summary
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        self.logger.info(f"Backup validation completed: {successful} passed, {failed} failed")
        
        return results