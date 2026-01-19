"""Authentication handler for SSO using Playwright browser context persistence."""
import json
import logging
from pathlib import Path
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Optional
from .config_loader import Config

logger = logging.getLogger(__name__)


class AuthHandler:
    """Handles SSO authentication with persistent browser context."""
    
    def __init__(self, config: Config):
        """Initialize authentication handler."""
        self.config = config
        self.browser_state_path = config.get_browser_state_path()
        self.browser_state_file = config.get_browser_state_file()
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure browser state directory exists."""
        self.browser_state_path.mkdir(parents=True, exist_ok=True)
    
    def create_browser_context(self, browser: Browser, headless: bool = False) -> BrowserContext:
        """Create or load browser context with persistent state."""
        state_file = self.browser_state_file
        
        # Use a more reasonable viewport size so user can see everything
        viewport_size = {'width': 1280, 'height': 800}
        
        if state_file.exists():
            logger.info(f"Loading browser state from {state_file}")
            try:
                # Load existing browser context
                context = browser.new_context(
                    storage_state=str(state_file),
                    viewport=viewport_size
                )
                logger.info("Browser state loaded successfully")
                return context
            except Exception as e:
                logger.warning(f"Failed to load browser state: {e}. Creating new context.")
        
        # Create new context
        logger.info("Creating new browser context")
        context = browser.new_context(
            viewport=viewport_size
        )
        return context
    
    def save_browser_state(self, context: BrowserContext):
        """Save browser context state for future use."""
        try:
            state = context.storage_state()
            with open(self.browser_state_file, 'w') as f:
                json.dump(state, f, indent=2)
            logger.info(f"Browser state saved to {self.browser_state_file}")
        except Exception as e:
            logger.error(f"Failed to save browser state: {e}")
    
    def is_authenticated(self, page: Page) -> bool:
        """Check if user is authenticated by checking top-right corner.
        
        When signed in: Button with ID 'btnProfile' is present (contains user icon + name "Oishik Saha")
        When not signed in: "Sign in" button/text is present
        """
        try:
            # PRIMARY CHECK: Look for the profile button (most reliable, fast check)
            # Button ID: btnProfile - this is always present when authenticated
            try:
                profile_button = page.query_selector('#btnProfile')
                if profile_button and profile_button.is_visible(timeout=500):  # Reduced timeout
                    logger.debug("Authentication check: Found profile button (#btnProfile) - user IS authenticated")
                    return True
            except Exception:
                pass
            
            # Quick check for "Sign in" (not authenticated) - do this early
            try:
                sign_in_element = page.get_by_text("Sign in", exact=False).first
                if sign_in_element.is_visible(timeout=500):  # Reduced timeout
                    logger.debug("Authentication check: Found 'Sign in' - user is NOT authenticated")
                    return False
            except Exception:
                pass
            
            # Check URL as fast fallback
            current_url = page.url.lower()
            if 'login' in current_url or 'signin' in current_url:
                logger.debug("Authentication check: On login page - user is NOT authenticated")
                return False
            
            # FALLBACK: Check for user name text (only if profile button not found)
            try:
                user_name_element = page.get_by_text("Oishik Saha", exact=False).first
                if user_name_element.is_visible(timeout=500):  # Reduced timeout
                    logger.debug("Authentication check: Found 'Oishik Saha' text - user IS authenticated")
                    return True
            except Exception:
                pass
            
            # If we're on the program page but can't find profile button, 
            # assume not authenticated (safer to re-auth)
            logger.debug("Authentication check: Could not find profile button (#btnProfile) - assuming NOT authenticated")
            return False
                
        except Exception as e:
            logger.debug(f"Error checking authentication: {e}")
            return False
    
    def authenticate(self, page: Page, headless: bool = False) -> bool:
        """Perform authentication. Returns True if successful."""
        if not headless:
            logger.info("Waiting for you to sign in manually...")
            logger.info("Checking every 3 seconds for authentication...")
            
            # Wait for user to authenticate
            # Check every 3 seconds if authentication is complete
            max_wait_time = 300  # 5 minutes
            wait_interval = 3
            elapsed = 0
            check_count = 0
            
            while elapsed < max_wait_time:
                page.wait_for_timeout(wait_interval * 1000)
                elapsed += wait_interval
                check_count += 1
                
                # Refresh page occasionally to ensure we're checking current state
                if check_count % 5 == 0:  # Every 15 seconds
                    try:
                        page.reload(wait_until='networkidle')
                        page.wait_for_timeout(2000)
                    except:
                        pass
                
                if self.is_authenticated(page):
                    logger.info("✅ Authentication detected! You are now signed in.")
                    return True
                
                # Show progress every 15 seconds
                if check_count % 5 == 0:
                    remaining = max_wait_time - elapsed
                    logger.info(f"Still waiting... ({remaining} seconds remaining)")
            
            logger.error("❌ Authentication timeout after 5 minutes. Please try again.")
            return False
        else:
            logger.error("Cannot authenticate in headless mode. Please run with headless=False first.")
            return False
    
    def ensure_authenticated(self, page: Page, context: BrowserContext, headless: bool = False) -> bool:
        """Ensure user is authenticated. Authenticate if needed."""
        # If we have a saved browser state and we're in headless mode, trust it
        # (the browser state should contain valid authentication cookies)
        if headless and self.browser_state_file.exists():
            logger.info("Headless mode with saved browser state - assuming authentication is valid")
            logger.info("If authentication fails, run 'python src/main.py --authenticate' to refresh browser state")
        
        # Navigate to booking page - use 'domcontentloaded' for faster initial load
        page.goto(self.config.booking_url, wait_until='domcontentloaded', timeout=10000)
        
        # Handle cookie consent if present (quick check, don't wait long)
        try:
            cookie_button = page.query_selector(self.config.selectors['cookie_button'])
            if cookie_button and cookie_button.is_visible(timeout=1000):
                cookie_button.click()
                logger.debug("Cookie consent accepted")
                page.wait_for_timeout(500)  # Reduced wait after cookie click
        except Exception:
            pass  # Cookie button not needed or not found
        
        # Quick authentication check - try immediately, then once more after brief wait
        if self.is_authenticated(page):
            logger.info("Already authenticated")
            return True
        
        # Wait briefly for any dynamic content to load, then check again
        page.wait_for_timeout(1000)  # Reduced from 2000
        if self.is_authenticated(page):
            logger.info("Already authenticated")
            return True
        
        # If in headless mode and we have saved state, try one more time with a longer wait
        # (sometimes the page needs more time to load with saved cookies)
        if headless and self.browser_state_file.exists():
            logger.warning("Authentication check failed, but saved browser state exists")
            logger.info("Waiting a bit longer for page to fully load with saved cookies...")
            page.wait_for_timeout(3000)
            if self.is_authenticated(page):
                logger.info("Authentication confirmed after longer wait")
                return True
            else:
                logger.error("❌ Saved browser state appears to be expired or invalid")
                logger.error("Please run 'python src/main.py --authenticate' (non-headless) to refresh authentication")
                return False
        
        # Need to authenticate (non-headless mode only)
        logger.warning("="*60)
        logger.warning("NOT AUTHENTICATED - Manual sign-in required")
        logger.warning("="*60)
        logger.info("The browser window is open. Please:")
        logger.info("1. Look for 'Sign in' button in the top right")
        logger.info("2. Click it and log in with your credentials")
        logger.info("3. Wait for the page to load (you should see your name 'Oishik Saha' in top right)")
        logger.info("4. The bot will automatically detect when you're logged in")
        logger.info("="*60)
        
        if self.authenticate(page, headless):
            self.save_browser_state(context)
            logger.info("✅ Authentication successful! Browser state saved.")
            return True
        else:
            logger.error("❌ Authentication failed or timed out.")
            logger.error("Please try running: python src/main.py --authenticate")
            return False

