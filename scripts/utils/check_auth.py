#!/usr/bin/env python3
"""Quick script to check authentication status and re-authenticate if needed."""
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
    print("Checking authentication status...")
    print("="*60)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        try:
            auth_handler = AuthHandler(config)
            context = auth_handler.create_browser_context(browser, headless=False)
            page = context.new_page()
            
            # Navigate to booking page
            print(f"Navigating to: {config.booking_url}")
            page.goto(config.booking_url, wait_until='networkidle')
            page.wait_for_timeout(3000)
            
            # Check authentication
            if auth_handler.is_authenticated(page):
                print("✅ You are authenticated!")
                print(f"Current URL: {page.url}")
                
                # Try to find courts
                court_links = page.query_selector_all(config.selectors['court_link'])
                print(f"Found {len(court_links)} courts")
                
                if court_links:
                    print("\nCourts found:")
                    for i, link in enumerate(court_links[:5], 1):
                        try:
                            text = link.inner_text().split('\n')[0]
                            print(f"  {i}. {text}")
                        except:
                            pass
            else:
                print("❌ You are NOT authenticated")
                print(f"Current URL: {page.url}")
                print("\nThe browser window is open. Please log in manually.")
                print("Waiting for you to authenticate...")
                
                if auth_handler.authenticate(page, headless=False):
                    auth_handler.save_browser_state(context)
                    print("✅ Authentication successful! Browser state saved.")
                else:
                    print("❌ Authentication failed or timed out.")
            
            print("\nPress Enter to close the browser...")
            input()
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            browser.close()

if __name__ == '__main__':
    main()

