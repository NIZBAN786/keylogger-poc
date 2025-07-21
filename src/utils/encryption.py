"""
Encryption Utilities Module
Educational Purpose Only - Use Responsibly

This module handles encryption and decryption of log data.
"""

import os
import base64
import logging
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.key_file = Path(config.get('ENCRYPTION', 'key_file', '.encryption_key'))
        self.fernet = None
        
        # Initialize encryption if enabled
        if config.getboolean('ENCRYPTION', 'enabled', True):
            self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption system."""
        try:
            # Load or generate encryption key
            if self.key_file.exists():
                self._load_key()
            else:
                self._generate_key()
            
            self.logger.info("Encryption system initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing encryption: {e}")
            raise
    
    def _generate_key(self):
        """Generate a new encryption key."""
        try:
            # Generate a random key
            key = Fernet.generate_key()
            
            # Save key to file
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set file permissions (read-only for owner)
            if os.name != 'nt':  # Unix-like systems
                self.key_file.chmod(0o600)
            
            # Initialize Fernet
            self.fernet = Fernet(key)
            
            self.logger.info(f"New encryption key generated and saved to {self.key_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating encryption key: {e}")
            raise
    
    def _load_key(self):
        """Load existing encryption key."""
        try:
            with open(self.key_file, 'rb') as f:
                key = f.read()
            
            # Initialize Fernet
            self.fernet = Fernet(key)
            
            self.logger.debug(f"Encryption key loaded from {self.key_file}")
            
        except Exception as e:
            self.logger.error(f"Error loading encryption key: {e}")
            raise
    
    def encrypt_data(self, data):
        """Encrypt string data."""
        try:
            if not self.fernet:
                raise ValueError("Encryption not initialized")
            
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.fernet.encrypt(data)
            return encrypted_data
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data back to string."""
        try:
            if not self.fernet:
                raise ValueError("Encryption not initialized")
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            raise
    
    def encrypt_file(self, file_path, output_path=None):
        """Encrypt a file."""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if output_path is None:
                output_path = file_path.with_suffix(file_path.suffix + '.enc')
            else:
                output_path = Path(output_path)
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt data
            encrypted_data = self.encrypt_data(file_data)
            
            # Write encrypted data
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            self.logger.info(f"File encrypted: {file_path} -> {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error encrypting file: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path, output_path=None):
        """Decrypt a file."""
        try:
            encrypted_file_path = Path(encrypted_file_path)
            
            if not encrypted_file_path.exists():
                raise FileNotFoundError(f"Encrypted file not found: {encrypted_file_path}")
            
            if output_path is None:
                # Remove .enc extension
                if encrypted_file_path.suffix == '.enc':
                    output_path = encrypted_file_path.with_suffix('')
                else:
                    output_path = encrypted_file_path.with_suffix('.decrypted')
            else:
                output_path = Path(output_path)
            
            # Read encrypted data
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            # Write decrypted data
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            self.logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error decrypting file: {e}")
            raise
    
    def encrypt_string_with_password(self, data, password):
        """Encrypt string data with a password."""
        try:
            # Generate salt
            salt = os.urandom(16)
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Encrypt data
            fernet = Fernet(key)
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = fernet.encrypt(data)
            
            # Combine salt and encrypted data
            result = salt + encrypted_data
            
            return base64.urlsafe_b64encode(result)
            
        except Exception as e:
            self.logger.error(f"Error encrypting with password: {e}")
            raise
    
    def decrypt_string_with_password(self, encrypted_data, password):
        """Decrypt string data with a password."""
        try:
            # Decode base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_data)
            
            # Extract salt and encrypted data
            salt = encrypted_data[:16]
            encrypted_data = encrypted_data[16:]
            
            # Derive key from password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Decrypt data
            fernet = Fernet(key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error decrypting with password: {e}")
            raise
    
    def is_encryption_enabled(self):
        """Check if encryption is enabled."""
        return self.config.getboolean('ENCRYPTION', 'enabled', True) and self.fernet is not None
    
    def get_key_info(self):
        """Get information about the encryption key."""
        try:
            if not self.key_file.exists():
                return {
                    'exists': False,
                    'path': str(self.key_file),
                    'size': 0,
                    'created': None
                }
            
            stat = self.key_file.stat()
            
            return {
                'exists': True,
                'path': str(self.key_file),
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime
            }
            
        except Exception as e:
            self.logger.error(f"Error getting key info: {e}")
            return {}
    
    def regenerate_key(self):
        """Regenerate encryption key (WARNING: This will make existing encrypted data unreadable)."""
        try:
            # Backup old key if it exists
            if self.key_file.exists():
                backup_file = self.key_file.with_suffix('.key.bak')
                self.key_file.rename(backup_file)
                self.logger.warning(f"Old key backed up to {backup_file}")
            
            # Generate new key
            self._generate_key()
            
            self.logger.warning("New encryption key generated. Old encrypted data is no longer accessible.")
            return True
            
        except Exception as e:
            self.logger.error(f"Error regenerating key: {e}")
            return False
    
    def test_encryption(self):
        """Test encryption/decryption functionality."""
        try:
            if not self.fernet:
                return False, "Encryption not initialized"
            
            # Test data
            test_data = "This is a test message for encryption validation."
            
            # Encrypt
            encrypted = self.encrypt_data(test_data)
            
            # Decrypt
            decrypted = self.decrypt_data(encrypted)
            
            # Verify
            if decrypted == test_data:
                return True, "Encryption test passed"
            else:
                return False, "Decrypted data doesn't match original"
                
        except Exception as e:
            return False, f"Encryption test failed: {e}"

