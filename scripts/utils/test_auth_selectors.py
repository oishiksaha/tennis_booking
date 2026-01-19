#!/usr/bin/env python3
"""Test script to find the exact selectors for authentication check."""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from src.config_loader import Config
from src.auth import AuthHandler

def main():
    config = Config()
    print("="*60)
    print("Authentication Selector Test")
    print("="*60)
    print("\nThis script will help identify the exact selectors for:")
    print("  - 'Sign in' button/text (when NOT authenticated)")
    print("  - 'Oishik Saha' text (when authenticated)")
    print("\nThe browser will open. Please check the page and then")
    print("press Enter to continue...")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        try:
            auth_handler = AuthHandler(config)
            context = auth_handler.create_browser_context(browser, headless=False)
            page = context.new_page()
            
            # Navigate to booking page
            print(f"\nNavigating to: {config.booking_url}")
            page.goto(config.booking_url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            print("\n" + "="*60)
            print("Testing selectors...")
            print("="*60)
            
            # Test for "Sign in"
            print("\n1. Looking for 'Sign in':")
            try:
                sign_in = page.get_by_text("Sign in", exact=False).first
                if sign_in.is_visible(timeout=1000):
                    print("   ✓ Found 'Sign in' using get_by_text")
                    # Try to get more info
                    try:
                        tag = sign_in.evaluate("el => el.tagName")
                        classes = sign_in.evaluate("el => el.className")
                        print(f"     Tag: {tag}, Classes: {classes}")
                    except:
                        pass
                else:
                    print("   ✗ 'Sign in' not visible")
            except Exception as e:
                print(f"   ✗ Error: {e}")
            
            # Test for "Oishik Saha"
            print("\n2. Looking for 'Oishik Saha':")
            try:
                user_name = page.get_by_text("Oishik Saha", exact=False).first
                if user_name.is_visible(timeout=1000):
                    print("   ✓ Found 'Oishik Saha' using get_by_text")
                    # Try to get more info
                    try:
                        tag = user_name.evaluate("el => el.tagName")
                        classes = user_name.evaluate("el => el.className")
                        parent_tag = user_name.evaluate("el => el.parentElement?.tagName")
                        print(f"     Tag: {tag}, Classes: {classes}, Parent: {parent_tag}")
                    except:
                        pass
                else:
                    print("   ✗ 'Oishik Saha' not visible")
            except Exception as e:
                print(f"   ✗ Error: {e}")
            
            # Try XPath
            print("\n3. Testing XPath selectors:")
            try:
                xpath_signin = page.query_selector('xpath=//*[contains(text(), "Sign in")]')
                if xpath_signin:
                    print("   ✓ Found 'Sign in' using XPath")
                else:
                    print("   ✗ 'Sign in' not found with XPath")
            except Exception as e:
                print(f"   ✗ XPath error: {e}")
            
            try:
                xpath_name = page.query_selector('xpath=//*[contains(text(), "Oishik Saha")]')
                if xpath_name:
                    print("   ✓ Found 'Oishik Saha' using XPath")
                else:
                    print("   ✗ 'Oishik Saha' not found with XPath")
            except Exception as e:
                print(f"   ✗ XPath error: {e}")
            
            print("\n" + "="*60)
            print("Current page URL:", page.url)
            print("\nPlease check the browser window:")
            print("  - Do you see 'Sign in' or 'Oishik Saha' in the top right?")
            print("  - What element contains it? (button, span, div, etc.)")
            print("\nPress Enter when done...")
            input()
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == '__main__':
    main()

