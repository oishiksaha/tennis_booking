"""Manage existing bookings - view and cancel."""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from playwright.sync_api import Page
from .config_loader import Config

logger = logging.getLogger(__name__)


class BookingsManager:
    """Manages viewing and canceling existing bookings."""
    
    def __init__(self, config: Config):
        """Initialize bookings manager."""
        self.config = config
        self.selectors = config.selectors
    
    def get_my_bookings(self, page: Page) -> List[Dict]:
        """Get list of current bookings.
        
        Returns list of booking dictionaries with:
        - date: Booking date
        - time: Time slot (e.g., "7:00 - 8:00 AM")
        - court: Court name (e.g., "Murr Tennis: Court 2")
        - location: Location info
        - cancel_button_ref: Reference to cancel button (for canceling)
        - more_vert_button_ref: Reference to more_vert button (opens action menu)
        """
        bookings = []
        
        try:
            # Check if we're already on the bookings page
            current_url = page.url
            if '/profile/programregistrations' not in current_url.lower():
                # Navigate to bookings page if not already there
                self.view_bookings_page(page)
                page.wait_for_timeout(2000)
            else:
                logger.info("Already on bookings page, skipping navigation")
                page.wait_for_timeout(1000)  # Just wait for page to be ready
            
            # Based on browser inspection, bookings are displayed as cards with:
            # - Heading with court name (h2, h3, etc.)
            # - Time info (contains "Schedule" and time range)
            # - Location info (contains "location_on" and location text)
            # - more_vert button for actions
            
            # Look for all headings that might be court names
            # Court names are typically in headings (h2, h3, h4, etc.)
            # and contain "Court" or "Tennis"
            
            # Strategy: Find all headings, then find their parent containers
            # Each booking card seems to be a container with:
            # - A heading (court name)
            # - Time info
            # - Location info
            # - Action buttons
            
            # Based on HTML structure, bookings are in cards with:
            # - h3.program-name (court name like "Murr Tennis: Court 2")
            # - .event-time .opacity-text (time like "6:00 - 7:00 PM")
            # - .event-location-or-btn .opacity-text (location like "Indoor Tennis Court 2")
            # - .event-day and .event-month (date)
            # - button.dropdown-toggle (more_vert button)
            
            # Find all booking cards - they have class "upcoming-event-card" or contain h3.program-name
            # Wait a bit for page to fully load
            page.wait_for_timeout(2000)
            
            booking_cards = []
            
            # Method 1: Find by class "upcoming-event-card"
            # Note: The outer div with class "upcoming-event-card" doesn't have data-regid
            # The inner div with class "card" has the data-regid, so we need to find that
            outer_cards = page.query_selector_all('.upcoming-event-card')
            logger.info(f"Found {len(outer_cards)} elements with class 'upcoming-event-card'")
            if outer_cards:
                # For each outer card, find the inner card with data-regid
                for outer_card in outer_cards:
                    inner_card = outer_card.query_selector('.card[data-regid]')
                    if inner_card:
                        booking_cards.append(inner_card)
                    else:
                        # Fallback: use the outer card if inner not found
                        booking_cards.append(outer_card)
            
            # Method 2: Find by data-regid attribute (each booking card has one)
            if not booking_cards:
                cards_by_regid = page.query_selector_all('.card[data-regid]')
                logger.info(f"Found {len(cards_by_regid)} cards with data-regid attribute")
                if cards_by_regid:
                    booking_cards = list(cards_by_regid)
            
            # Method 3: Find by h3.program-name headings
            if not booking_cards:
                headings = page.query_selector_all("h3.program-name")
                logger.info(f"Found {len(headings)} program-name headings, using as fallback")
                for heading in headings:
                    try:
                        # Get the card's data-regid to find it uniquely
                        regid = heading.evaluate("""
                            el => {
                                const card = el.closest('.card[data-regid]');
                                return card ? card.getAttribute('data-regid') : null;
                            }
                        """)
                        if regid:
                            card = page.query_selector(f'.card[data-regid="{regid}"]')
                            if card and card not in booking_cards:
                                booking_cards.append(card)
                    except Exception as e:
                        logger.debug(f"Error finding card for heading: {e}")
                        pass
            
            logger.info(f"Total booking cards found: {len(booking_cards)}")
            
            for card in booking_cards:
                try:
                    # Extract court name from h3.program-name
                    court_heading = card.query_selector('h3.program-name')
                    if not court_heading:
                        continue
                    
                    court_name = court_heading.inner_text().strip()
                    if not court_name or "Court" not in court_name:
                        continue
                    
                    logger.debug(f"Found booking card: {court_name}")
                    
                    booking_info = {
                        'court': court_name,
                        'time': None,
                        'location': None,
                        'date': None,
                        'more_vert_button': None,
                        'heading_element': court_heading,
                        'card_element': card
                    }
                    
                    # Extract time from .event-time .opacity-text
                    try:
                        time_elem = card.query_selector('.event-time .opacity-text')
                        if time_elem:
                            time_text = time_elem.inner_text().strip()
                            # Format: "6:00 - 7:00 PM" or "7:00 - 8:00 AM"
                            booking_info['time'] = time_text
                            logger.debug(f"  Time: {time_text}")
                    except Exception as e:
                        logger.debug(f"  Could not extract time: {e}")
                    
                    # Extract location from .event-location-or-btn .opacity-text
                    try:
                        location_elem = card.query_selector('.event-location-or-btn .opacity-text')
                        if location_elem:
                            location_text = location_elem.inner_text().strip()
                            booking_info['location'] = location_text
                            logger.debug(f"  Location: {location_text}")
                    except Exception as e:
                        logger.debug(f"  Could not extract location: {e}")
                    
                    # Extract date from .event-day and .event-month
                    try:
                        day_elem = card.query_selector('.event-day')
                        month_elem = card.query_selector('.event-month')
                        if day_elem and month_elem:
                            day = day_elem.inner_text().strip()
                            month = month_elem.inner_text().strip()
                            booking_info['date'] = f"{month} {day}"
                            logger.debug(f"  Date: {month} {day}")
                    except Exception as e:
                        logger.debug(f"  Could not extract date: {e}")
                    
                    # Extract reg_id from the card's data-regid attribute
                    # The structure is: .upcoming-event-card > .card[data-regid]
                    # So we need to check the card itself or find a child with data-regid
                    try:
                        reg_id = None
                        
                        # Method 1: Direct attribute access on card (if card has it)
                        try:
                            reg_id = card.get_attribute('data-regid')
                            if reg_id:
                                logger.debug(f"  Reg ID (direct): {reg_id}")
                        except Exception:
                            pass
                        
                        # Method 2: If card doesn't have it, find child card with data-regid
                        if not reg_id:
                            try:
                                child_card = card.query_selector('.card[data-regid]')
                                if child_card:
                                    reg_id = child_card.get_attribute('data-regid')
                                    if reg_id:
                                        logger.debug(f"  Reg ID (from child card): {reg_id}")
                            except Exception:
                                pass
                        
                        # Method 3: Use evaluate to search up/down the DOM tree
                        if not reg_id:
                            try:
                                reg_id = card.evaluate("""
                                    el => {
                                        // First check if this element has it
                                        if (el.getAttribute('data-regid')) {
                                            return el.getAttribute('data-regid');
                                        }
                                        // Check child with class 'card'
                                        const childCard = el.querySelector('.card[data-regid]');
                                        if (childCard) {
                                            return childCard.getAttribute('data-regid');
                                        }
                                        // Check parent
                                        let current = el.parentElement;
                                        for (let i = 0; i < 3; i++) {
                                            if (!current) break;
                                            const regid = current.getAttribute('data-regid');
                                            if (regid) return regid;
                                            current = current.parentElement;
                                        }
                                        return null;
                                    }
                                """)
                                if reg_id:
                                    logger.debug(f"  Reg ID (evaluate search): {reg_id}")
                            except Exception as e:
                                logger.debug(f"  Method 3 failed: {e}")
                        
                        if reg_id:
                            booking_info['reg_id'] = reg_id
                            logger.info(f"  ✓ Reg ID extracted: {reg_id}")
                        else:
                            logger.warning(f"  ⚠️  Could not extract reg_id for booking: {court_name}")
                            logger.warning(f"     Cancellation will not work for this booking without reg_id")
                            # Still add the booking, but cancellation won't work without reg_id
                    except Exception as e:
                        logger.warning(f"  Error extracting reg_id: {e}", exc_info=True)
                    
                    # Find more_vert button - button with dropdown-toggle class
                    try:
                        more_vert = card.query_selector('button.dropdown-toggle')
                        if more_vert:
                            booking_info['more_vert_button'] = more_vert
                            logger.debug(f"  Found more_vert button")
                    except Exception as e:
                        logger.debug(f"  Could not find more_vert button: {e}")
                    
                    bookings.append(booking_info)
                    logger.info(f"Parsed booking: {court_name} on {booking_info.get('date', 'Unknown date')} at {booking_info.get('time', 'Unknown time')}")
                
                except Exception as e:
                    logger.debug(f"Error parsing booking card: {e}")
                    continue
            
            logger.info(f"Found {len(bookings)} booking(s)")
            return bookings
            
        except Exception as e:
            logger.error(f"Error getting bookings: {e}", exc_info=True)
            return bookings
    
    def cancel_booking(self, page: Page, booking_info: Dict) -> bool:
        """Cancel a specific booking.
        
        Workflow:
        1. Navigate to bookings page (if not already there)
        2. Find the booking card by reg_id
        3. Click more_vert button (three dots)
        4. Click "Cancel Registration" option in menu
        5. Click "Confirm" in the confirmation dialog
        
        Args:
            page: Playwright page object
            booking_info: Dictionary with booking details (from get_my_bookings)
            Must contain:
            - reg_id: Registration ID (required for finding the card)
            - court: Court name (for logging)
            - time: Time slot (for logging)
        
        Returns:
            True if cancellation successful, False otherwise
        """
        court = booking_info.get('court', 'Unknown')
        time = booking_info.get('time', 'Unknown')
        reg_id = booking_info.get('reg_id')
        
        if not reg_id:
            logger.error("Cannot cancel booking: Missing registration ID.")
            return False
        
        logger.info(f"Attempting to cancel booking: {court} at {time} (Reg ID: {reg_id})")
        
        try:
            # Step 1: Make sure we're on the bookings page
            current_url = page.url
            if '/profile/programregistrations' not in current_url.lower():
                logger.info("Navigating to bookings page...")
                self.view_bookings_page(page)
                page.wait_for_timeout(2000)
            
            # Step 2: Find the booking card by reg_id
            logger.info(f"Looking for booking card with reg_id: {reg_id}")
            booking_card = page.query_selector(f'.card[data-regid="{reg_id}"]')
            
            if not booking_card:
                # Try with upcoming-event-card class
                booking_card = page.query_selector(f'.upcoming-event-card[data-regid="{reg_id}"]')
            
            if not booking_card:
                logger.error(f"Could not find booking card with reg_id: {reg_id}")
                return False
            
            logger.info("Found booking card, looking for more_vert button...")
            
            # Step 3: Find the more_vert button within this card
            more_vert_button = booking_card.query_selector('button.dropdown-toggle')
            
            if not more_vert_button:
                # Try alternative selectors
                more_vert_button = booking_card.query_selector('button[aria-label*="Action"]')
            
            if not more_vert_button:
                logger.error("Could not find more_vert button for booking")
                return False
            
            logger.info("Clicking more_vert button...")
            more_vert_button.click()
            page.wait_for_timeout(1000)  # Wait for dropdown menu to appear
            
            # Step 4: Click "Cancel Registration" in the dropdown menu
            logger.info("Looking for 'Cancel Registration' link in dropdown...")
            cancel_link = page.locator('div.dropdown-menu.show a.dropdown-item:has-text("Cancel Registration")').first
            
            if not cancel_link.is_visible(timeout=2000):
                logger.warning("Cancel Registration link not found or not visible in dropdown.")
                # Check if it's disabled
                if "disabled" in cancel_link.get_attribute("class", timeout=1000) or "text-muted" in cancel_link.get_attribute("class", timeout=1000):
                    logger.warning("Cancel Registration link is disabled. Cannot cancel this booking.")
                    return False
                return False
            
            logger.info("Clicking 'Cancel Registration' link...")
            cancel_link.click()
            page.wait_for_timeout(1000)  # Wait for confirmation dialog
            
            # Step 5: Confirm cancellation in the dialog
            logger.info("Looking for cancellation confirmation dialog...")
            confirm_dialog = page.get_by_role("dialog").filter(has=page.get_by_text("Cancel Registration?", exact=False)).first
            
            if not confirm_dialog.is_visible(timeout=3000):
                logger.error("Cancellation confirmation dialog not found or not visible.")
                return False
            
            logger.info("Clicking 'Confirm' button in dialog...")
            confirm_button = confirm_dialog.get_by_role("button", name="Confirm").first
            confirm_button.click()
            
            # Wait for the dialog to close and cancellation to process
            try:
                # Wait for dialog to disappear
                confirm_dialog.wait_for(state='hidden', timeout=5000)
            except Exception:
                pass  # Dialog might close differently
            
            # Wait a bit for the cancellation to process
            page.wait_for_timeout(2000)
            
            # Step 6: Verify cancellation - refresh the page to get updated bookings
            logger.info("Refreshing page to verify cancellation...")
            current_url = page.url
            page.reload(wait_until='domcontentloaded', timeout=10000)
            page.wait_for_timeout(2000)  # Wait for page to fully render
            
            # Re-fetch bookings and check if the cancelled booking is gone
            updated_bookings = self.get_my_bookings(page)
            is_cancelled = True
            for booking in updated_bookings:
                if booking.get('reg_id') == reg_id:
                    is_cancelled = False
                    logger.debug(f"Found booking with reg_id {reg_id}: {booking.get('date')} at {booking.get('time')}")
                    break
            
            if is_cancelled:
                logger.info(f"✓ Booking {court} at {time} successfully cancelled.")
                return True
            else:
                # The booking might still be in the list due to caching or timing
                # But if we got here, the cancellation was likely successful
                # Check if we can still find the booking card on the page
                try:
                    booking_card = page.query_selector(f'.card[data-regid="{reg_id}"]')
                    if not booking_card:
                        booking_card = page.query_selector(f'.upcoming-event-card .card[data-regid="{reg_id}"]')
                    
                    if not booking_card or not booking_card.is_visible():
                        logger.info(f"✓ Booking {court} at {time} successfully cancelled (card no longer visible).")
                        return True
                    else:
                        logger.warning(f"Booking {court} at {time} still visible on page after cancellation attempt.")
                        return False
                except Exception:
                    # If we can't check visibility, assume success since confirmation was clicked
                    logger.info(f"✓ Booking {court} at {time} cancellation confirmed (verification inconclusive).")
                    return True
            
        except Exception as e:
            logger.error(f"Error canceling booking: {e}", exc_info=True)
            return False
    
    def view_bookings_page(self, page: Page) -> str:
        """Navigate to bookings page and return the HTML for inspection.
        
        Workflow:
        1. Click profile button
        2. Click "Program Registrations" in left sidebar
        3. Save HTML for inspection
        """
        try:
            logger.info("Navigating to bookings page...")
            page.goto(self.config.booking_url, wait_until='networkidle')
            page.wait_for_timeout(2000)
            
            # Step 1: Click profile button (opens dropdown)
            profile_button = page.query_selector('#btnProfile')
            if profile_button and profile_button.is_visible():
                logger.info("Clicking profile button (opens dropdown)...")
                profile_button.click()
                page.wait_for_timeout(1000)  # Wait for dropdown to appear
                
                # Step 1b: Click "Profile" link in the dropdown popup
                logger.info("Looking for 'Profile' link in dropdown...")
                profile_clicked = False
                
                # Method 1: Try by ID (most reliable)
                try:
                    profile_link_elem = page.query_selector('#lnkProfile')
                    if profile_link_elem and profile_link_elem.is_visible(timeout=2000):
                        logger.info("Found 'Profile' link by ID (#lnkProfile), clicking...")
                        profile_link_elem.click()
                        # Wait for navigation to complete
                        page.wait_for_load_state('networkidle', timeout=10000)
                        page.wait_for_timeout(2000)  # Extra wait for page to fully render
                        
                        logger.info(f"After click, URL is: {page.url}")
                        logger.info(f"Page title: {page.title()}")
                        profile_clicked = True
                except Exception as e:
                    logger.debug(f"Error finding Profile link by ID: {e}")
                
                # Method 2: Try by href
                if not profile_clicked:
                    try:
                        profile_link_elem = page.query_selector('a[href="/Profile"]')
                        if profile_link_elem and profile_link_elem.is_visible(timeout=2000):
                            logger.info("Found 'Profile' link by href, clicking...")
                            profile_link_elem.click()
                            page.wait_for_load_state('networkidle', timeout=10000)
                            page.wait_for_timeout(2000)
                            logger.info(f"After click, URL is: {page.url}")
                            profile_clicked = True
                    except Exception as e:
                        logger.debug(f"Error finding Profile link by href: {e}")
                
                # Method 3: Try by text
                if not profile_clicked:
                    try:
                        profile_link_elem = page.get_by_text("Profile", exact=True).first
                        if profile_link_elem.is_visible(timeout=2000):
                            logger.info("Found 'Profile' link by text, clicking...")
                            profile_link_elem.click()
                            page.wait_for_load_state('networkidle', timeout=10000)
                            page.wait_for_timeout(2000)
                            logger.info(f"After click, URL is: {page.url}")
                            profile_clicked = True
                        else:
                            logger.warning("Profile link not found in dropdown")
                            return page.content()
                    except Exception:
                        logger.warning("Could not find Profile link in dropdown")
                        return page.content()
                
                # Verify we actually navigated to profile page
                if profile_clicked:
                    # Wait a bit more and check URL
                    page.wait_for_timeout(1000)
                    current_url = page.url
                    logger.info(f"Current URL after navigation: {current_url}")
                    
                    if '/profile' not in current_url.lower() and '/Profile' not in current_url:
                        logger.warning(f"Expected to be on profile page, but URL is: {current_url}")
                        # Try waiting a bit more
                        page.wait_for_timeout(2000)
                        current_url = page.url
                        if '/profile' not in current_url.lower() and '/Profile' not in current_url:
                            logger.error("Failed to navigate to profile page")
                            return page.content()
                    
                    # Save profile page HTML for inspection
                    html = page.content()
                    self._save_html_for_inspection(html, "profile_page")
                    logger.info("Saved profile page HTML to data/profile_page.html")
                else:
                    logger.error("Failed to click Profile link")
                    return page.content()
            else:
                logger.warning("Profile button not found")
                return page.content()
            
            # Step 2: Click "Program Registration" in left sidebar on the profile page
            # Note: It's "Program Registration" (singular), not "Registrations"
            # IMPORTANT: We need to look in the profile page sidebar, not the main site sidebar
            logger.info("Looking for 'Program Registration' link in profile page sidebar...")
            
            # Wait a moment for page to fully load
            page.wait_for_timeout(1000)
            
            # The profile page has a navigation sidebar with links like:
            # - Profile
            # - Program Registration
            # - Membership
            # etc.
            # This is different from the main site navigation sidebar
            
            # Try different ways to find it
            program_reg_link = None
            
            # Method 1: Look in the profile navigation (role="navigation" with name="Profile")
            try:
                profile_nav = page.get_by_role("navigation", name="Profile").first
                if profile_nav.is_visible(timeout=2000):
                    logger.info("Found profile navigation sidebar")
                    # Look for "Program Registration" link in this navigation
                    program_reg_link = profile_nav.get_by_text("Program Registration", exact=False).first
                    if program_reg_link.is_visible(timeout=2000):
                        logger.info("Found 'Program Registration' link in profile navigation")
                    else:
                        program_reg_link = None
                else:
                    profile_nav = None
            except Exception as e:
                logger.debug(f"Error finding profile navigation: {e}")
                profile_nav = None
            
            # Method 2: Exact text match (singular) - search entire page
            if not program_reg_link:
                try:
                    program_reg_link = page.get_by_text("Program Registration", exact=True).first
                    if program_reg_link.is_visible(timeout=2000):
                        logger.info("Found 'Program Registration' link (exact match)")
                    else:
                        program_reg_link = None
                except Exception:
                    pass
            
            # Method 3: Partial text match
            if not program_reg_link:
                try:
                    program_reg_link = page.get_by_text("Program Registration", exact=False).first
                    if program_reg_link.is_visible(timeout=2000):
                        logger.info("Found 'Program Registration' link (partial match)")
                    else:
                        program_reg_link = None
                except Exception:
                    pass
            
            # Method 4: Try plural version as fallback
            if not program_reg_link:
                try:
                    program_reg_link = page.get_by_text("Program Registrations", exact=False).first
                    if program_reg_link.is_visible(timeout=2000):
                        logger.info("Found 'Program Registrations' link (plural)")
                    else:
                        program_reg_link = None
                except Exception:
                    pass
            
            # Method 3: Look for links in left sidebar (most reliable)
            if not program_reg_link:
                try:
                    # Look for sidebar (common classes: sidebar, nav, menu, etc.)
                    sidebar_selectors = [
                        "aside",
                        ".sidebar",
                        ".nav",
                        ".menu",
                        "[role='navigation']",
                        ".left-sidebar",
                        ".side-nav",
                        ".side-bar",
                        "nav",
                        ".navigation",
                        "[class*='sidebar']",
                        "[class*='nav']"
                    ]
                    
                    sidebar = None
                    for selector in sidebar_selectors:
                        try:
                            elements = page.query_selector_all(selector)
                            for elem in elements:
                                if elem.is_visible():
                                    sidebar = elem
                                    logger.info(f"Found visible sidebar with selector: {selector}")
                                    break
                            if sidebar:
                                break
                        except Exception:
                            continue
                    
                    if sidebar:
                        # Look for all links in sidebar
                        all_links = sidebar.query_selector_all("a")
                        logger.info(f"Found {len(all_links)} links in sidebar")
                        
                        # Log all link texts for debugging
                        link_texts = []
                        for link in all_links:
                            try:
                                link_text = link.inner_text().strip()
                                link_texts.append(link_text)
                                logger.debug(f"Sidebar link: '{link_text}'")
                            except Exception:
                                pass
                        
                        logger.info(f"All sidebar links: {link_texts}")
                        
                        # Look for link containing "Program" and "Registration"
                        for link in all_links:
                            try:
                                link_text = link.inner_text().strip()
                                if "program" in link_text.lower() and "registration" in link_text.lower():
                                    program_reg_link = link
                                    logger.info(f"Found 'Program Registrations' link: '{link_text}'")
                                    break
                            except Exception:
                                continue
                    else:
                        logger.warning("Could not find sidebar element")
                except Exception as e:
                    logger.debug(f"Error searching sidebar: {e}")
                    pass
            
            if program_reg_link:
                logger.info("Clicking 'Program Registrations'...")
                program_reg_link.click()
                # Wait for navigation to complete
                page.wait_for_load_state('networkidle', timeout=10000)
                page.wait_for_timeout(2000)  # Extra wait for page to fully render
                
                logger.info(f"Navigated to bookings page: {page.url}")
                logger.info(f"Page title: {page.title()}")
                
                # Save the bookings page HTML
                html = page.content()
                self._save_html_for_inspection(html, "bookings_page")
                logger.info("Saved bookings page HTML to data/bookings_page.html")
                
                return html
            else:
                logger.warning("Could not find 'Program Registrations' link")
                logger.info("Saved current page HTML for inspection")
                logger.info("Please check data/profile_page.html to see the sidebar structure")
                html = page.content()
                self._save_html_for_inspection(html, "current_page")
                return html
            
            # If profile button approach didn't work, try direct URLs
            possible_urls = [
                f"{self.config.urls['base']}/Account/Bookings",
                f"{self.config.urls['base']}/MyBookings",
                f"{self.config.urls['base']}/Reservations",
                f"{self.config.urls['base']}/MyReservations",
                f"{self.config.urls['base']}/Account",
            ]
            
            for url in possible_urls:
                try:
                    logger.info(f"Trying URL: {url}")
                    page.goto(url, wait_until='networkidle', timeout=10000)
                    page.wait_for_timeout(2000)
                    
                    html = page.content()
                    self._save_html_for_inspection(html, "bookings_page")
                    logger.info(f"Saved page HTML to data/bookings_page.html")
                    return html
                    
                except Exception as e:
                    logger.debug(f"URL {url} failed: {e}")
                    continue
            
            # Return current page HTML
            html = page.content()
            self._save_html_for_inspection(html, "current_page")
            return html
            
        except Exception as e:
            logger.error(f"Error viewing bookings page: {e}")
            return ""
    
    def _save_html_for_inspection(self, html: str, filename: str):
        """Save HTML to file for inspection."""
        from pathlib import Path
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        
        html_file = data_dir / f"{filename}.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"Saved HTML to {html_file}")
    
    def analyze_bookings_html(self, page: Page) -> Dict:
        """Analyze the bookings page HTML to find card structure.
        
        Returns analysis of the page structure to help determine selectors.
        """
        try:
            # Make sure we're on bookings page
            self.view_bookings_page(page)
            page.wait_for_timeout(2000)
            
            analysis = {
                'url': page.url,
                'title': page.title(),
                'potential_cards': [],
                'potential_cancel_buttons': [],
                'text_content': []
            }
            
            # Look for common card patterns
            card_elements = page.query_selector_all('.card, [class*="card"], [class*="booking"], [class*="registration"]')
            analysis['potential_cards'] = [f"Found {len(card_elements)} elements with card/booking/registration classes"]
            
            # Look for cancel/remove buttons
            cancel_texts = ['cancel', 'remove', 'delete', 'withdraw']
            for text in cancel_texts:
                buttons = page.get_by_text(text, exact=False).all()
                if buttons:
                    analysis['potential_cancel_buttons'].append(f"Found {len(buttons)} elements with text '{text}'")
            
            # Get some sample text to understand structure
            body_text = page.query_selector('body')
            if body_text:
                # Get first 500 chars of text content
                full_text = body_text.inner_text()[:500]
                analysis['text_content'] = full_text.split('\n')[:20]  # First 20 lines
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing HTML: {e}")
            return {}

