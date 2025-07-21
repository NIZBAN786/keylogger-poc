"""
Screenshot Capture Module
Educational Purpose Only - Use Responsibly

This module handles periodic screenshot capture functionality.
"""

import os
import time
import logging
import threading
from datetime import datetime
from pathlib import Path
from PIL import ImageGrab, Image

class ScreenshotCapture:
    """Handles periodic screenshot capture."""
    
    def __init__(self, config, log_manager):
        self.config = config
        self.log_manager = log_manager
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.capture_thread = None
        
        # Configuration
        self.interval = config.getint('SCREENSHOT', 'interval_seconds', 300)  # 5 minutes default
        self.quality = config.getint('SCREENSHOT', 'quality', 85)
        self.max_screenshots = config.getint('SCREENSHOT', 'max_screenshots', 100)
        self.screenshot_dir = Path(config.get('GENERAL', 'log_directory', 'logs')) / 'screenshots'
        
        # Create screenshot directory
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    def start_capture(self):
        """Start periodic screenshot capture."""
        if self.running:
            self.logger.warning("Screenshot capture is already running")
            return
        
        try:
            self.running = True
            self.logger.info(f"Starting screenshot capture (interval: {self.interval}s)")
            
            while self.running:
                try:
                    self._capture_screenshot()
                    time.sleep(self.interval)
                except Exception as e:
                    self.logger.error(f"Error in screenshot capture loop: {e}")
                    time.sleep(10)  # Wait before retrying
            
        except Exception as e:
            self.logger.error(f"Error starting screenshot capture: {e}")
        finally:
            self.running = False
    
    def stop_capture(self):
        """Stop screenshot capture."""
        if not self.running:
            return
        
        self.running = False
        self.logger.info("Screenshot capture stopped")
    
    def _capture_screenshot(self):
        """Capture a single screenshot."""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            # Capture screenshot
            screenshot = ImageGrab.grab()
            
            # Resize if needed to save space
            max_width = self.config.getint('SCREENSHOT', 'max_width', 1920)
            max_height = self.config.getint('SCREENSHOT', 'max_height', 1080)
            
            if screenshot.width > max_width or screenshot.height > max_height:
                screenshot.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save screenshot
            screenshot.save(filepath, 'PNG', optimize=True)
            
            # Log the screenshot
            metadata = {
                'size': f"{screenshot.width}x{screenshot.height}",
                'file_size': filepath.stat().st_size,
                'timestamp': timestamp
            }
            
            self.log_manager.log_screenshot(str(filepath), metadata)
            self.logger.debug(f"Screenshot saved: {filepath}")
            
            # Clean up old screenshots
            self._cleanup_old_screenshots()
            
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
    
    def _cleanup_old_screenshots(self):
        """Remove old screenshots to maintain max count."""
        try:
            # Get all screenshot files
            screenshot_files = list(self.screenshot_dir.glob('screenshot_*.png'))
            
            # Sort by modification time (oldest first)
            screenshot_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove excess files
            while len(screenshot_files) > self.max_screenshots:
                old_file = screenshot_files.pop(0)
                old_file.unlink()
                self.logger.debug(f"Removed old screenshot: {old_file}")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up screenshots: {e}")
    
    def capture_immediate(self):
        """Capture an immediate screenshot (for manual trigger)."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"manual_screenshot_{timestamp}.png"
            filepath = self.screenshot_dir / filename
            
            screenshot = ImageGrab.grab()
            screenshot.save(filepath, 'PNG', optimize=True)
            
            self.log_manager.log_screenshot(str(filepath), {'type': 'manual'})
            self.logger.info(f"Manual screenshot saved: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            self.logger.error(f"Error capturing manual screenshot: {e}")
            return None
    
    def get_recent_screenshots(self, count=5):
        """Get list of recent screenshots."""
        try:
            screenshot_files = list(self.screenshot_dir.glob('screenshot_*.png'))
            screenshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return screenshot_files[:count]
            
        except Exception as e:
            self.logger.error(f"Error getting recent screenshots: {e}")
            return []
    
    def get_screenshot_statistics(self):
        """Get statistics about screenshots."""
        try:
            screenshot_files = list(self.screenshot_dir.glob('screenshot_*.png'))
            
            if not screenshot_files:
                return {
                    'count': 0,
                    'total_size': 0,
                    'average_size': 0,
                    'oldest': None,
                    'newest': None
                }
            
            total_size = sum(f.stat().st_size for f in screenshot_files)
            oldest = min(screenshot_files, key=lambda x: x.stat().st_mtime)
            newest = max(screenshot_files, key=lambda x: x.stat().st_mtime)
            
            return {
                'count': len(screenshot_files),
                'total_size': total_size,
                'average_size': total_size // len(screenshot_files),
                'oldest': oldest.name,
                'newest': newest.name
            }
            
        except Exception as e:
            self.logger.error(f"Error getting screenshot statistics: {e}")
            return {}
    
    def delete_screenshot(self, filename):
        """Delete a specific screenshot."""
        try:
            filepath = self.screenshot_dir / filename
            if filepath.exists():
                filepath.unlink()
                self.logger.info(f"Screenshot deleted: {filename}")
                return True
            else:
                self.logger.warning(f"Screenshot not found: {filename}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting screenshot: {e}")
            return False
    
    def delete_all_screenshots(self):
        """Delete all screenshots."""
        try:
            screenshot_files = list(self.screenshot_dir.glob('screenshot_*.png'))
            
            for screenshot_file in screenshot_files:
                screenshot_file.unlink()
            
            self.logger.info(f"Deleted {len(screenshot_files)} screenshots")
            return len(screenshot_files)
            
        except Exception as e:
            self.logger.error(f"Error deleting all screenshots: {e}")
            return 0

