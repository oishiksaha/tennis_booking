"""Availability checker to view available slots."""
import logging
import sys
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from .config_loader import Config
from .auth import AuthHandler
from .booking_engine import BookingEngine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


def check_availability(config: Config, days_ahead: int = 7):
    """Check availability for the next N days."""
    logger.info(f"Checking availability for next {days_ahead} days...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        try:
            # Set up authentication
            auth_handler = AuthHandler(config)
            context = auth_handler.create_browser_context(browser, headless=False)
            page = context.new_page()
            
            # Ensure authenticated
            if not auth_handler.ensure_authenticated(page, context, headless=False):
                logger.error("Authentication failed")
                return
            
            # Save browser state
            auth_handler.save_browser_state(context)
            
            # Set up booking engine
            booking_engine = BookingEngine(config)
            
            # Navigate to program page
            page.goto(config.booking_url, wait_until='networkidle')
            page.wait_for_timeout(2000)
            
            # Handle cookie consent
            try:
                cookie_button = page.query_selector(config.selectors['cookie_button'])
                if cookie_button and cookie_button.is_visible():
                    cookie_button.click()
                    page.wait_for_timeout(1000)
            except Exception:
                pass
            
            # Get available courts
            courts = booking_engine.get_available_courts(page)
            if not courts:
                logger.warning("No courts found")
                return
            
            print("\n" + "="*80)
            print("AVAILABILITY REPORT")
            print("="*80)
            print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Checking next {days_ahead} days\n")
            
            all_availability = {}
            
            # Check each court
            for court_name, court_link in courts.items():
                print(f"\nCourt: {court_name}")
                print("-" * 80)
                
                court_availability = {}
                
                # Check each day
                for day_offset in range(1, days_ahead + 1):
                    target_date = datetime.today() + timedelta(days=day_offset)
                    
                    try:
                        # Navigate to court page
                        page.goto(court_link, wait_until='networkidle')
                        page.wait_for_timeout(2000)
                        
                        # Navigate to target date
                        if not booking_engine.navigate_to_target_date(page, target_date):
                            continue
                        
                        # Find all available slots (not just target times)
                        # We'll check all slots and filter later
                        try:
                            page.wait_for_selector(
                                booking_engine.selectors['time_slot_card'],
                                timeout=booking_engine.timeout
                            )
                            page.wait_for_timeout(2000)
                            
                            time_slots = page.query_selector_all(booking_engine.selectors['time_slot_card'])
                            select_buttons = page.query_selector_all(booking_engine.selectors['select_button'])
                            
                            day_slots = []
                            
                            for index in range(len(time_slots)):
                                if index >= len(select_buttons):
                                    continue
                                
                                try:
                                    time_slot = time_slots[index]
                                    select_button = select_buttons[index]
                                    
                                    # Check availability
                                    spots_element = time_slot.query_selector(booking_engine.selectors['spots_tag'])
                                    if not spots_element:
                                        continue
                                    
                                    spots_text = spots_element.inner_text().strip()
                                    is_disabled = select_button.is_disabled()
                                    
                                    if "No Spots Left" in spots_text or is_disabled:
                                        continue
                                    
                                    # Get time
                                    time_element = time_slot.query_selector(booking_engine.selectors['instance_time'])
                                    if not time_element:
                                        continue
                                    
                                    time_text = time_element.inner_text().strip()
                                    
                                    # Get court name
                                    location_div = time_slot.query_selector(booking_engine.selectors['location_div'])
                                    slot_court_name = "Unknown"
                                    if location_div:
                                        p_tag = location_div.query_selector('p')
                                        if p_tag:
                                            slot_court_name = p_tag.inner_text().replace("location_on", "").strip()
                                    
                                    day_slots.append({
                                        'time': time_text,
                                        'court_name': slot_court_name,
                                        'spots': spots_text
                                    })
                                    
                                except Exception as e:
                                    logger.debug(f"Error processing slot {index}: {e}")
                                    continue
                            
                            if day_slots:
                                court_availability[target_date.strftime('%Y-%m-%d')] = day_slots
                                
                        except Exception as e:
                            logger.debug(f"Error checking date {target_date}: {e}")
                            continue
                            
                    except Exception as e:
                        logger.warning(f"Error processing court {court_name} for date {target_date}: {e}")
                        continue
                
                all_availability[court_name] = court_availability
                
                # Print availability for this court
                if court_availability:
                    for date_str, slots in sorted(court_availability.items()):
                        print(f"\n  {date_str}:")
                        for slot in slots:
                            print(f"    - {slot['time']} ({slot['spots']})")
                else:
                    print("  No available slots found")
            
            # Summary
            print("\n" + "="*80)
            print("SUMMARY")
            print("="*80)
            
            total_slots = sum(
                len(slots)
                for court_avail in all_availability.values()
                for slots in court_avail.values()
            )
            
            print(f"Total available slots found: {total_slots}")
            print(f"Courts checked: {len(courts)}")
            print(f"Days checked: {days_ahead}")
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}", exc_info=True)
        finally:
            browser.close()


def main():
    """Main entry point for availability checker."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Check tennis court availability')
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days ahead to check (default: 7)'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file (default: config/config.yaml)'
    )
    
    args = parser.parse_args()
    
    config = Config(args.config)
    check_availability(config, args.days)


if __name__ == '__main__':
    main()

