#!/usr/bin/env python3
"""Script to test authentication status locally or on VM."""
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from src.config_loader import Config
from src.auth import AuthHandler


def test_authentication():
    """Test authentication status."""
    config = Config()
    auth_handler = AuthHandler(config)
    
    print("=" * 60)
    print(f"Authentication Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"Browser state file: {auth_handler.browser_state_file}")
    print(f"File exists: {auth_handler.browser_state_file.exists()}")
    
    if auth_handler.browser_state_file.exists():
        size = os.path.getsize(auth_handler.browser_state_file)
        mtime = os.path.getmtime(auth_handler.browser_state_file)
        mtime_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f"File size: {size} bytes")
        print(f"Last modified: {mtime_str}")
    else:
        print("⚠️  Browser state file does not exist!")
        print("   Run 'python -m src.main --authenticate' to create it")
        return False
    
    print()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = auth_handler.create_browser_context(browser, headless=True)
            page = context.new_page()
            
            print("Navigating to booking page...")
            page.goto(config.booking_url, wait_until='networkidle', timeout=20000)
            
            # Wait for profile button to appear (it loads dynamically)
            print("Waiting for profile button to load...")
            try:
                # Wait for the button to exist first
                page.wait_for_selector('#btnProfile', timeout=10000, state='attached')
                print("✓ Profile button exists in DOM")
                
                # Then wait for it to be visible (may take additional time)
                page.wait_for_selector('#btnProfile', timeout=5000, state='visible')
                print("✓ Profile button is visible")
            except Exception as e:
                print(f"⚠️  Profile button wait: {e}")
                # Give it one more chance with a simple timeout
                page.wait_for_timeout(2000)
            
            print("Checking authentication...")
            is_auth = auth_handler.is_authenticated(page)
            
            # Also check page elements (matching is_authenticated() logic)
            profile_found = False
            profile_visible = False
            sign_in_found = False
            user_name_found = False
            
            # Check profile button (primary check in is_authenticated)
            # Re-query to get fresh state after waits
            try:
                profile_btn = page.query_selector('#btnProfile')
                if profile_btn:
                    profile_found = True
                    # Check visibility with fresh query
                    try:
                        # Use evaluate to check visibility more reliably
                        is_visible_js = profile_btn.evaluate("""
                            el => {
                                const style = window.getComputedStyle(el);
                                const rect = el.getBoundingClientRect();
                                return style.display !== 'none' && 
                                       style.visibility !== 'hidden' && 
                                       style.opacity !== '0' &&
                                       rect.width > 0 && 
                                       rect.height > 0;
                            }
                        """)
                        if is_visible_js:
                            profile_visible = True
                    except:
                        # Fallback to Playwright's is_visible
                        if profile_btn.is_visible(timeout=1000):
                            profile_visible = True
            except:
                pass
            
            # Check sign in button
            try:
                sign_in_btn = page.get_by_text("Sign in", exact=False).first
                if sign_in_btn.is_visible(timeout=1000):
                    sign_in_found = True
            except:
                pass
            
            # Check for user name (fallback in is_authenticated)
            try:
                user_name_elem = page.get_by_text("Oishik Saha", exact=False).first
                if user_name_elem.is_visible(timeout=1000):
                    user_name_found = True
            except:
                pass
            
            print()
            print("=" * 60)
            if is_auth:
                print("✅ AUTHENTICATION SUCCESSFUL")
                print("   User is authenticated and ready for booking")
            else:
                print("❌ AUTHENTICATION FAILED")
                print("   User is NOT authenticated")
                print("   Browser state may be expired")
            
            print()
            print("Page element check (matching is_authenticated() logic):")
            print(f"  Profile button (#btnProfile) exists: {'✓' if profile_found else '✗'}")
            print(f"  Profile button visible: {'✓' if profile_visible else '✗'}")
            print(f"  User name 'Oishik Saha' found: {'✓' if user_name_found else '✗'}")
            print(f"  Sign in button: {'✗ Found (not authenticated)' if sign_in_found else '✓ Not found (good)'}")
            
            # Explain why authentication succeeded/failed
            if is_auth:
                if profile_visible:
                    print("\n  → Authentication confirmed by profile button (#btnProfile)")
                elif user_name_found:
                    print("\n  → Authentication confirmed by user name text (fallback)")
                else:
                    print("\n  → Authentication confirmed by other method")
            print("=" * 60)
            
            return is_auth
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()


if __name__ == '__main__':
    success = test_authentication()
    sys.exit(0 if success else 1)

