# Email Notification Alternatives

**Last Updated**: January 18, 2026

If Gmail App Passwords aren't available, here are alternative options:

## Option 1: Use Outlook/Hotmail (Simpler - No App Password Needed)

Outlook allows you to use your regular password (or a simpler setup):

### Setup Steps:

1. **Create or use Outlook account**:
   - Go to: https://outlook.live.com
   - Create account if needed (e.g., `tennisbot2026@outlook.com`)

2. **Configure on VM**:
   ```bash
   export SMTP_SERVER='smtp-mail.outlook.com'
   export SMTP_PORT='587'
   export NOTIFICATION_EMAIL_FROM='tennisbot2026@outlook.com'
   export NOTIFICATION_EMAIL_PASSWORD='your-outlook-password'
   export NOTIFICATION_EMAIL_TO='your-real-email@gmail.com'
   ```

3. **Add to ~/.bashrc**:
   ```bash
   echo 'export SMTP_SERVER="smtp-mail.outlook.com"' >> ~/.bashrc
   echo 'export SMTP_PORT="587"' >> ~/.bashrc
   echo 'export NOTIFICATION_EMAIL_FROM="tennisbot2026@outlook.com"' >> ~/.bashrc
   echo 'export NOTIFICATION_EMAIL_PASSWORD="your-password"' >> ~/.bashrc
   echo 'export NOTIFICATION_EMAIL_TO="your-real-email@gmail.com"' >> ~/.bashrc
   ```

**Note**: Outlook may require enabling "Less secure apps" or using a modern authentication method.

## Option 2: Enable 2FA on Gmail (Then App Passwords Work)

If the Gmail account doesn't have 2FA enabled:

1. **Enable 2-Step Verification**:
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification"
   - Follow the setup process

2. **Then create App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Should now work!

## Option 3: Use Yahoo Mail

Yahoo also supports SMTP with regular password:

```bash
export SMTP_SERVER='smtp.mail.yahoo.com'
export SMTP_PORT='587'
export NOTIFICATION_EMAIL_FROM='tennisbot2026@yahoo.com'
export NOTIFICATION_EMAIL_PASSWORD='your-yahoo-password'
export NOTIFICATION_EMAIL_TO='your-real-email@gmail.com'
```

## Option 4: Use a Different Gmail Account

If `tennisbot2026@gmail.com` has restrictions, try:

1. **Create a new Gmail account** (different email)
2. **Enable 2FA immediately** during setup
3. **Create App Password** - should work now

## Option 5: Use SendGrid (Free Tier - API Key Based)

More complex but no password needed:

1. **Sign up**: https://sendgrid.com (free tier: 100 emails/day)
2. **Get API Key**
3. **Update code** to use SendGrid API instead of SMTP

This requires code changes - let me know if you want this option.

## Recommended: Outlook/Hotmail

**Easiest option** - Outlook usually works with regular password and doesn't require App Passwords.

### Quick Setup Script:

```bash
# On VM
export SMTP_SERVER='smtp-mail.outlook.com'
export SMTP_PORT='587'
export NOTIFICATION_EMAIL_FROM='tennisbot2026@outlook.com'
export NOTIFICATION_EMAIL_PASSWORD='your-password'
export NOTIFICATION_EMAIL_TO='your-real-email@gmail.com'

# Add to ~/.bashrc
cat >> ~/.bashrc << 'EOF'
# Tennis Bot Email Notifications
export SMTP_SERVER='smtp-mail.outlook.com'
export SMTP_PORT='587'
export NOTIFICATION_EMAIL_FROM='tennisbot2026@outlook.com'
export NOTIFICATION_EMAIL_PASSWORD='your-password'
export NOTIFICATION_EMAIL_TO='your-real-email@gmail.com'
EOF

# Test
cd ~/tennis-booking-bot
source venv/bin/activate
python scripts/monitoring/check_auth_and_notify.py
```

## Testing

After setup, test with:
```bash
python scripts/monitoring/check_auth_and_notify.py
```

You should receive a test email.

