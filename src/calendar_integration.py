"""Microsoft Outlook calendar integration for checking class schedules.

NOTE: This module is currently NOT USED in production.
It's prepared for future calendar conflict checking functionality.
To use this, you would need to:
1. Register an Azure AD application
2. Configure MS_CLIENT_ID, MS_CLIENT_SECRET, MS_TENANT_ID in config
3. Integrate into booking_engine.py to check for class conflicts

Status: Future feature, not actively used.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from msal import ConfidentialClientApplication
import requests
from .config_loader import Config

logger = logging.getLogger(__name__)


class OutlookCalendar:
    """Microsoft Outlook calendar integration using Microsoft Graph API."""
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str):
        """Initialize Outlook calendar integration.
        
        Args:
            client_id: Azure AD application client ID
            client_secret: Azure AD application client secret
            tenant_id: Azure AD tenant ID
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        self._access_token = None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token for Microsoft Graph API."""
        try:
            app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=self.authority
            )
            
            result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                self._access_token = result["access_token"]
                return self._access_token
            else:
                logger.error(f"Failed to acquire token: {result.get('error_description')}")
                return None
                
        except Exception as e:
            logger.error(f"Error acquiring access token: {e}")
            return None
    
    def get_calendar_events(
        self,
        start_date: datetime,
        end_date: datetime,
        calendar_id: str = "calendar"
    ) -> List[Dict]:
        """Get calendar events for a date range.
        
        Args:
            start_date: Start date for events
            end_date: End date for events
            calendar_id: Calendar ID (default: "calendar" for primary calendar)
        
        Returns:
            List of calendar events
        """
        if not self._access_token:
            if not self.get_access_token():
                logger.error("Failed to get access token")
                return []
        
        try:
            # Format dates for API
            start_str = start_date.isoformat() + "Z"
            end_str = end_date.isoformat() + "Z"
            
            # Build API URL
            url = f"{self.graph_endpoint}/me/calendars/{calendar_id}/calendarView"
            params = {
                "startDateTime": start_str,
                "endDateTime": end_str,
                "$orderby": "start/dateTime"
            }
            
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            events = response.json().get("value", [])
            logger.info(f"Retrieved {len(events)} calendar events")
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving calendar events: {e}")
            return []
    
    def get_busy_times(
        self,
        start_date: datetime,
        end_date: datetime,
        calendar_id: str = "calendar"
    ) -> List[Dict]:
        """Get busy times from calendar.
        
        Returns list of dicts with 'start' and 'end' datetime objects.
        """
        events = self.get_calendar_events(start_date, end_date, calendar_id)
        
        busy_times = []
        for event in events:
            try:
                start_str = event.get("start", {}).get("dateTime")
                end_str = event.get("end", {}).get("dateTime")
                
                if start_str and end_str:
                    start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                    
                    busy_times.append({
                        "start": start_dt,
                        "end": end_dt,
                        "subject": event.get("subject", "No subject"),
                        "location": event.get("location", {}).get("displayName", "")
                    })
            except Exception as e:
                logger.warning(f"Error parsing event: {e}")
                continue
        
        return busy_times
    
    def is_time_available(
        self,
        target_time: datetime,
        duration_minutes: int = 90,
        buffer_minutes: int = 15
    ) -> bool:
        """Check if a time slot is available (no conflicts with calendar).
        
        Args:
            target_time: Target booking time
            duration_minutes: Duration of booking in minutes
            buffer_minutes: Buffer time before/after booking
        
        Returns:
            True if time is available, False if there's a conflict
        """
        start_check = target_time - timedelta(minutes=buffer_minutes)
        end_check = target_time + timedelta(minutes=duration_minutes + buffer_minutes)
        
        busy_times = self.get_busy_times(start_check, end_check)
        
        for busy in busy_times:
            busy_start = busy["start"]
            busy_end = busy["end"]
            
            # Check for overlap
            if (target_time < busy_end) and (target_time + timedelta(minutes=duration_minutes) > busy_start):
                logger.info(
                    f"Time conflict detected: {target_time} conflicts with "
                    f"{busy['subject']} ({busy_start} - {busy_end})"
                )
                return False
        
        return True
    
    def filter_available_times(
        self,
        candidate_times: List[datetime],
        duration_minutes: int = 90,
        buffer_minutes: int = 15
    ) -> List[datetime]:
        """Filter list of candidate times to only include available ones.
        
        Args:
            candidate_times: List of candidate booking times
            duration_minutes: Duration of booking in minutes
            buffer_minutes: Buffer time before/after booking
        
        Returns:
            List of available times (no calendar conflicts)
        """
        available = []
        for time in candidate_times:
            if self.is_time_available(time, duration_minutes, buffer_minutes):
                available.append(time)
        
        return available


def get_class_schedule(
    config: Config,
    start_date: datetime,
    end_date: datetime
) -> List[Dict]:
    """Get class schedule from Outlook calendar.
    
    This is a convenience function that uses the OutlookCalendar class.
    """
    if not config.ms_client_id or not config.ms_client_secret or not config.ms_tenant_id:
        logger.warning("Microsoft Graph API credentials not configured")
        return []
    
    calendar = OutlookCalendar(
        client_id=config.ms_client_id,
        client_secret=config.ms_client_secret,
        tenant_id=config.ms_tenant_id
    )
    
    return calendar.get_calendar_events(start_date, end_date)


# Note: To use this integration, you need to:
# 1. Register an application in Azure AD
# 2. Grant it "Calendars.Read" permission
# 3. Add the credentials to .env file
# This is optional and can be set up later

