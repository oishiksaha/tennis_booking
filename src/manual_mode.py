"""Interactive manual mode for testing and manual booking."""
import logging
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright
from .config_loader import Config
from .auth import AuthHandler
from .booking_engine import BookingEngine
from .bookings_manager import BookingsManager

logger = logging.getLogger(__name__)


class ManualMode:
    """Interactive manual mode for testing and manual booking."""
    
    def __init__(self, config: Config):
        """Initialize manual mode."""
        self.config = config
        self.auth_handler = None
        self.booking_engine = None
        self.page = None
        self.context = None
        self.browser = None
        self._available_slots = []
        self._target_date = None
    
    def start(self):
        """Start manual mode with browser."""
        logger.info("Starting manual mode...")
        
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=False)
        
        try:
            # Set up authentication
            self.auth_handler = AuthHandler(self.config)
            self.context = self.auth_handler.create_browser_context(self.browser, headless=False)
            self.page = self.context.new_page()
            
            # Ensure authenticated
            if not self.auth_handler.ensure_authenticated(self.page, self.context, headless=False):
                logger.error("Authentication failed")
                print("\n⚠️  Authentication failed. The browser window is still open.")
                print("Please check if you need to log in manually, then try again.")
                print("You can also run: python src/main.py --authenticate")
                return
            
            # Save browser state
            self.auth_handler.save_browser_state(self.context)
            
            # Set up booking engine
            self.booking_engine = BookingEngine(self.config)
            
            # Set up bookings manager
            self.bookings_manager = BookingsManager(self.config)
            
            # Run interactive loop
            self._interactive_loop()
            
        except KeyboardInterrupt:
            logger.info("Manual mode stopped by user")
        except Exception as e:
            logger.error(f"Error in manual mode: {e}", exc_info=True)
        finally:
            if self.browser:
                self.browser.close()
    
    def _interactive_loop(self):
        """Main interactive loop."""
        while True:
            print("\n" + "="*80)
            print("MANUAL MODE - Tennis Booking Bot")
            print("="*80)
            print("1. Check available slots (7 days from today)")
            print("2. Book a specific slot")
            print("3. Check availability for specific date")
            print("4. View my bookings")
            print("5. Cancel a booking")
            print("6. View all open slots (all dates per court)")
            print("7. Test selectors (debug mode)")
            print("8. Exit")
            print("="*80)
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                self._check_availability()
            elif choice == "2":
                self._book_slot_manual()
            elif choice == "3":
                self._check_specific_date()
            elif choice == "4":
                self._view_bookings()
            elif choice == "5":
                self._cancel_booking()
            elif choice == "6":
                self._view_all_open_slots()
            elif choice == "7":
                self._test_selectors()
            elif choice == "8":
                print("Exiting manual mode...")
                break
            else:
                print("Invalid choice. Please enter 1-8.")
    
    def _check_availability(self):
        """Check and display available slots for 7 days from today (exactly 7 days ahead)."""
        booking_window = self.config.booking_window_days
        target_date = self.booking_engine.get_target_date()  # This is exactly 7 days from today
        date_display = target_date.strftime('%A, %B %d, %Y')
        
        print(f"\n{'='*80}")
        print(f"CHECKING AVAILABILITY - {date_display}")
        print(f"{'='*80}")
        print(f"This will check all courts for {booking_window} days from today ({date_display}).")
        print("="*80)
        
        try:
            # Navigate to program page
            self.page.goto(self.config.booking_url, wait_until='domcontentloaded', timeout=10000)
            self.page.wait_for_timeout(1000)
            
            # Handle cookie consent
            try:
                cookie_button = self.page.query_selector(self.config.selectors['cookie_button'])
                if cookie_button and cookie_button.is_visible(timeout=1000):
                    cookie_button.click()
                    self.page.wait_for_timeout(500)
            except Exception:
                pass
            
            # Get available courts
            courts = self.booking_engine.get_available_courts(self.page)
            if not courts:
                print("No courts found.")
                return
            
            print(f"\nFound {len(courts)} court(s):")
            for i, (court_name, court_link) in enumerate(courts.items(), 1):
                print(f"  {i}. {court_name}")
            
            # Check each court for the target date (7 days from today)
            all_slots = {}
            
            for court_name, court_link in courts.items():
                print(f"\n{'='*80}")
                print(f"Checking {court_name}...")
                print("="*80)
                
                try:
                    # Navigate to court page
                    self.page.goto(court_link, wait_until='domcontentloaded', timeout=10000)
                    self.page.wait_for_timeout(1000)
                    
                    print(f"  Checking {date_display}...", end=' ', flush=True)
                    
                    # Navigate to target date (7 days from today)
                    if not self.booking_engine.navigate_to_target_date_fast(self.page, target_date):
                        print("❌ (date not accessible)")
                        continue
                    
                    # Find all available slots for this date
                    date_slots = self.booking_engine.find_all_available_slots_for_date(self.page, target_date)
                    
                    if date_slots:
                        for slot in date_slots:
                            slot['court_link'] = court_link
                            slot['date'] = target_date.strftime('%Y-%m-%d')
                            slot['date_display'] = date_display
                        
                        all_slots[court_name] = {
                            'court_link': court_link,
                            'slots': date_slots
                        }
                        print(f"✓ {len(date_slots)} slot(s)")
                    else:
                        print("✓ 0 slots")
                            
                except Exception as e:
                    logger.warning(f"Error processing court {court_name}: {e}")
                    print(f"  Error: {e}")
                    continue
            
            # Display results
            print("\n" + "="*80)
            print(f"AVAILABLE SLOTS FOR {date_display}")
            print("="*80)
            
            if not all_slots:
                print("No available slots found.")
                return
            
            slot_number = 1
            slot_list = []
            
            for court_name, court_data in all_slots.items():
                print(f"\n{court_name}:")
                for slot in court_data['slots']:
                    print(f"  [{slot_number}] {slot['time']} - {slot['court_name']} ({slot['spots']})")
                    slot_list.append({
                        'court_name': court_name,
                        'court_link': court_data['court_link'],
                        **slot
                    })
                    slot_number += 1
            
            # Store slots for potential booking
            self._available_slots = slot_list
            
        except Exception as e:
            logger.error(f"Error checking availability: {e}", exc_info=True)
            print(f"Error: {e}")
    
    def _book_slot_manual(self):
        """Manually book a slot after checking availability."""
        if not hasattr(self, '_available_slots') or not self._available_slots:
            print("\nPlease check availability first (option 1).")
            return
        
        print("\nAvailable slots:")
        for i, slot in enumerate(self._available_slots, 1):
            print(f"  {i}. {slot['time']} at {slot['court_name']} ({slot['spots']})")
        
        try:
            choice = input("\nEnter slot number to book (or 'cancel'): ").strip()
            if choice.lower() == 'cancel':
                return
            
            slot_index = int(choice) - 1
            if slot_index < 0 or slot_index >= len(self._available_slots):
                print("Invalid slot number.")
                return
            
            selected_slot = self._available_slots[slot_index]
            
            print(f"\nBooking: {selected_slot['time']} at {selected_slot['court_name']}")
            confirm = input("Confirm booking? (yes/no): ").strip().lower()
            
            if confirm != 'yes':
                print("Booking cancelled.")
                return
            
            # Navigate to court page
            self.page.goto(selected_slot['court_link'], wait_until='networkidle')
            self.page.wait_for_timeout(2000)
            
            # Navigate to target date
            if not self.booking_engine.navigate_to_target_date(self.page, self._target_date):
                print("Failed to navigate to target date.")
                return
            
            # Book the slot
            slot_info = {
                'index': selected_slot['index'],
                'time': selected_slot['time'],
                'court_name': selected_slot['court_name']
            }
            
            if self.booking_engine.book_slot(self.page, slot_info):
                print(f"✓ Successfully booked: {selected_slot['time']} at {selected_slot['court_name']}")
            else:
                print("✗ Booking failed. Please try again.")
                
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            logger.error(f"Error booking slot: {e}", exc_info=True)
            print(f"Error: {e}")
    
    def _check_specific_date(self):
        """Check availability for a specific date."""
        try:
            days_input = input("\nEnter number of days ahead (default 7): ").strip()
            days_ahead = int(days_input) if days_input else 7
            
            target_date = datetime.today() + timedelta(days=days_ahead)
            print(f"\nChecking availability for {target_date.strftime('%A, %B %d, %Y')}...")
            
            # Navigate to program page
            self.page.goto(self.config.booking_url, wait_until='networkidle')
            self.page.wait_for_timeout(2000)
            
            # Get courts
            courts = self.booking_engine.get_available_courts(self.page)
            if not courts:
                print("No courts found.")
                return
            
            # Check each court for the specific date
            for court_name, court_link in courts.items():
                print(f"\n{court_name}:")
                self.page.goto(court_link, wait_until='networkidle')
                self.page.wait_for_timeout(2000)
                
                if self.booking_engine.navigate_to_target_date(self.page, target_date):
                    # Find slots
                    slots = self.booking_engine.find_available_slots(self.page, [])  # Empty list = all times
                    if slots:
                        for slot in slots:
                            print(f"  - {slot['time']} ({slot['spots_text']})")
                    else:
                        print("  No available slots")
                        
        except ValueError:
            print("Invalid input. Please enter a number.")
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"Error: {e}")
    
    def _view_bookings(self):
        """View current bookings."""
        print("\nViewing your bookings...")
        print("="*80)
        
        try:
            # Navigate to bookings page (only if not already there)
            current_url = self.page.url
            if '/profile/programregistrations' not in current_url.lower():
                print("Navigating to bookings page...")
                self.bookings_manager.view_bookings_page(self.page)
                self.page.wait_for_timeout(2000)
            else:
                print("Already on bookings page.")
            
            print(f"\nCurrent URL: {self.page.url}")
            print(f"Page title: {self.page.title()}")
            
            # Get bookings
            print("\nParsing bookings...")
            bookings = self.bookings_manager.get_my_bookings(self.page)
            
            if bookings:
                print(f"\n✓ Found {len(bookings)} booking(s):")
                print("="*80)
                for i, booking in enumerate(bookings, 1):
                    date = booking.get('date', 'Unknown date')
                    time = booking.get('time', 'Unknown time')
                    court = booking.get('court', 'Unknown court')
                    location = booking.get('location', '')
                    
                    print(f"\n  {i}. {date} at {time}")
                    print(f"     Court: {court}")
                    if location:
                        print(f"     Location: {location}")
            else:
                print("\n⚠️  No bookings found.")
                print(f"Current URL: {self.page.url}")
                print("The page may still be loading, or there are no bookings.")
                print("\nHTML has been saved to data/bookings_page.html for inspection.")
            
        except Exception as e:
            logger.error(f"Error viewing bookings: {e}", exc_info=True)
            print(f"Error: {e}")
    
    def _cancel_booking(self):
        """Cancel a booking."""
        print("\nCancel Booking")
        print("="*80)
        
        try:
            # First, get bookings
            bookings = self.bookings_manager.get_my_bookings(self.page)
            
            if not bookings:
                print("No bookings found. Please view bookings first (option 4).")
                return
            
            print("\nYour bookings:")
            for i, booking in enumerate(bookings, 1):
                reg_id = booking.get('reg_id', 'N/A')
                reg_status = "✓" if reg_id and reg_id != 'N/A' else "⚠️ (no reg_id)"
                print(f"  {i}. {booking.get('date')} at {booking.get('time')} - {booking.get('court')} {reg_status}")
            
            choice = input("\nEnter booking number to cancel (or 'cancel'): ").strip()
            if choice.lower() == 'cancel':
                return
            
            try:
                booking_index = int(choice) - 1
                if booking_index < 0 or booking_index >= len(bookings):
                    print("Invalid booking number.")
                    return
                
                selected_booking = bookings[booking_index]
                reg_id = selected_booking.get('reg_id')
                
                if not reg_id:
                    print(f"\n⚠️  Warning: This booking does not have a registration ID.")
                    print("   Cancellation may not work. The booking might need to be refreshed.")
                    print("   Try viewing bookings again (option 4) to refresh the data.")
                    proceed = input("   Continue anyway? (yes/no): ").strip().lower()
                    if proceed != 'yes':
                        return
                
                print(f"\nCancel booking: {selected_booking.get('date')} at {selected_booking.get('time')}?")
                confirm = input("Type 'yes' to confirm: ").strip().lower()
                
                if confirm == 'yes':
                    if self.bookings_manager.cancel_booking(self.page, selected_booking):
                        print("✓ Booking cancelled successfully")
                    else:
                        print("✗ Failed to cancel booking")
                else:
                    print("Cancellation cancelled.")
                    
            except ValueError:
                print("Invalid input.")
                
        except Exception as e:
            logger.error(f"Error canceling booking: {e}", exc_info=True)
            print(f"Error: {e}")
    
    def _view_all_open_slots(self):
        """View all open slots for all dates per court."""
        booking_window = self.config.booking_window_days
        print("\n" + "="*80)
        print("VIEW ALL OPEN SLOTS")
        print("="*80)
        print(f"This will check all courts for the next {booking_window} days from today.")
        print("Optimized to only check dates with available buttons.")
        print("="*80)
        
        try:
            # Navigate to program page (faster load)
            self.page.goto(self.config.booking_url, wait_until='domcontentloaded', timeout=10000)
            self.page.wait_for_timeout(1000)
            
            # Handle cookie consent
            try:
                cookie_button = self.page.query_selector(self.config.selectors['cookie_button'])
                if cookie_button and cookie_button.is_visible(timeout=1000):
                    cookie_button.click()
                    self.page.wait_for_timeout(500)
            except Exception:
                pass
            
            # Get all courts
            print("\nFetching courts...")
            courts = self.booking_engine.get_available_courts(self.page)
            if not courts:
                print("⚠️  No courts found")
                return
            
            print(f"Found {len(courts)} court(s)")
            print("="*80)
            
            all_availability = {}
            total_slots = 0
            
            # Check each court
            for court_idx, (court_name, court_link) in enumerate(courts.items(), 1):
                print(f"\n[{court_idx}/{len(courts)}] Checking {court_name}...")
                print("-" * 80)
                
                try:
                    # Navigate to court page (faster load)
                    self.page.goto(court_link, wait_until='domcontentloaded', timeout=10000)
                    self.page.wait_for_timeout(1000)
                    
                    # Get available dates for this court (smart check - only dates with visible buttons)
                    available_dates = self.booking_engine.get_available_dates(self.page, booking_window)
                    
                    if not available_dates:
                        print(f"  ⚠️  No available dates found for {court_name}")
                        continue
                    
                    print(f"  Found {len(available_dates)} available date(s) to check")
                    
                    court_availability = {}
                    
                    # Check each available date
                    for date_obj in available_dates:
                        date_str = date_obj.strftime('%Y-%m-%d')
                        date_display = date_obj.strftime('%b %d, %Y (%a)')
                        print(f"    Checking {date_display}...", end=' ', flush=True)
                        
                        try:
                            # Navigate to this date (optimized fast navigation)
                            if not self.booking_engine.navigate_to_target_date_fast(self.page, date_obj):
                                print("❌ (date not accessible)")
                                continue
                            
                            # Find all available slots for this date
                            available_slots = self.booking_engine.find_all_available_slots_for_date(
                                self.page, date_obj
                            )
                            
                            if available_slots:
                                court_availability[date_str] = {
                                    'date_display': date_display,
                                    'slots': available_slots
                                }
                                total_slots += len(available_slots)
                                print(f"✓ {len(available_slots)} slot(s)")
                            else:
                                print("✓ 0 slots")
                                
                        except Exception as e:
                            logger.debug(f"Error checking {court_name} for {date_str}: {e}")
                            print(f"❌ Error: {e}")
                            continue
                    
                    if court_availability:
                        all_availability[court_name] = court_availability
                        print(f"  Total: {sum(len(d['slots']) for d in court_availability.values())} slot(s) across {len(court_availability)} date(s)")
                    else:
                        print(f"  No available slots found for {court_name}")
                            
                except Exception as e:
                    logger.warning(f"Error processing court {court_name}: {e}")
                    print(f"  Error: {e}")
                    continue
            
            # Display results
            print("\n" + "="*80)
            print("AVAILABILITY SUMMARY")
            print("="*80)
            
            if not all_availability:
                print("\n⚠️  No available slots found for any court in the booking window.")
                return
            
            # Display by court
            for court_name, court_data in all_availability.items():
                print(f"\n{'='*80}")
                print(f"COURT: {court_name}")
                print(f"{'='*80}")
                
                # Sort dates
                for date_str in sorted(court_data.keys()):
                    date_info = court_data[date_str]
                    slots = date_info['slots']
                    
                    print(f"\n  📅 {date_info['date_display']}")
                    print(f"     Available slots: {len(slots)}")
                    
                    # Group slots by time for better readability
                    for slot in slots:
                        time_str = slot.get('time', 'Unknown')
                        spots_str = slot.get('spots_text', '')
                        print(f"     • {time_str:15s} - {spots_str}")
            
            # Summary
            print("\n" + "="*80)
            print("SUMMARY")
            print("="*80)
            print(f"Total available slots: {total_slots}")
            print(f"Courts with availability: {len(all_availability)}")
            print(f"Days checked: {booking_window}")
            print("="*80)
            
        except Exception as e:
            logger.error(f"Error viewing all open slots: {e}", exc_info=True)
            print(f"Error: {e}")
    
    def _test_selectors(self):
        """Test selectors for debugging."""
        print("\nSelector Testing Mode")
        print("="*80)
        print("This will help you verify that selectors are working correctly.")
        print("The browser will stay open so you can inspect elements.")
        
        try:
            # Navigate to program page
            self.page.goto(self.config.booking_url, wait_until='networkidle')
            self.page.wait_for_timeout(2000)
            
            print("\nTesting selectors...")
            print(f"Current URL: {self.page.url}")
            
            # Test cookie button
            cookie_btn = self.page.query_selector(self.config.selectors['cookie_button'])
            print(f"Cookie button found: {cookie_btn is not None}")
            
            # Test court links
            court_links = self.page.query_selector_all(self.config.selectors['court_link'])
            print(f"Court links found: {len(court_links)}")
            
            if court_links:
                print("Courts:")
                for i, link in enumerate(court_links[:5], 1):  # Show first 5
                    try:
                        text = link.inner_text().split('\n')[0]
                        print(f"  {i}. {text}")
                    except:
                        print(f"  {i}. (could not read text)")
            
            print("\nBrowser will stay open for inspection.")
            print("Press Enter when done...")
            input()
            
        except Exception as e:
            logger.error(f"Error testing selectors: {e}", exc_info=True)
            print(f"Error: {e}")


def run_manual_mode(config: Config):
    """Run manual mode."""
    manual = ManualMode(config)
    manual.start()

