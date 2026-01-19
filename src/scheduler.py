"""Scheduler for running bookings at specific times."""
import logging
import schedule
import time
from datetime import datetime
from typing import Callable, List
from .config_loader import Config

logger = logging.getLogger(__name__)


class BookingScheduler:
    """Schedules and manages booking tasks."""
    
    def __init__(self, config: Config, booking_function: Callable):
        """Initialize scheduler.
        
        Args:
            config: Configuration object
            booking_function: Function to call when it's time to book
        """
        self.config = config
        self.booking_function = booking_function
        self.booking_times = config.booking_times
        self._setup_schedule()
    
    def _setup_schedule(self):
        """Set up scheduled jobs for each booking time.
        
        Note: Courts open on the hour (e.g., 7 PM Thursday next week opens at 7 PM this Thursday).
        The scheduler runs at the exact hour to book slots as soon as they become available.
        """
        for booking_time in self.booking_times:
            # Parse time (format: "HH:MM")
            try:
                hour, minute = booking_time.split(':')
                hour = int(hour)
                minute = int(minute)
                
                # Schedule daily at this exact time
                # Slots open on the hour, so we schedule at :00 to book immediately
                schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(
                    self._run_booking,
                    booking_time=booking_time
                )
                logger.info(f"Scheduled booking at {hour:02d}:{minute:02d} (slots open on the hour)")
            except Exception as e:
                logger.error(f"Failed to schedule time {booking_time}: {e}")
    
    def _run_booking(self, booking_time: str):
        """Run booking for a specific time.
        
        Note: This runs exactly on the hour when slots become available.
        A small delay (2 seconds) is added to ensure the slot is available.
        """
        import time as time_module
        logger.info(f"Running scheduled booking for {booking_time} (slots just opened)")
        
        # Small delay to ensure slot is available (slots open exactly on the hour)
        time_module.sleep(2)
        
        try:
            self.booking_function()
        except Exception as e:
            logger.error(f"Error in scheduled booking: {e}")
    
    def run_continuously(self):
        """Run scheduler continuously, checking for scheduled jobs."""
        check_interval = self.config.scheduler['check_interval_minutes']
        logger.info(f"Starting scheduler (checking every {check_interval} minute(s))")
        logger.info(f"Scheduled times: {', '.join(self.booking_times)}")
        
        while True:
            schedule.run_pending()
            time.sleep(check_interval * 60)  # Convert minutes to seconds
    
    def get_next_runs(self) -> List[datetime]:
        """Get list of next scheduled run times."""
        jobs = schedule.jobs
        next_runs = []
        for job in jobs:
            next_run = job.next_run
            if next_run:
                next_runs.append(next_run)
        return sorted(next_runs)
    
    def print_schedule(self):
        """Print current schedule."""
        logger.info("Current schedule:")
        for job in schedule.jobs:
            logger.info(f"  {job}")

