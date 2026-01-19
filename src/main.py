"""Main entry point for the tennis booking bot."""
import argparse
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from playwright.sync_api import sync_playwright
from .config_loader import Config
from .auth import AuthHandler
from .booking_engine import BookingEngine
from .scheduler import BookingScheduler
from .manual_mode import run_manual_mode
from .notifications import NotificationSender

# Set up logging
def setup_logging(config: Config):
    """Set up logging configuration."""
    log_file = Path(config.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create rotating file handler (max 10MB per file, keep 5 backup files)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            file_handler,
            logging.StreamHandler(sys.stdout)
        ]
    )


def run_booking(config: Config, headless: bool = False) -> bool:
    """Run a single booking attempt."""
    logger = logging.getLogger(__name__)
    from datetime import datetime
    from pathlib import Path
    
    # Set up notification sender
    notification = NotificationSender()
    
    # Capture log output
    log_capture = []
    log_handler = None
    
    # Set up log capture if email is configured
    if notification.email_from and notification.email_password:
        class LogCaptureHandler(logging.Handler):
            def __init__(self, capture_list):
                super().__init__()
                self.capture_list = capture_list
            def emit(self, record):
                self.capture_list.append(self.format(record))
        
        log_handler = LogCaptureHandler(log_capture)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(log_handler)
    
    logger.info("=" * 80)
    logger.info(f"Starting booking process at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Test mode: {'ENABLED' if config.test_mode_enabled else 'DISABLED'}")
    if config.test_mode_enabled:
        logger.info(f"  Test target: {config.test_target_court} on {config.test_target_date.strftime('%Y-%m-%d')} at {config.test_target_time}")
    else:
        logger.info(f"  Target times: {config.booking_times}")
        logger.info(f"  Booking window: {config.booking_window_days} days ahead")
    logger.info("=" * 80)
    
    booking_result = None
    booking_success = False
    error_message = None
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=headless)
            
            try:
                # Set up authentication
                auth_handler = AuthHandler(config)
                context = auth_handler.create_browser_context(browser, headless)
                page = context.new_page()
                
                # Ensure authenticated
                if not auth_handler.ensure_authenticated(page, context, headless):
                    error_message = "Authentication failed - booking cannot proceed"
                    logger.error(f"❌ {error_message}")
                    logger.error("Please run 'python -m src.main --authenticate' to refresh authentication")
                    return False
                
                logger.info("✅ Authentication successful")
                
                # Save browser state after authentication
                auth_handler.save_browser_state(context)
                
                # Set up booking engine
                booking_engine = BookingEngine(config)
                
                # Attempt booking
                result = booking_engine.attempt_booking(
                    page,
                    config.booking_times,
                    config.court_preference
                )
                
                logger.info("=" * 80)
                if result:
                    booking_success = True
                    booking_result = result
                    logger.info(f"✅ BOOKING SUCCESSFUL")
                    logger.info(f"   Court: {result.get('court_name', 'Unknown')}")
                    logger.info(f"   Date: {result.get('date', 'Unknown')}")
                    logger.info(f"   Time: {result.get('time', 'Unknown')}")
                    logger.info(f"   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    logger.warning("⚠️  No booking was made")
                    logger.warning("   Possible reasons:")
                    logger.warning("   - No slots available at target times")
                    logger.warning("   - All slots were already booked")
                    logger.warning("   - Booking process encountered an error")
                    logger.info(f"   Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info("=" * 80)
                    
            except Exception as e:
                error_message = f"Error in booking process: {str(e)}"
                logger.error("=" * 80)
                logger.error(f"❌ {error_message}")
                logger.error(f"   Error occurred at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.error("=" * 80)
                import traceback
                logger.error(traceback.format_exc())
                log_capture.append(traceback.format_exc())
            finally:
                browser.close()
    except Exception as e:
        error_message = f"Critical error: {str(e)}"
        logger.error(f"❌ {error_message}")
        import traceback
        log_capture.append(traceback.format_exc())
    
    # Remove log capture handler
    if log_handler:
        logger.removeHandler(log_handler)
    
    # Send notification
    try:
        notification.send_booking_notification(
            success=booking_success,
            booking_details=booking_result,
            log_lines=log_capture if log_capture else None,
            error_message=error_message
        )
    except Exception as e:
        logger.warning(f"Failed to send notification: {e}")
    
    return booking_success


def run_scheduled(config: Config, headless: bool = False):
    """Run scheduler continuously."""
    logger = logging.getLogger(__name__)
    logger.info("Starting scheduled booking bot...")
    
    def booking_task():
        """Task to run for each scheduled booking."""
        return run_booking(config, headless)
    
    scheduler = BookingScheduler(config, booking_task)
    scheduler.print_schedule()
    
    try:
        scheduler.run_continuously()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


def authenticate_only(config: Config):
    """Run authentication only (for first-time setup)."""
    logger = logging.getLogger(__name__)
    logger.info("Running authentication setup...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        try:
            auth_handler = AuthHandler(config)
            context = auth_handler.create_browser_context(browser, headless=False)
            page = context.new_page()
            
            # Navigate to booking page
            page.goto(config.booking_url, wait_until='networkidle')
            
            # Handle cookie consent
            try:
                cookie_button = page.query_selector(config.selectors['cookie_button'])
                if cookie_button and cookie_button.is_visible():
                    cookie_button.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass
            
            # Authenticate
            if auth_handler.ensure_authenticated(page, context, headless=False):
                logger.info("Authentication successful! Browser state saved.")
                logger.info("You can now run the bot with --schedule or without arguments.")
            else:
                logger.error("Authentication failed. Please try again.")
                
        except Exception as e:
            logger.error(f"Error during authentication: {e}", exc_info=True)
        finally:
            browser.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Tennis Booking Bot')
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run scheduler continuously (for production)'
    )
    parser.add_argument(
        '--authenticate',
        action='store_true',
        help='Run authentication setup only'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (default: config/config.yaml)'
    )
    parser.add_argument(
        '--manual',
        action='store_true',
        help='Run in interactive manual mode (for testing and manual booking)'
    )
    parser.add_argument(
        '--test-now',
        action='store_true',
        help='Run a booking attempt immediately (for testing auto mode without waiting for scheduled time)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = Config(args.config)
    
    # Set up logging
    setup_logging(config)
    
    logger = logging.getLogger(__name__)
    logger.info("Tennis Booking Bot starting...")
    
    # Determine mode
    if args.authenticate:
        authenticate_only(config)
    elif args.manual:
        run_manual_mode(config)
    elif args.test_now:
        # Test mode: run booking immediately (same as auto mode but bypasses scheduler)
        logger.info("Running test mode - booking attempt will start immediately")
        success = run_booking(config, headless=args.headless)
        sys.exit(0 if success else 1)
    elif args.schedule:
        run_scheduled(config, headless=args.headless)
    else:
        # Single booking run (auto mode - one attempt)
        success = run_booking(config, headless=args.headless)
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

