"""
Helper Utilities Module
Educational Purpose Only - Use Responsibly

This module contains various helper functions and utilities.
"""

import os
import sys
import logging
import platform
import subprocess
from pathlib import Path
from datetime import datetime

def setup_logging(log_directory='logs', log_level=logging.INFO):
    """Setup logging configuration."""
    try:
        # Create log directory
        log_dir = Path(log_directory) / 'system'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file path
        log_file = log_dir / 'application.log'
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # Set specific logger levels
        logging.getLogger('pynput').setLevel(logging.WARNING)
        logging.getLogger('PIL').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized. Log file: {log_file}")
        
        return True
        
    except Exception as e:
        print(f"Error setting up logging: {e}")
        return False

def check_admin_privileges():
    """Check if the application is running with administrator privileges."""
    try:
        system = platform.system()
        
        if system == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        
        elif system in ["Linux", "Darwin"]:
            return os.geteuid() == 0
        
        else:
            return False
            
    except Exception:
        return False

def get_system_info():
    """Get system information."""
    try:
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'hostname': platform.node(),
            'username': os.getenv('USERNAME') or os.getenv('USER', 'Unknown'),
            'admin_privileges': check_admin_privileges(),
            'timestamp': datetime.now().isoformat()
        }
        
        return info
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting system info: {e}")
        return {}

def is_process_running(process_name):
    """Check if a process is running."""
    try:
        system = platform.system()
        
        if system == "Windows":
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    return True
        
        elif system in ["Linux", "Darwin"]:
            result = subprocess.run(['pgrep', '-f', process_name], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        
        return False
        
    except Exception:
        return False

def kill_process(process_name):
    """Kill a process by name."""
    try:
        system = platform.system()
        
        if system == "Windows":
            subprocess.run(['taskkill', '/f', '/im', process_name], 
                         capture_output=True)
        
        elif system in ["Linux", "Darwin"]:
            subprocess.run(['pkill', '-f', process_name], 
                         capture_output=True)
        
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error killing process {process_name}: {e}")
        return False

def get_installed_software():
    """Get list of installed software (Windows only)."""
    try:
        if platform.system() != "Windows":
            return []
        
        import winreg
        
        software_list = []
        
        # Check both 32-bit and 64-bit registry keys
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        
        for hkey, subkey in registry_keys:
            try:
                key = winreg.OpenKey(hkey, subkey)
                
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey_handle = winreg.OpenKey(key, subkey_name)
                        
                        try:
                            display_name = winreg.QueryValueEx(subkey_handle, "DisplayName")[0]
                            software_list.append(display_name)
                        except FileNotFoundError:
                            pass
                        
                        winreg.CloseKey(subkey_handle)
                        
                    except Exception:
                        continue
                
                winreg.CloseKey(key)
                
            except Exception:
                continue
        
        return sorted(list(set(software_list)))
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting installed software: {e}")
        return []

def get_network_info():
    """Get network information."""
    try:
        import socket
        import psutil
        
        info = {
            'hostname': socket.gethostname(),
            'ip_addresses': [],
            'network_interfaces': []
        }
        
        # Get IP addresses
        try:
            # Get local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            info['ip_addresses'].append(local_ip)
        except:
            pass
        
        # Get network interfaces
        try:
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {'name': interface, 'addresses': []}
                
                for addr in addresses:
                    if addr.family == socket.AF_INET:
                        interface_info['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address,
                            'netmask': addr.netmask
                        })
                    elif addr.family == socket.AF_INET6:
                        interface_info['addresses'].append({
                            'type': 'IPv6',
                            'address': addr.address
                        })
                
                if interface_info['addresses']:
                    info['network_interfaces'].append(interface_info)
        except:
            pass
        
        return info
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting network info: {e}")
        return {}

def format_file_size(size_bytes):
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

def format_duration(seconds):
    """Format duration in human-readable format."""
    try:
        if seconds < 60:
            return f"{seconds:.0f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"
    except:
        return "Unknown"

def create_directory_structure(base_path, structure):
    """Create directory structure from dictionary."""
    try:
        base_path = Path(base_path)
        
        for item, content in structure.items():
            item_path = base_path / item
            
            if isinstance(content, dict):
                # It's a directory
                item_path.mkdir(parents=True, exist_ok=True)
                create_directory_structure(item_path, content)
            else:
                # It's a file
                item_path.parent.mkdir(parents=True, exist_ok=True)
                if content is not None:
                    with open(item_path, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        return True
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating directory structure: {e}")
        return False

def sanitize_filename(filename):
    """Sanitize filename for safe file system usage."""
    try:
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        filename = filename.strip(' .')
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        # Ensure it's not empty
        if not filename:
            filename = 'unnamed'
        
        return filename
        
    except Exception:
        return 'unnamed'

def is_debugger_present():
    """Check if a debugger is attached (basic detection)."""
    try:
        import sys
        
        # Check for common debugger indicators
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            return True
        
        # Check for PyCharm debugger
        if 'pydevd' in sys.modules:
            return True
        
        # Check for other debuggers
        debugger_modules = ['pdb', 'ipdb', 'pudb', 'pydevd_pycharm']
        for module in debugger_modules:
            if module in sys.modules:
                return True
        
        return False
        
    except Exception:
        return False

def get_file_hash(file_path, algorithm='sha256'):
    """Get hash of a file."""
    try:
        import hashlib
        
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting file hash: {e}")
        return None

def cleanup_temp_files(temp_dir='temp'):
    """Clean up temporary files."""
    try:
        temp_path = Path(temp_dir)
        
        if not temp_path.exists():
            return 0
        
        count = 0
        for file_path in temp_path.rglob('*'):
            if file_path.is_file():
                try:
                    file_path.unlink()
                    count += 1
                except:
                    pass
        
        # Remove empty directories
        for dir_path in temp_path.rglob('*'):
            if dir_path.is_dir():
                try:
                    dir_path.rmdir()
                except:
                    pass
        
        return count
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error cleaning up temp files: {e}")
        return 0

