"""Notification system for authentication status alerts."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class NotificationSender:
    """Send notifications via email or SMS."""
    
    def __init__(self):
        """Initialize notification sender."""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_from = os.getenv('NOTIFICATION_EMAIL_FROM')
        self.email_to = os.getenv('NOTIFICATION_EMAIL_TO')
        self.email_password = os.getenv('NOTIFICATION_EMAIL_PASSWORD')
        self.sms_email = os.getenv('SMS_EMAIL')  # Email-to-SMS gateway
        
    def send_email(self, subject: str, body: str, to_email: Optional[str] = None) -> bool:
        """Send email notification.
        
        Args:
            subject: Email subject
            body: Email body
            to_email: Recipient email (defaults to NOTIFICATION_EMAIL_TO)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.email_from or not self.email_password:
            logger.warning("Email credentials not configured. Skipping email notification.")
            return False
            
        to_email = to_email or self.email_to
        if not to_email:
            logger.warning("No recipient email configured. Skipping email notification.")
            return False
        
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
            
            logger.info(f"Email notification sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
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

