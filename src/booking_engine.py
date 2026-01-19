"""Core booking engine using Playwright."""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from .config_loader import Config

logger = logging.getLogger(__name__)


class BookingEngine:
    """Handles the core booking logic."""
    
    def __init__(self, config: Config):
        """Initialize booking engine."""
        self.config = config
        self.selectors = config.selectors
        self.booking_window_days = config.booking_window_days
        self.timeout = config.booking['timeout_seconds'] * 1000  # Convert to milliseconds
    
    def navigate_to_target_date(self, page: Page, target_date: datetime) -> bool:
        """Navigate to the target date in the booking interface."""
        try:
            logger.info(f"Navigating to target date: {target_date.strftime('%Y-%m-%d')}")
            
            # Wait for page to load
            page.wait_for_timeout(2000)
            
            # Check if page shows "no instances available" - fail fast if so
            try:
                no_instances_text = page.get_by_text("no instances available", exact=False).first
                if no_instances_text.is_visible(timeout=1000):
                    logger.warning(f"Page shows 'no instances available' - skipping date navigation")
                    return False
            except Exception:
                pass  # Text not found, continue
            
            target_xpath = self._build_date_xpath(target_date)
            logger.debug(f"Looking for target date button: {target_xpath}")
            
            # Use shorter timeout for initial attempt (5 seconds instead of 30)
            initial_timeout = 5000
            
            try:
                # Use locator - it handles multiple matches better and waits for visibility
                target_button = page.locator(target_xpath).first
                target_button.wait_for(state='visible', timeout=initial_timeout)
                
                # .click() automatically scrolls into view and waits for actionability
                target_button.click()
                page.wait_for_timeout(2000)  # Wait for page to update
                
                logger.info("Successfully navigated to target date")
                return True
                
            except PlaywrightTimeoutError:
                logger.warning(f"Target date button not visible after {initial_timeout/1000}s, trying alternative approach...")
                
                # Alternative: Try clicking next day first to expand calendar (short timeout)
                next_day = target_date + timedelta(days=1)
                next_day_xpath = self._build_date_xpath(next_day)
                
                try:
                    next_day_button = page.locator(next_day_xpath).first
                    next_day_button.wait_for(state='visible', timeout=3000)
                    next_day_button.click()
                    page.wait_for_timeout(1000)
                    logger.debug("Clicked next day button")
                except Exception:
                    logger.debug("Next day button not available")
                
                # Try right arrow to navigate (quick check)
                try:
                    right_arrow = page.query_selector(self.selectors['right_arrow'])
                    if right_arrow and right_arrow.is_visible():
                        right_arrow.click()
                        page.wait_for_timeout(1000)
                        logger.debug("Clicked right arrow")
                except Exception:
                    pass
                
                # Try target date again with shorter timeout (5 seconds max)
                try:
                    target_button = page.locator(target_xpath).first
                    target_button.wait_for(state='visible', timeout=5000)
                    target_button.click()
                    page.wait_for_timeout(2000)
                    logger.info("Successfully navigated to target date (alternative method)")
                    return True
                except PlaywrightTimeoutError:
                    logger.warning(f"Target date button still not visible after alternative attempts")
                    logger.warning(f"Date {target_date.strftime('%Y-%m-%d')} may not be available or page structure changed")
                    return False
                except Exception as e:
                    logger.warning(f"Error clicking target date button: {e}")
                    return False
            
        except Exception as e:
            logger.warning(f"Failed to navigate to target date: {e}")
            return False
    
    def _build_date_xpath(self, date: datetime) -> str:
        """Build XPath for date button.
        
        Excludes mobile buttons (single-date-select-mobile) to avoid clicking hidden elements.
        """
        year = str(date.year)
        month = str(date.month)
        day = str(date.day)
        # Exclude mobile buttons - only click desktop visible buttons
        return f'//button[@data-year="{year}" and @data-month="{month}" and @data-day="{day}" and not(contains(@class, "single-date-select-mobile"))]'
    
    def get_target_date(self) -> datetime:
        """Get the target date for booking (booking_window_days ahead, or test date if test mode enabled)."""
        # Check if test mode is enabled
        if self.config.test_mode_enabled and self.config.test_target_date:
            logger.info(f"Test mode enabled: Using test target date {self.config.test_target_date.strftime('%Y-%m-%d')}")
            return self.config.test_target_date
        # Normal mode: use booking_window_days
        return datetime.today() + timedelta(days=self.booking_window_days)
    
    def parse_time_slot(self, time_text: str) -> Optional[datetime]:
        """Parse time slot text to datetime. Returns None if parsing fails."""
        try:
            # Clean the time text - it may contain extra text like "Program Instance for current date\n"
            # Remove newlines and extra whitespace
            cleaned = time_text.replace('\n', ' ').strip()
            
            # Extract just the time range (e.g., "7:00 AM - 8:00 AM")
            # Look for pattern like "X:XX AM/PM - X:XX AM/PM"
            import re
            time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))'
            match = re.search(time_pattern, cleaned)
            
            if not match:
                logger.debug(f"Could not find time pattern in: '{time_text}'")
                return None
            
            # Get the start time (first match group)
            start_time_str = match.group(1).strip()
            
            # Parse time (e.g., "7:00 AM" or "1:30 PM")
            time_obj = datetime.strptime(start_time_str, "%I:%M %p")
            
            # Get target date
            target_date = self.get_target_date()
            
            # Combine date and time
            return target_date.replace(
                hour=time_obj.hour,
                minute=time_obj.minute,
                second=0,
                microsecond=0
            )
        except Exception as e:
            logger.debug(f"Failed to parse time slot '{time_text}': {e}")
            return None
    
    def time_matches_target(self, time_text: str, target_times: List[str]) -> bool:
        """Check if a time slot matches any of the target times."""
        parsed_time = self.parse_time_slot(time_text)
        if parsed_time is None:
            return False
        
        time_str = parsed_time.strftime("%H:%M")
        return time_str in target_times
    
    def get_available_courts(self, page: Page) -> Dict[str, str]:
        """Get all available courts and their links."""
        courts = {}
        try:
            court_elements = page.query_selector_all(self.selectors['court_link'])
            logger.info(f"Found {len(court_elements)} courts")
            
            # Get base URL for relative links
            base_url = self.config.urls['base']
            
            for element in court_elements:
                try:
                    court_name = element.inner_text().split('\n')[0].strip()
                    court_link = element.get_attribute('href')
                    if court_name and court_link:
                        # Convert relative URLs to absolute
                        if court_link.startswith('/'):
                            court_link = base_url + court_link
                        elif not court_link.startswith('http'):
                            court_link = base_url + '/' + court_link
                        
                        courts[court_name] = court_link
                        logger.debug(f"Found court: {court_name} -> {court_link}")
                except Exception as e:
                    logger.warning(f"Error extracting court info: {e}")
            
        except Exception as e:
            logger.error(f"Error getting available courts: {e}")
        
        return courts
    
    def find_available_slots(
        self,
        page: Page,
        target_times: List[str]
    ) -> List[Dict[str, any]]:
        """Find available time slots matching target times.
        
        Optimized: Collects all available slots first, then filters by target times.
        This is faster than checking time matches during iteration.
        """
        all_available_slots = []
        
        try:
            # Wait for time slots to load
            page.wait_for_selector(
                self.selectors['time_slot_card'],
                timeout=self.timeout
            )
            page.wait_for_timeout(2000)  # Additional wait for dynamic content
            
            time_slots = page.query_selector_all(self.selectors['time_slot_card'])
            logger.info(f"Found {len(time_slots)} time slots for this court")
            
            select_buttons = page.query_selector_all(self.selectors['select_button'])
            
            # First pass: Collect ALL available slots (regardless of time)
            # This is faster than filtering during iteration
            for index in range(len(time_slots)):
                try:
                    if index >= len(select_buttons):
                        continue
                    
                    time_slot = time_slots[index]
                    select_button = select_buttons[index]
                    
                    # Check availability
                    spots_element = time_slot.query_selector(self.selectors['spots_tag'])
                    if not spots_element:
                        continue
                    
                    spots_text = spots_element.inner_text().strip()
                    
                    # Check if button is disabled
                    is_disabled = select_button.is_disabled()
                    
                    # Check if slot is available
                    if "No Spots Left" in spots_text or is_disabled:
                        continue
                    
                    # Get time
                    time_element = time_slot.query_selector(self.selectors['instance_time'])
                    if not time_element:
                        continue
                    
                    time_text = time_element.inner_text().strip()
                    
                    # Get court name
                    location_div = time_slot.query_selector(self.selectors['location_div'])
                    court_name = "Unknown"
                    if location_div:
                        p_tag = location_div.query_selector('p')
                        if p_tag:
                            court_name = p_tag.inner_text().replace("location_on", "").strip()
                    
                    slot_info = {
                        'index': index,
                        'time': time_text,
                        'court_name': court_name,
                        'spots_text': spots_text,
                    }
                    
                    all_available_slots.append(slot_info)
                    
                except Exception as e:
                    logger.debug(f"Error processing time slot {index}: {e}")
                    continue
            
            # Second pass: Filter by target times (faster than checking during iteration)
            matching_slots = []
            
            # Log available times for debugging
            available_times = [s['time'] for s in all_available_slots]
            logger.info(f"Target times: {target_times}")
            logger.info(f"Available slot times: {available_times[:10]}")  # Show first 10
            
            for slot in all_available_slots:
                # Parse and log for debugging
                parsed = self.parse_time_slot(slot['time'])
                if parsed:
                    parsed_str = parsed.strftime("%H:%M")
                    logger.debug(f"Slot '{slot['time']}' -> '{parsed_str}' (targets: {target_times})")
                else:
                    logger.warning(f"Failed to parse time slot: '{slot['time']}'")
                
                if self.time_matches_target(slot['time'], target_times):
                    matching_slots.append(slot)
                    logger.info(f"✓ MATCH: {slot['time']} at {slot['court_name']}")
                else:
                    if parsed:
                        parsed_str = parsed.strftime("%H:%M")
                        logger.debug(f"✗ No match: '{slot['time']}' ({parsed_str}) not in {target_times}")
            
            logger.info(f"Court has {len(all_available_slots)} available slots, {len(matching_slots)} match target times")
            if len(all_available_slots) > 0 and len(matching_slots) == 0:
                logger.warning(f"⚠️  No matches! Available times were: {available_times[:10]}")
                logger.warning(f"   Looking for: {target_times}")
            return matching_slots
            
        except PlaywrightTimeoutError:
            logger.error("Timeout waiting for time slots")
        except Exception as e:
            logger.error(f"Error finding available slots: {e}")
        
        return []
    
    def find_all_available_slots_for_date(self, page: Page, target_date: datetime) -> List[Dict[str, any]]:
        """Find ALL available time slots for a given date (not filtered by target times).
        
        Returns a list of all available slots with their details.
        """
        all_available_slots = []
        
        try:
            # Navigate to target date
            if not self.navigate_to_target_date(page, target_date):
                logger.debug(f"Could not navigate to date {target_date.strftime('%Y-%m-%d')}")
                return []
            
            # Wait for time slots to load
            try:
                page.wait_for_selector(
                    self.selectors['time_slot_card'],
                    timeout=self.timeout
                )
                page.wait_for_timeout(2000)  # Additional wait for dynamic content
            except PlaywrightTimeoutError:
                logger.debug(f"No time slots found for date {target_date.strftime('%Y-%m-%d')}")
                return []
            
            time_slots = page.query_selector_all(self.selectors['time_slot_card'])
            logger.debug(f"Found {len(time_slots)} time slots for date {target_date.strftime('%Y-%m-%d')}")
            
            select_buttons = page.query_selector_all(self.selectors['select_button'])
            
            # Collect ALL available slots
            for index in range(len(time_slots)):
                try:
                    if index >= len(select_buttons):
                        continue
                    
                    time_slot = time_slots[index]
                    select_button = select_buttons[index]
                    
                    # Check availability
                    spots_element = time_slot.query_selector(self.selectors['spots_tag'])
                    if not spots_element:
                        continue
                    
                    spots_text = spots_element.inner_text().strip()
                    
                    # Check if button is disabled
                    is_disabled = select_button.is_disabled()
                    
                    # Check if slot is available
                    if "No Spots Left" in spots_text or is_disabled:
                        continue
                    
                    # Get time
                    time_element = time_slot.query_selector(self.selectors['instance_time'])
                    if not time_element:
                        continue
                    
                    time_text = time_element.inner_text().strip()
                    
                    # Get court name
                    location_div = time_slot.query_selector(self.selectors['location_div'])
                    court_name = "Unknown"
                    if location_div:
                        p_tag = location_div.query_selector('p')
                        if p_tag:
                            court_name = p_tag.inner_text().replace("location_on", "").strip()
                    
                    slot_info = {
                        'index': index,
                        'time': time_text,
                        'court_name': court_name,
                        'spots_text': spots_text,
                        'date': target_date.strftime('%Y-%m-%d'),
                        'date_display': target_date.strftime('%b %d, %Y')
                    }
                    
                    all_available_slots.append(slot_info)
                    
                except Exception as e:
                    logger.debug(f"Error processing time slot {index}: {e}")
                    continue
            
            logger.debug(f"Found {len(all_available_slots)} available slots for {target_date.strftime('%Y-%m-%d')}")
            return all_available_slots
            
        except Exception as e:
            logger.error(f"Error finding slots for date {target_date.strftime('%Y-%m-%d')}: {e}")
            return []
    
    def get_available_dates(self, page: Page, days_ahead: int) -> List[datetime]:
        """Get list of dates to check (days 1 through days_ahead from today).
        
        Returns dates from tomorrow (day 1) through day N (days_ahead).
        Optionally filters to only include dates with visible buttons for optimization.
        """
        today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Generate all dates from day 1 to day N (1 through days_ahead)
        all_dates = [today + timedelta(days=i) for i in range(1, days_ahead + 1)]
        
        try:
            # Wait for date buttons to load
            page.wait_for_timeout(500)
            
            # Get all date buttons that are visible (exclude mobile)
            date_buttons = page.query_selector_all(
                'button[data-year][data-month][data-day]:not(.single-date-select-mobile)'
            )
            
            logger.debug(f"Found {len(date_buttons)} date buttons on page")
            
            # Extract dates from visible buttons
            visible_dates = set()
            for button in date_buttons:
                try:
                    if not button.is_visible():
                        continue
                    
                    year = int(button.get_attribute('data-year'))
                    month = int(button.get_attribute('data-month'))
                    day = int(button.get_attribute('data-day'))
                    
                    date_obj = datetime(year, month, day)
                    visible_dates.add(date_obj)
                except Exception:
                    continue
            
            # Filter to only include dates that are both in our range AND have visible buttons
            # This is the "smart" part - we only check dates that are actually available
            available_dates = [d for d in all_dates if d in visible_dates]
            
            # If we found visible buttons, use them; otherwise check all dates anyway
            if available_dates:
                logger.info(f"Found {len(available_dates)} dates with visible buttons (out of {len(all_dates)} total)")
                return sorted(available_dates)
            else:
                # No visible buttons found, but return all dates anyway (they might become visible after navigation)
                logger.info(f"No visible date buttons found, will check all {len(all_dates)} dates")
                return all_dates
            
        except Exception as e:
            logger.warning(f"Error getting available dates: {e}, will check all dates")
            # Fallback: return all dates in booking window
            return all_dates
    
    def navigate_to_target_date_fast(self, page: Page, target_date: datetime) -> bool:
        """Fast version of navigate_to_target_date with reduced waits."""
        try:
            target_xpath = self._build_date_xpath(target_date)
            
            # Quick check if button exists and is visible
            try:
                target_button = page.locator(target_xpath).first
                if not target_button.is_visible(timeout=2000):
                    return False
                
                # Click immediately
                target_button.click()
                page.wait_for_timeout(1000)  # Reduced wait
                return True
            except Exception:
                return False
                
        except Exception as e:
            logger.debug(f"Fast date navigation failed: {e}")
            return False
    
    def book_slot(self, page: Page, slot_info: Dict) -> bool:
        """Book a specific time slot. Returns True if successful."""
        try:
            index = slot_info['index']
            time_text = slot_info['time']
            court_name = slot_info['court_name']
            
            logger.info(f"Attempting to book: {time_text} at {court_name}")
            
            # Re-query elements to avoid stale references (elements may have changed)
            page.wait_for_timeout(1000)  # Brief wait for page stability
            time_slots = page.query_selector_all(self.selectors['time_slot_card'])
            select_buttons = page.query_selector_all(self.selectors['select_button'])
            
            if index >= len(select_buttons) or index >= len(time_slots):
                logger.error(f"Select button index {index} out of range (found {len(select_buttons)} buttons)")
                return False
            
            # Verify this is still the right slot by checking the time
            time_slot = time_slots[index]
            time_element = time_slot.query_selector(self.selectors['instance_time'])
            if time_element:
                current_time_text = time_element.inner_text().strip()
                if current_time_text != time_text:
                    logger.warning(f"Time mismatch: expected {time_text}, found {current_time_text}")
                    # Try to find the correct index by matching time
                    for i, ts in enumerate(time_slots):
                        te = ts.query_selector(self.selectors['instance_time'])
                        if te and te.inner_text().strip() == time_text:
                            index = i
                            logger.info(f"Found correct slot at index {i}")
                            break
            
            select_button = select_buttons[index]
            
            # Click select button
            page.evaluate("(element) => element.click()", select_button)
            page.wait_for_timeout(2000)
            
            # Click register button
            register_button = page.wait_for_selector(
                self.selectors['register_button'],
                timeout=self.timeout
            )
            page.evaluate("(element) => element.click()", register_button)
            page.wait_for_timeout(2000)
            
            # Proceed to checkout
            proceed_button = page.wait_for_selector(
                self.selectors['proceed_to_checkout'],
                timeout=self.timeout
            )
            page.evaluate("(element) => element.click()", proceed_button)
            page.wait_for_timeout(2000)
            
            # Checkout
            checkout_button = page.wait_for_selector(
                self.selectors['checkout_button'],
                timeout=self.timeout
            )
            checkout_button.click()
            page.wait_for_timeout(2000)
            
            # Final checkout
            final_checkout = page.wait_for_selector(
                self.selectors['final_checkout'],
                timeout=self.timeout
            )
            final_checkout.click()
            page.wait_for_timeout(3000)  # Wait for confirmation
            
            logger.info(f"Successfully booked: {time_text} at {court_name}")
            return True
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout during booking process: {e}")
            return False
        except Exception as e:
            logger.error(f"Error booking slot: {e}")
            return False
    
    def attempt_booking(
        self,
        page: Page,
        target_times: List[str],
        court_preference: str = "any"
    ) -> Optional[Dict[str, str]]:
        """Attempt to book a court at one of the target times."""
        max_retries = self.config.booking['max_retries']
        retry_delay = self.config.booking['retry_delay_seconds'] * 1000
        
        # Check if test mode is enabled and override settings
        if self.config.test_mode_enabled:
            logger.info("Test mode enabled - overriding booking parameters")
            target_times = self.config.test_target_time
            court_preference = "specific"
            logger.info(f"Test mode: target_times={target_times}, target_court={self.config.test_target_court}")
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Booking attempt {attempt + 1}/{max_retries}")
                
                # Navigate to program page
                page.goto(self.config.booking_url, wait_until='networkidle', timeout=15000)
                page.wait_for_timeout(2000)
                
                # Handle cookie consent
                try:
                    cookie_button = page.query_selector(self.config.selectors['cookie_button'])
                    if cookie_button and cookie_button.is_visible():
                        cookie_button.click()
                        page.wait_for_timeout(1000)
                except Exception:
                    pass
                
                # Get available courts
                courts = self.get_available_courts(page)
                if not courts:
                    logger.warning("No courts found")
                    # Don't retry if no courts found - likely a page structure issue
                    return None
                
                # Filter courts to test court if test mode is enabled
                if self.config.test_mode_enabled and self.config.test_target_court:
                    test_court = self.config.test_target_court
                    if test_court in courts:
                        logger.info(f"Test mode: Filtering to only check {test_court}")
                        courts = {test_court: courts[test_court]}
                    else:
                        logger.warning(f"Test mode: Test court '{test_court}' not found in available courts")
                        logger.info(f"Available courts: {list(courts.keys())}")
                        return None
                
                # Track if we found any available slots across all courts
                found_any_slots = False
                booking_error = False
                
                # Try each court
                for court_name, court_link in courts.items():
                    try:
                        logger.info(f"Checking court: {court_name}")
                        
                        # Navigate to court page with timeout
                        page.goto(court_link, wait_until='networkidle', timeout=15000)
                        page.wait_for_timeout(2000)
                        
                        # Check if page shows "no instances available" - skip this court quickly
                        try:
                            no_instances = page.get_by_text("no instances available", exact=False).first
                            if no_instances.is_visible(timeout=1000):
                                logger.info(f"Court {court_name} shows 'no instances available' - skipping")
                                continue
                        except Exception:
                            pass
                        
                        # Navigate to target date
                        target_date = self.get_target_date()
                        if not self.navigate_to_target_date(page, target_date):
                            logger.warning(f"Could not navigate to target date for {court_name} - skipping")
                            continue
                        
                        # Find available slots
                        available_slots = self.find_available_slots(page, target_times)
                        
                        if not available_slots:
                            logger.info(f"No available slots at target times for {court_name}")
                            continue
                        
                        found_any_slots = True
                        
                        # Book the first available slot
                        slot = available_slots[0]
                        logger.info(f"Attempting to book: {slot['time']} at {slot['court_name']}")
                        if self.book_slot(page, slot):
                            return {
                                'time': slot['time'],
                                'court_name': slot['court_name'],
                                'date': target_date.strftime('%Y-%m-%d')
                            }
                        else:
                            # Booking failed but slot was available - might be worth retrying
                            booking_error = True
                            logger.warning(f"Booking failed for {slot['time']} at {slot['court_name']}")
                        
                    except Exception as e:
                        logger.warning(f"Error processing court {court_name}: {e}")
                        booking_error = True
                        continue
                
                # Decision: Only retry if there was a booking error, not if no slots were found
                if found_any_slots and booking_error:
                    # We found slots but booking failed - retry might help
                    if attempt < max_retries - 1:
                        logger.info(f"Found slots but booking failed. Retrying in {retry_delay/1000} seconds...")
                        page.wait_for_timeout(retry_delay)
                        continue
                elif not found_any_slots:
                    # No slots found at all - don't retry, just return
                    logger.info("No available slots found at target times across all courts")
                    return None
                else:
                    # Shouldn't reach here, but if we do, don't retry
                    return None
                
            except Exception as e:
                logger.error(f"Error in booking attempt {attempt + 1}: {e}")
                # Only retry on actual errors, not on "no slots found"
                if attempt < max_retries - 1:
                    logger.info(f"Retrying due to error in {retry_delay/1000} seconds...")
                    page.wait_for_timeout(retry_delay)
        
        logger.warning("All booking attempts completed")
        return None

