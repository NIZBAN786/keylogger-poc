# Detailed Setup Instructions

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (64-bit recommended)
- **Python**: Python 3.8 or higher
- **RAM**: Minimum 4GB RAM (8GB recommended)
- **Storage**: At least 100MB free space for installation, additional space for logs
- **Network**: Internet connection for Telegram integration (optional)
- **Permissions**: Administrator privileges recommended for full functionality

### Required Software
1. **Python 3.8+**: Download from [python.org](https://python.org)
   - During installation, check "Add Python to PATH"
   - Verify installation: `python --version`

2. **Git** (optional): For cloning the repository
   - Download from [git-scm.com](https://git-scm.com)

## Installation Methods

### Method 1: Automated Installation (Recommended)

1. **Download the project**:
   ```bash
   git clone https://github.com/yourusername/keylogger-poc.git
   cd keylogger-poc
   ```

2. **Run the installation script**:
   ```bash
   scripts\install.bat
   ```

3. **Follow the on-screen instructions**

### Method 2: Manual Installation

1. **Download and extract the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create directory structure**:
   ```bash
   mkdir logs
   mkdir logs\keystrokes
   mkdir logs\screenshots
   mkdir logs\system
   ```

4. **Test the installation**:
   ```bash
   python -c "import pynput, cryptography, requests, PIL; print('Success')"
   ```

## Configuration

### Basic Configuration

The application will create a default `config.ini` file on first run. You can modify these settings:

```ini
[GENERAL]
log_directory = logs
stealth_mode = true
startup_persistence = false
debug_mode = false

[KEYLOGGER]
log_rotation_size = 10MB
max_log_files = 10
timestamp_format = %Y-%m-%d %H:%M:%S.%f
capture_special_keys = true
buffer_size = 50
flush_interval = 10

[SCREENSHOT]
enabled = true
interval_seconds = 300
quality = 85
max_screenshots = 100
max_width = 1920
max_height = 1080

[TELEGRAM]
enabled = false
bot_token = 
chat_id = 
send_interval = 3600
max_file_size = 52428800
send_logs = true
send_screenshots = true

[ENCRYPTION]
enabled = true
key_file = .encryption_key
algorithm = fernet
```

### Telegram Integration Setup

1. **Create a Telegram Bot**:
   - Open Telegram and search for @BotFather
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Save the bot token

2. **Get your Chat ID**:
   - Search for @userinfobot in Telegram
   - Send any message to get your chat ID
   - Or send a message to your bot and visit:
     `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`

3. **Configure the bot**:
   ```bash
   python scripts\setup_telegram.py
   ```

4. **Test the connection**:
   The setup script will send a test message to verify the connection.

## Advanced Configuration

### Stealth Mode
When enabled, the application runs in the background without showing in the taskbar:
```ini
[GENERAL]
stealth_mode = true
```

### Startup Persistence
To start the keylogger automatically with Windows:
```ini
[GENERAL]
startup_persistence = true
```

**Warning**: This adds the application to Windows startup registry.

### Log Encryption
All logs are encrypted by default using Fernet encryption:
```ini
[ENCRYPTION]
enabled = true
key_file = .encryption_key
```

The encryption key is automatically generated and stored securely.

### Screenshot Configuration
Customize screenshot capture:
```ini
[SCREENSHOT]
enabled = true
interval_seconds = 300    # 5 minutes
quality = 85             # JPEG quality (1-100)
max_screenshots = 100    # Maximum screenshots to keep
max_width = 1920         # Resize large screenshots
max_height = 1080
```

## Security Considerations

### Antivirus Software
Some antivirus software may flag this application as malicious due to its keylogging capabilities. This is expected behavior. You may need to:

1. **Add exceptions** for the application directory
2. **Whitelist** the Python executable
3. **Temporarily disable** real-time protection during installation

### Windows Defender
Windows Defender may quarantine the application. To resolve:

1. Open Windows Security
2. Go to Virus & threat protection
3. Manage settings under "Virus & threat protection settings"
4. Add an exclusion for the application folder

### Firewall Configuration
If using Telegram integration, ensure Python can access the internet:

1. Open Windows Defender Firewall
2. Allow Python through the firewall
3. Or create specific rules for the application

## Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Permission denied errors
- Run Command Prompt as Administrator
- Check file permissions in the application directory
- Ensure antivirus isn't blocking file access

#### Telegram bot not working
- Verify bot token and chat ID
- Check internet connection
- Test with the setup script: `python scripts\setup_telegram.py`

#### Screenshots not capturing
- Check if PIL/Pillow is installed correctly
- Verify screenshot directory permissions
- Test manual screenshot: `python -c "from PIL import ImageGrab; ImageGrab.grab().save('test.png')"`

#### High CPU usage
- Increase flush_interval in configuration
- Reduce screenshot frequency
- Check for infinite loops in logs

### Debug Mode
Enable debug mode for detailed logging:
```ini
[GENERAL]
debug_mode = true
```

Or set environment variable:
```bash
set DEBUG=true
python main.py
```

### Log Analysis
Check system logs for errors:
- Application logs: `logs\system\application.log`
- Screenshot logs: `logs\system\screenshots.log`
- System events: `logs\system\system.log`

## Performance Optimization

### Resource Usage
- **CPU**: Typically <1% on modern systems
- **RAM**: ~10-50MB depending on configuration
- **Disk**: Varies based on log retention settings

### Optimization Tips
1. **Increase buffer size** to reduce disk writes
2. **Adjust screenshot interval** based on needs
3. **Enable log rotation** to manage disk space
4. **Use compression** for archived logs

## Uninstallation

### Automated Uninstallation
```bash
scripts\uninstall.bat
```

### Manual Uninstallation
1. **Stop the application**:
   - Create `KILL_SWITCH` file in application directory
   - Or press Ctrl+C if running in console

2. **Remove startup persistence**:
   ```bash
   reg delete "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run" /v "WindowsSecurityUpdate" /f
   ```

3. **Delete application files**:
   - Remove the entire application directory
   - Delete log files if desired

4. **Uninstall Python packages** (optional):
   ```bash
   pip uninstall pynput cryptography requests Pillow psutil pywin32
   ```

## Security Best Practices

### For Educational Use
1. **Always inform users** when deploying for testing
2. **Use only on systems you own** or have explicit permission
3. **Follow all applicable laws** and regulations
4. **Document your testing** activities
5. **Remove after testing** is complete

### Data Protection
1. **Encrypt all logs** (enabled by default)
2. **Secure the encryption key** file
3. **Use strong passwords** for Telegram bot
4. **Regularly rotate** encryption keys
5. **Implement secure deletion** of old logs

### Network Security
1. **Use HTTPS** for all communications (Telegram API uses HTTPS)
2. **Monitor network traffic** during testing
3. **Implement rate limiting** for Telegram messages
4. **Use VPN** if additional privacy is needed

## Legal Compliance

### Before Deployment
- [ ] Verify you own the target system OR have explicit written permission
- [ ] Check local, state, and federal laws regarding keyloggers
- [ ] Inform all users who may be affected
- [ ] Document the educational/testing purpose
- [ ] Establish clear testing boundaries and duration

### During Testing
- [ ] Monitor only necessary data for educational purposes
- [ ] Avoid capturing sensitive personal information
- [ ] Regularly review captured data and delete unnecessary information
- [ ] Maintain secure storage of any captured data

### After Testing
- [ ] Completely remove the keylogger from all systems
- [ ] Securely delete all captured data
- [ ] Document lessons learned
- [ ] Share educational insights (without sensitive data)

## Support and Resources

### Documentation
- `README.md` - Project overview and quick start
- `docs/USAGE.md` - Detailed usage instructions
- `docs/SECURITY.md` - Security considerations and best practices
- `docs/API.md` - API documentation for developers

### Getting Help
1. Check the troubleshooting section above
2. Review log files for error messages
3. Test individual components separately
4. Create an issue in the project repository (for educational purposes)

### Educational Resources
- Understanding keylogger detection methods
- Learning about system security hardening
- Exploring ethical hacking and penetration testing
- Studying malware analysis and reverse engineering

Remember: This tool is for educational purposes only. Always use responsibly and ethically!

