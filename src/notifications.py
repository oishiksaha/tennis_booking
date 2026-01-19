"""Notification system for booking and authentication status alerts."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path
import os

logger = logging.getLogger(__name__)

# Try to import SendGrid (optional)
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False


class NotificationSender:
    """Send notifications via email or SMS."""
    
    def __init__(self):
        """Initialize notification sender.
        
        Supports multiple email providers:
        - SendGrid (API-based, recommended for automated emails)
        - Gmail (requires App Password with 2FA)
        - Outlook/Hotmail
        - Yahoo
        - Custom SMTP server
        """
        # SendGrid configuration (preferred if available)
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.use_sendgrid = bool(self.sendgrid_api_key and SENDGRID_AVAILABLE)
        
        # SMTP configuration (fallback)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('NOTIFICATION_EMAIL_FROM') or os.getenv('EMAIL_FROM')
        self.email_to = os.getenv('NOTIFICATION_EMAIL_TO') or os.getenv('EMAIL_TO')
        self.email_password = os.getenv('NOTIFICATION_EMAIL_PASSWORD') or os.getenv('EMAIL_PASSWORD')
        self.sms_email = os.getenv('SMS_EMAIL')  # Email-to-SMS gateway
        
        # Auto-detect SMTP settings based on email domain
        if self.email_from and not os.getenv('SMTP_SERVER'):
            if '@gmail.com' in self.email_from:
                self.smtp_server = 'smtp.gmail.com'
                self.smtp_port = 587
            elif '@outlook.com' in self.email_from or '@hotmail.com' in self.email_from:
                self.smtp_server = 'smtp-mail.outlook.com'
                self.smtp_port = 587
            elif '@yahoo.com' in self.email_from:
                self.smtp_server = 'smtp.mail.yahoo.com'
                self.smtp_port = 587
        
    def send_email(self, subject: str, body: str, to_email: Optional[str] = None) -> bool:
        """Send email notification.
        
        Uses SendGrid API if configured, otherwise falls back to SMTP.
        
        Args:
            subject: Email subject
            body: Email body
            to_email: Recipient email (defaults to NOTIFICATION_EMAIL_TO)
            
        Returns:
            True if sent successfully, False otherwise
        """
        to_email = to_email or self.email_to
        if not to_email:
            logger.warning("No recipient email configured. Skipping email notification.")
            return False
        
        # Try SendGrid first (if configured)
        if self.use_sendgrid:
            return self._send_email_sendgrid(subject, body, to_email)
        
        # Fall back to SMTP
        if not self.email_from or not self.email_password:
            logger.warning("Email credentials not configured. Skipping email notification.")
            return False
        
        return self._send_email_smtp(subject, body, to_email)
    
    def _send_email_sendgrid(self, subject: str, body: str, to_email: str) -> bool:
        """Send email using SendGrid API."""
        try:
            if not SENDGRID_AVAILABLE:
                logger.error("SendGrid package not installed. Install with: pip install sendgrid")
                return False
            
            message = Mail(
                from_email=self.email_from or 'tennisbot2026@outlook.com',
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            
            logger.info(f"Email notification sent via SendGrid to {to_email} (status: {response.status_code})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {e}")
            return False
    
    def _send_email_smtp(self, subject: str, body: str, to_email: str) -> bool:
        """Send email using SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.email_password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent via SMTP to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False
    
    def send_sms(self, message: str, phone_number: Optional[str] = None) -> bool:
        """Send SMS via email-to-SMS gateway.
        
        Args:
            message: SMS message
            phone_number: Phone number (defaults to SMS_EMAIL env var)
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Email-to-SMS gateways (carrier-specific)
        # Format: phone_number@carrier_gateway.com
        sms_email = phone_number or self.sms_email
        
        if not sms_email:
            logger.warning("SMS email gateway not configured. Skipping SMS notification.")
            return False
        
        # If it's already an email address, use it directly
        # Otherwise, assume it's a phone number and we need carrier gateway
        if '@' in sms_email:
            return self.send_email("Tennis Bot Alert", message, sms_email)
        else:
            logger.warning("SMS email gateway format not recognized. Use format: phone@carrier.com")
            return False
    
    def send_booking_notification(
        self, 
        success: bool, 
        booking_details: Optional[Dict] = None,
        log_lines: Optional[list] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Send booking attempt notification with logs.
        
        Args:
            success: Whether booking was successful
            booking_details: Dict with court_name, date, time if successful
            log_lines: Recent log lines to include
            error_message: Error message if failed
            
        Returns:
            True if notification sent successfully
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if success and booking_details:
            subject = f"✅ Tennis Bot: Booking Successful - {booking_details.get('court_name', 'Unknown')}"
            body = f"""Tennis Booking Bot - Booking Result

Status: ✅ SUCCESS
Time: {timestamp}

Booking Details:
  Court: {booking_details.get('court_name', 'Unknown')}
  Date: {booking_details.get('date', 'Unknown')}
  Time: {booking_details.get('time', 'Unknown')}

The booking was completed successfully!
"""
        else:
            subject = "❌ Tennis Bot: Booking Failed"
            body = f"""Tennis Booking Bot - Booking Result

Status: ❌ FAILED
Time: {timestamp}

The booking attempt did not succeed.

"""
            if error_message:
                body += f"Error: {error_message}\n\n"
            else:
                body += "Possible reasons:\n"
                body += "  - No slots available at target times\n"
                body += "  - All slots were already booked\n"
                body += "  - Booking process encountered an error\n\n"
        
        # Add log lines if provided
        if log_lines:
            body += "\n" + "=" * 60 + "\n"
            body += "Recent Log Output:\n"
            body += "=" * 60 + "\n"
            body += "\n".join(log_lines[-50:])  # Last 50 lines
            body += "\n" + "=" * 60 + "\n"
        
        # Try email first
        email_sent = self.send_email(subject, body)
        
        # Also try SMS if configured
        sms_sent = False
        if self.sms_email:
            sms_msg = f"Tennis Bot: {'✅ Booked' if success else '❌ Failed'} - {timestamp}"
            if success and booking_details:
                sms_msg += f" {booking_details.get('court_name')} {booking_details.get('time')}"
            sms_sent = self.send_sms(sms_msg)
        
        return email_sent or sms_sent
    
    def send_auth_status_notification(self, is_authenticated: bool, details: str = "") -> bool:
        """Send authentication status notification.
        
        Args:
            is_authenticated: Whether authentication is working
            details: Additional details about the status
            
        Returns:
            True if notification sent successfully
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if is_authenticated:
            subject = "✅ Tennis Bot: Authentication Working"
            body = f"""Tennis Booking Bot - Authentication Status

Status: ✅ WORKING
Time: {timestamp}

Authentication is working correctly. The bot is ready to book courts.

{details}
"""
        else:
            subject = "❌ Tennis Bot: Authentication Failed"
            body = f"""Tennis Booking Bot - Authentication Status

Status: ❌ FAILED
Time: {timestamp}

Authentication has failed. The bot cannot book courts.

{details}

Action Required:
1. Check the VM logs: bash scripts/monitoring/view_vm_logs.sh
2. Re-authenticate: bash scripts/auth/reauth_vm.sh
3. Check keep-alive service: bash scripts/auth/view_auth_keepalive_log.sh
"""
        
        # Try email first
        email_sent = self.send_email(subject, body)
        
        # Also try SMS if configured
        sms_sent = False
        if self.sms_email:
            sms_sent = self.send_sms(f"Tennis Bot: {'✅ Auth OK' if is_authenticated else '❌ Auth Failed'} - {timestamp}")
        
        return email_sent or sms_sent


def get_carrier_sms_gateway(phone_number: str, carrier: str) -> str:
    """Get email-to-SMS gateway address for a phone number.
    
    Args:
        phone_number: Phone number (digits only, e.g., "1234567890")
        carrier: Carrier name (att, verizon, tmobile, sprint)
        
    Returns:
        Email address for SMS gateway
    """
    carriers = {
        'att': '@txt.att.net',
        'verizon': '@vtext.com',
        'tmobile': '@tmomail.net',
        'sprint': '@messaging.sprintpcs.com',
        'uscellular': '@email.uscc.net',
        'cricket': '@sms.cricketwireless.net',
    }
    
    gateway = carriers.get(carrier.lower())
    if not gateway:
        raise ValueError(f"Unknown carrier: {carrier}. Supported: {', '.join(carriers.keys())}")
    
    return f"{phone_number}{gateway}"

