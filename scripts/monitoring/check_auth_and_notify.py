#!/usr/bin/env python3
"""Check authentication and send notification via email/SMS."""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from src.config_loader import Config
from src.auth import AuthHandler
from src.notifications import NotificationSender

def main():
    """Check authentication and send notification."""
    config = Config()
    auth_handler = AuthHandler(config)
    notification = NotificationSender()
    
    print("=" * 60)
    print("Authentication Check with Notification")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check authentication
    print("Checking authentication...")
    is_authenticated = False
    details = ""
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = auth_handler.create_browser_context(browser, headless=True)
                page = context.new_page()
                
                result = auth_handler.ensure_authenticated(page, context, headless=True)
                is_authenticated = result
                
                if is_authenticated:
                    details = "Authentication check passed. Profile button found and visible."
                    print("✅ Authentication: WORKING")
                else:
                    details = "Authentication check failed. Profile button not found or not visible."
                    print("❌ Authentication: FAILED")
                
                browser.close()
                
            except Exception as e:
                details = f"Error during authentication check: {str(e)}"
                print(f"❌ Error: {e}")
                browser.close()
                
    except Exception as e:
        details = f"Critical error: {str(e)}"
        print(f"❌ Critical error: {e}")
    
    # Send notification
    print()
    print("Sending notification...")
    notification_sent = notification.send_auth_status_notification(is_authenticated, details)
    
    if notification_sent:
        print("✅ Notification sent successfully")
    else:
        print("⚠️  Notification not sent (check configuration)")
        print("   Set environment variables:")
        print("   - NOTIFICATION_EMAIL_FROM")
        print("   - NOTIFICATION_EMAIL_PASSWORD")
        print("   - NOTIFICATION_EMAIL_TO")
        print("   - SMS_EMAIL (optional, for SMS)")
    
    print()
    print("=" * 60)
    
    return 0 if is_authenticated else 1

if __name__ == '__main__':
    sys.exit(main())

