# Keylogger POC with Screenshot Capture and Telegram Integration

## ⚠️ IMPORTANT LEGAL DISCLAIMER

**This project is strictly for educational purposes only.** Using keyloggers without explicit permission from all affected parties is illegal in most jurisdictions and unethical. Always:

- Only deploy on systems you own or have explicit permission to test
- Never use to collect sensitive information from others
- Inform all users of any system where this POC is deployed
- Comply with all applicable local, state, and federal laws

## Project Overview

This is a Proof of Concept (POC) keylogger application developed for educational purposes to demonstrate how keylogging technology works and to understand security vulnerabilities. The project includes advanced features such as encrypted data storage, screenshot capture, and Telegram bot integration for remote monitoring.

## Features

### Core Functionality
- **Keystroke Capture**: Captures all keyboard inputs including special keys (Shift, Ctrl, Alt, etc.)
- **Timestamp Logging**: Maintains keystroke sequence with precise timestamps
- **Application Context**: Identifies the application where keystrokes were entered
- **Stealth Operation**: Runs in background with minimal system footprint

### Advanced Features
- **Screenshot Capture**: Takes periodic screenshots of the system
- **Telegram Bot Integration**: Sends logs and screenshots to a Telegram bot
- **Encrypted Storage**: Encrypts log files to prevent unauthorized access
- **Log Management**: Supports log rotation based on size/time
- **Startup Persistence**: Implements startup persistence mechanisms
- **Kill Switch**: Emergency shutdown mechanism

### Security Features
- **Data Encryption**: Uses Fernet encryption for all stored data
- **Remote Transmission**: Secure transmission to Telegram bot
- **Password Protection**: Optional password protection for accessing logs
- **Stealth Mode**: Hides application from taskbar/process lists

## Directory Structure

```
keylogger-poc/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── config.ini                 # Configuration file (created on first run)
├── README.md                   # This file
├── LICENSE                     # License file
├── .gitignore                  # Git ignore file
├── docs/                       # Documentation
│   ├── SETUP.md               # Detailed setup instructions
│   ├── USAGE.md               # Usage guide
│   ├── SECURITY.md            # Security considerations
│   └── API.md                 # API documentation
├── src/                        # Source code
│   ├── __init__.py
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── keylogger.py       # Main keylogger class
│   │   ├── log_manager.py     # Log file management
│   │   └── persistence.py     # Startup persistence
│   ├── modules/                # Additional modules
│   │   ├── __init__.py
│   │   ├── screenshot.py      # Screenshot capture
│   │   └── telegram_bot.py    # Telegram bot integration
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── config.py          # Configuration management
│       ├── encryption.py      # Encryption utilities
│       └── helpers.py         # Helper functions
├── logs/                       # Log files (created at runtime)
│   ├── keystrokes/            # Keystroke logs
│   ├── screenshots/           # Screenshot files
│   └── system/                # System logs
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_keylogger.py
│   ├── test_encryption.py
│   └── test_telegram.py
├── scripts/                    # Utility scripts
│   ├── install.bat            # Windows installation script
│   ├── uninstall.bat          # Windows uninstallation script
│   └── setup_telegram.py     # Telegram bot setup
└── resources/                  # Resources and assets
    ├── icons/                 # Application icons
    └── templates/             # Configuration templates
```

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: Python 3.8 or higher
- **RAM**: Minimum 4GB RAM
- **Storage**: At least 100MB free space
- **Network**: Internet connection for Telegram integration

### Required Python Packages
- `pynput` - Keyboard and mouse monitoring
- `cryptography` - Data encryption
- `requests` - HTTP requests for Telegram API
- `Pillow` - Screenshot capture and image processing
- `configparser` - Configuration file management
- `psutil` - System and process utilities
- `pywin32` - Windows-specific functionality
- `schedule` - Task scheduling

## Installation and Setup

### Step 1: Clone or Download the Project
```bash
git clone https://github.com/yourusername/keylogger-poc.git
cd keylogger-poc
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Telegram Bot (Optional)
1. Create a new Telegram bot by messaging @BotFather
2. Get your bot token
3. Get your chat ID by messaging @userinfobot
4. Run the setup script:
```bash
python scripts/setup_telegram.py
```

### Step 4: Configure the Application
Edit the `config.ini` file or let the application create it on first run:
```ini
[GENERAL]
log_directory = logs
stealth_mode = true
startup_persistence = false

[KEYLOGGER]
log_rotation_size = 10MB
timestamp_format = %Y-%m-%d %H:%M:%S
capture_special_keys = true

[SCREENSHOT]
enabled = true
interval_seconds = 300
quality = 85
max_screenshots = 100

[TELEGRAM]
enabled = false
bot_token = YOUR_BOT_TOKEN
chat_id = YOUR_CHAT_ID
send_interval = 3600

[ENCRYPTION]
enabled = true
key_file = .encryption_key
```

### Step 5: Run the Application
```bash
python main.py
```

## Usage

### Basic Usage
1. Run the application using `python main.py`
2. The keylogger will start capturing keystrokes in the background
3. Logs are saved in the `logs/keystrokes/` directory
4. Screenshots are saved in the `logs/screenshots/` directory

### Telegram Integration
1. Configure your Telegram bot credentials in `config.ini`
2. Enable Telegram integration by setting `enabled = true`
3. The bot will send periodic updates with logs and screenshots

### Stealth Mode
- Enable stealth mode in the configuration to hide the application
- The application will run without showing in the taskbar
- Use the kill switch mechanism to stop the application

### Kill Switch
- Press `Ctrl+Shift+F12` to immediately stop the keylogger
- Or create a file named `KILL_SWITCH` in the application directory

## Configuration Options

### General Settings
- `log_directory`: Directory to store log files
- `stealth_mode`: Run in background without UI
- `startup_persistence`: Start with Windows

### Keylogger Settings
- `log_rotation_size`: Maximum size before rotating logs
- `timestamp_format`: Format for timestamps in logs
- `capture_special_keys`: Include special keys in logs

### Screenshot Settings
- `enabled`: Enable/disable screenshot capture
- `interval_seconds`: Time between screenshots
- `quality`: JPEG quality (1-100)
- `max_screenshots`: Maximum number of screenshots to keep

### Telegram Settings
- `enabled`: Enable/disable Telegram integration
- `bot_token`: Your Telegram bot token
- `chat_id`: Your Telegram chat ID
- `send_interval`: Interval between sending updates (seconds)

### Encryption Settings
- `enabled`: Enable/disable log encryption
- `key_file`: File to store encryption key

## Security Considerations

### Detection Methods
This keylogger can be detected by:
- Antivirus software
- Process monitoring tools
- Network traffic analysis
- File system monitoring
- Registry monitoring (for persistence)

### Protection Against Keyloggers
- Use reputable antivirus software
- Monitor running processes regularly
- Use virtual keyboards for sensitive input
- Enable two-factor authentication
- Keep system and software updated

### Ethical Usage
- Only use on systems you own or have explicit permission to test
- Never collect sensitive information without consent
- Always inform users when deploying for testing
- Follow all applicable laws and regulations

## Troubleshooting

### Common Issues
1. **Permission Denied**: Run as administrator on Windows
2. **Module Not Found**: Install required packages using pip
3. **Telegram Not Working**: Check bot token and chat ID
4. **Screenshots Not Saving**: Check disk space and permissions

### Debug Mode
Enable debug mode by setting `DEBUG=true` in the environment:
```bash
set DEBUG=true
python main.py
```

## Contributing

This is an educational project. If you wish to contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

The authors and contributors of this project are not responsible for any misuse of this software. This tool is provided for educational purposes only. Users are solely responsible for ensuring their use of this software complies with all applicable laws and regulations.

## Educational Resources

### Understanding Keyloggers
- How keyloggers work at the system level
- Different types of keyloggers (hardware vs software)
- Common attack vectors and deployment methods

### Security Implications
- Impact on personal privacy and security
- Corporate security considerations
- Legal implications of unauthorized keylogging

### Detection and Prevention
- Anti-keylogger software and techniques
- System hardening against keyloggers
- Best practices for secure computing

## Support

For educational purposes and questions about this POC:
- Create an issue in the GitHub repository
- Review the documentation in the `docs/` directory
- Check the troubleshooting section above

Remember: This software is for educational purposes only. Always use responsibly and ethically.

#   k e y l o g g e r - p o c  
 