# Simple Email Setup for Booking Notifications

**Last Updated**: January 18, 2026

This guide shows the simplest way to set up email notifications for booking results.

## Overview

The bot will automatically send you an email after each booking attempt with:
- ✅ Success: Court, date, time booked
- ❌ Failure: Reason why booking failed
- 📋 Logs: Recent log output for debugging

## Simplest Setup: Gmail (Recommended)

### Option 1: Use Your Existing Gmail (Requires 2FA)

1. **Enable 2-Factor Authentication** on your Gmail:
   - Go to: https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "Tennis Bot"
   - Copy the 16-character password (looks like: `abcd efgh ijkl mnop`)

3. **Configure on VM**:
   ```bash
   export NOTIFICATION_EMAIL_FROM='your-email@gmail.com'
   export NOTIFICATION_EMAIL_PASSWORD='abcdefghijklmnop'  # The 16-char password
   export NOTIFICATION_EMAIL_TO='your-email@gmail.com'
   
   # Add to ~/.bashrc to persist
   echo 'export NOTIFICATION_EMAIL_FROM="your-email@gmail.com"' >> ~/.bashrc
   echo 'export NOTIFICATION_EMAIL_PASSWORD="abcdefghijklmnop"' >> ~/.bashrc
   echo 'export NOTIFICATION_EMAIL_TO="your-email@gmail.com"' >> ~/.bashrc
   ```

### Option 2: Create a Dummy Gmail Account (No Personal Info)

1. **Create new Gmail account**:
   - Go to: https://accounts.google.com/signup
   - Create account (e.g., `tennisbot2026@gmail.com`)
   - **No personal info needed** - use fake name/phone

2. **Enable 2FA and create App Password** (same as Option 1)

3. **Configure on VM**:
   ```bash
   export NOTIFICATION_EMAIL_FROM='tennisbot2026@gmail.com'
   export NOTIFICATION_EMAIL_PASSWORD='app-password-here'
   export NOTIFICATION_EMAIL_TO='your-real-email@gmail.com'  # Where you want notifications
   ```

## Alternative: Outlook/Hotmail (Also Simple)

1. **Use Outlook account** (or create one)
2. **Configure on VM**:
   ```bash
   export SMTP_SERVER='smtp-mail.outlook.com'
   export SMTP_PORT='587'
   export NOTIFICATION_EMAIL_FROM='your-email@outlook.com'
   export NOTIFICATION_EMAIL_PASSWORD='your-password'
   export NOTIFICATION_EMAIL_TO='your-email@outlook.com'
   ```

## Testing

**Test the notification:**
```bash
python scripts/monitoring/check_auth_and_notify.py
```

**Or trigger a booking attempt:**
```bash
python -m src.main --headless
```

You should receive an email with the booking result and logs.

## What You'll Receive

### Success Email
```
Subject: ✅ Tennis Bot: Booking Successful - Murr Tennis: Court 4

Status: ✅ SUCCESS
Time: 2026-01-20 07:00:15

Booking Details:
  Court: Murr Tennis: Court 4
  Date: 2026-01-27
  Time: 7:00 AM

Recent Log Output:
[logs included here]
```

### Failure Email
```
Subject: ❌ Tennis Bot: Booking Failed

Status: ❌ FAILED
Time: 2026-01-20 07:00:15

Possible reasons:
  - No slots available at target times
  - All slots were already booked
  - Booking process encountered an error

Recent Log Output:
[logs included here]
```

## Automatic Notifications

**Notifications are sent automatically** after each booking attempt:
- When cron jobs run (7 AM, 8 AM, 5 PM, 6 PM, 7 PM)
- When you run `python -m src.main --headless`
- When you run `python -m src.main --test-now`

**No additional setup needed** - just configure the email credentials once!

## Troubleshooting

### "Email credentials not configured"
- Check that environment variables are set
- Verify with: `echo $NOTIFICATION_EMAIL_FROM`

### "Failed to send email"
- Verify App Password is correct (16 characters, no spaces)
- Check that 2FA is enabled on Gmail
- Try testing with: `python scripts/monitoring/check_auth_and_notify.py`

### "Authentication failed" in email
- This means the bot couldn't authenticate to book
- Check VM logs: `bash scripts/monitoring/view_vm_logs.sh`
- Re-authenticate: `bash scripts/auth/reauth_vm.sh`

## Security Notes

- **App Passwords are safe** - they're separate from your main password
- **Dummy account is fine** - no personal info needed
- **Credentials are stored on VM only** - not in code or git

## See Also

- **[NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md)** - Full notification setup guide
- **[PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)** - Production configuration

