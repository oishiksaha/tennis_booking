#!/usr/bin/env python3
"""Keep authentication alive by periodically visiting the booking page."""
import sys
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from src.config_loader import Config
from src.auth import AuthHandler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/auth_keepalive.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def keep_alive_visit(config: Config) -> bool:
    """Visit the booking page to keep session alive. Returns True if successful.
    
    If session expired but long-lived cookies exist, automatically triggers re-auth
    by clicking "Sign in" (which uses the long-lived cookies for automatic login).
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                auth_handler = AuthHandler(config)
                context = auth_handler.create_browser_context(browser, headless=True)
                page = context.new_page()
                
                # Navigate to booking page (this refreshes session cookies)
                page.goto(config.booking_url, wait_until='domcontentloaded', timeout=10000)
                
                # Handle cookie consent if present
                try:
                    cookie_button = page.query_selector(config.selectors['cookie_button'])
                    if cookie_button and cookie_button.is_visible(timeout=1000):
                        cookie_button.click()
                        page.wait_for_timeout(500)
                except Exception:
                    pass
                
                # Check if still authenticated
                is_auth_initial = auth_handler.is_authenticated(page)
                logger.info(f"Initial authentication check: {'✓ AUTHENTICATED' if is_auth_initial else '✗ NOT AUTHENTICATED (session expired)'}")
                
                is_auth = is_auth_initial
                auto_reauth_attempted = False
                auto_reauth_success = False
                
                if not is_auth:
                    # Session expired, but we may have long-lived cookies (DT, ln, luf)
                    # Try clicking "Sign in" to trigger automatic re-authentication
                    logger.info("=" * 60)
                    logger.info("SESSION EXPIRED - Attempting automatic re-authentication")
                    logger.info("Strategy: Click 'Sign in' to use long-lived cookies (DT, ln, luf)")
                    logger.info("=" * 60)
                    
                    auto_reauth_attempted = True
                    try:
                        # Look for "Sign in" button/text
                        sign_in_element = page.get_by_text("Sign in", exact=False).first
                        if sign_in_element.is_visible(timeout=5000):
                            logger.info("✓ Found 'Sign in' button - clicking to trigger auto re-auth...")
                            sign_in_element.click()
                            logger.info("  Waiting for automatic re-authentication to complete...")
                            page.wait_for_timeout(3000)  # Wait for auto-login to complete
                            
                            # Check if we're now authenticated
                            is_auth_after = auth_handler.is_authenticated(page)
                            if is_auth_after:
                                auto_reauth_success = True
                                is_auth = True
                                logger.info("=" * 60)
                                logger.info("✓✓✓ AUTOMATIC RE-AUTHENTICATION SUCCESSFUL! ✓✓✓")
                                logger.info("  Long-lived cookies (DT, ln, luf) worked!")
                                logger.info("  Session refreshed without password")
                                logger.info("=" * 60)
                            else:
                                logger.warning("=" * 60)
                                logger.warning("✗✗✗ AUTOMATIC RE-AUTHENTICATION FAILED ✗✗✗")
                                logger.warning("  Long-lived cookies may have expired")
                                logger.warning("  Manual re-authentication may be needed")
                                logger.warning("=" * 60)
                        else:
                            logger.warning("✗ Could not find 'Sign in' button for automatic re-auth")
                    except Exception as e:
                        logger.error(f"✗ Error during automatic re-authentication: {e}")
                        logger.error(f"  Exception type: {type(e).__name__}")
                
                if is_auth:
                    # Save updated browser state (cookies may have been refreshed)
                    auth_handler.save_browser_state(context)
                    if auto_reauth_success:
                        logger.info("✓ Browser state saved with refreshed session cookies")
                    else:
                        logger.debug("Keep-alive visit successful, browser state saved")
                else:
                    logger.warning("=" * 60)
                    logger.warning("✗ KEEP-ALIVE FAILED - Authentication lost")
                    logger.warning("  Manual re-authentication required")
                    logger.warning("=" * 60)
                
                # Log experiment outcome summary
                logger.info("")
                logger.info("--- Experiment Outcome Summary ---")
                logger.info(f"  Initial auth status: {'Authenticated' if is_auth_initial else 'Not authenticated (session expired)'}")
                if auto_reauth_attempted:
                    logger.info(f"  Auto re-auth attempted: Yes (clicked 'Sign in')")
                    logger.info(f"  Auto re-auth result: {'✓ SUCCESS (long-lived cookies worked!)' if auto_reauth_success else '✗ FAILED (long-lived cookies may be expired)'}")
                else:
                    logger.info(f"  Auto re-auth attempted: No (session was still valid)")
                logger.info(f"  Final auth status: {'✓ Authenticated' if is_auth else '✗ Not authenticated'}")
                logger.info("--- End Summary ---")
                logger.info("")
                
                browser.close()
                return is_auth
                    
            except Exception as e:
                browser.close()
                logger.error(f"Error during keep-alive visit: {e}")
                return False
                
    except Exception as e:
        logger.error(f"Critical error during keep-alive: {e}")
        return False

def main():
    """Main loop - visit booking page every 10 minutes to keep session alive."""
    config = Config()
    keepalive_interval = 600  # 10 minutes in seconds
    
    logger.info("=" * 60)
    logger.info("Authentication Keep-Alive Service")
    logger.info("=" * 60)
    logger.info(f"Visiting booking page every {keepalive_interval // 60} minutes")
    logger.info("This keeps the session active and prevents expiration")
    logger.info("Log file: /tmp/auth_keepalive.log")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    logger.info("")
    
    visit_count = 0
    start_time = datetime.now()
    
    try:
        while True:
            visit_count += 1
            timestamp = datetime.now()
            elapsed = timestamp - start_time
            elapsed_str = str(elapsed).split('.')[0]
            
            logger.info(f"[{timestamp.strftime('%H:%M:%S')}] Keep-alive visit #{visit_count} (elapsed: {elapsed_str})...")
            
            success = keep_alive_visit(config)
            
            if success:
                logger.info(f"✓ Keep-alive successful - session refreshed")
            else:
                logger.warning(f"✗ Keep-alive failed - authentication may be lost")
                logger.warning("Consider re-authenticating: python -m src.main --authenticate")
            
            # Wait before next visit
            next_visit_time = timestamp + timedelta(seconds=keepalive_interval)
            logger.info(f"   Next visit at {next_visit_time.strftime('%H:%M:%S')}...")
            logger.info("")
            time.sleep(keepalive_interval)
            
    except KeyboardInterrupt:
        logger.info("\n\nKeep-alive service stopped by user")
        logger.info(f"Total visits: {visit_count}")
        logger.info(f"Total runtime: {str(datetime.now() - start_time).split('.')[0]}")

if __name__ == '__main__':
    main()

