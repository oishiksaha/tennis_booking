# SendGrid Email Setup

**Last Updated**: January 18, 2026

SendGrid is a reliable email service designed for automated emails. It's perfect for booking notifications!

## Quick Setup

### Step 1: Sign Up for SendGrid

1. Go to: https://signup.sendgrid.com
2. Sign up for a free account
3. Verify your email address

### Step 2: Create API Key

1. Go to: https://app.sendgrid.com/settings/api_keys
2. Click "Create API Key"
3. Name it: "Tennis Bot"
4. Select permissions: **"Full Access"** (or at minimum: "Mail Send")
5. Click "Create & View"
6. **Copy the API key immediately** (you won't be able to see it again!)

### Step 3: Verify Sender Email

1. Go to: https://app.sendgrid.com/settings/sender_auth/senders
2. Click "Create New Sender"
3. Fill in:
   - **From Email**: `tennisbot2026@outlook.com`
   - **From Name**: Tennis Booking Bot
   - **Reply To**: `tennisbot2026@outlook.com`
4. Click "Create"
5. Check your email (`tennisbot2026@outlook.com`) and verify the sender

### Step 4: Configure on VM

Once you have the API key, I'll configure it on the VM:

```bash
export SENDGRID_API_KEY='your-api-key-here'
export NOTIFICATION_EMAIL_FROM='tennisbot2026@outlook.com'
export NOTIFICATION_EMAIL_TO='osaha@mba2026.hbs.edu'

# Add to ~/.bashrc
echo 'export SENDGRID_API_KEY="your-api-key-here"' >> ~/.bashrc
echo 'export NOTIFICATION_EMAIL_FROM="tennisbot2026@outlook.com"' >> ~/.bashrc
echo 'export NOTIFICATION_EMAIL_TO="osaha@mba2026.hbs.edu"' >> ~/.bashrc
```

## Free Tier Limits

- **100 emails/day** (plenty for booking notifications!)
- **Unlimited contacts**
- **Email API access**

## Testing

After setup, test with:

```bash
python scripts/monitoring/check_auth_and_notify.py
```

## Troubleshooting

### "Sender email not verified"
- Make sure you verified the sender email in SendGrid dashboard
- Check spam folder for verification email

### "API key invalid"
- Verify the API key was copied correctly
- Check that API key has "Mail Send" permissions

### "Rate limit exceeded"
- Free tier: 100 emails/day
- If you exceed, wait 24 hours or upgrade plan

## See Also

- **[NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md)** - General notification setup
- **[EMAIL_SETUP_SIMPLE.md](EMAIL_SETUP_SIMPLE.md)** - Simple email setup guide

