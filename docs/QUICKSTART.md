# Quick Start Guide

Get up and running with the tennis booking bot in 5 minutes.

## Local Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure

The bot comes with default configuration in `config/config.yaml`. You can customize:
- Booking times (default: 7 AM, 8 AM, 5 PM, 6 PM, 7 PM)
- Booking window (default: 7 days ahead)
- Court preferences

Optional: Create a `.env` file for environment-specific settings:
```bash
cp .env.example .env
# Edit .env if needed
```

### 3. First-Time Authentication

Run the authentication setup (this will open a browser):

```bash
python src/main.py --authenticate
```

Log in manually when the browser opens. The browser state will be saved for future runs.

### 4. Test Booking

Run a single booking attempt:

```bash
python src/main.py
```

This will attempt to book a court at one of your configured times for 7 days ahead.

### 5. Test Auto Mode

To test the automatic booking logic without waiting for scheduled times:

```bash
python src/main.py --test-now
```

This runs a booking attempt immediately using the same logic as auto mode, perfect for testing.

### 6. Run Scheduled Mode (Auto Mode)

To run continuously and book at scheduled times:

```bash
python src/main.py --schedule
```

The bot will check every minute and book when it's time (7 AM, 8 AM, 5 PM, 6 PM, 7 PM).
**Note**: Slots open on the hour, so the bot runs exactly at :00 to book immediately.

### 7. Manual Mode (For Testing)

For interactive testing and manual booking:

```bash
python src/main.py --manual
```

This opens an interactive menu where you can:
- Check available courts and slots
- Book a specific slot manually
- Check availability for specific dates
- Test selectors (debug mode)

This is useful for:
- Testing and verifying selectors work correctly
- Manually booking when you want to choose
- Debugging booking issues

## Check Availability

To see what slots are available:

```bash
python src/availability.py
```

Or check specific number of days:

```bash
python src/availability.py --days 14
```

## Command Line Options

```bash
# Single booking attempt (auto mode - one try)
python src/main.py

# Run scheduler (continuous auto mode)
python src/main.py --schedule

# Test mode - run booking immediately (bypasses scheduler, for testing)
python src/main.py --test-now

# Manual mode (interactive)
python src/main.py --manual

# Run in headless mode (no browser window)
python src/main.py --headless

# Authentication only
python src/main.py --authenticate

# Custom config file
python src/main.py --config /path/to/config.yaml
```

## Two Modes Explained

### Auto Mode
- **Purpose**: Automatic daily bookings when you're not using the system
- **Usage**: `python src/main.py --schedule`
- **Behavior**: 
  - Runs continuously, checking every minute
  - Books automatically at configured times (7 AM, 8 AM, 5 PM, 6 PM, 7 PM)
  - Books exactly on the hour when slots open (e.g., 7:00 PM Thursday books for next Thursday 7:00 PM)
  - Best for: Production use, hands-off operation

### Manual Mode
- **Purpose**: Testing, debugging, and manual booking
- **Usage**: `python src/main.py --manual`
- **Behavior**:
  - Interactive menu with options
  - Check availability without booking
  - Manually select and book specific slots
  - Test selectors to verify they work
  - Best for: Development, testing, when you want to choose

## Troubleshooting

### Authentication Failed
- Make sure you're logged in when running `--authenticate`
- Check that `data/browser_state/` directory exists and is writable
- Try re-authenticating: `python src/main.py --authenticate`

### No Bookings Made
- Check if courts are available at your target times
- Verify booking window (7 days ahead)
- Check logs in `logs/booking_bot.log`
- Run availability checker to see what's available

### Import Errors
- Make sure you're in the project root directory
- Verify virtual environment is activated (if using one)
- Run: `pip install -r requirements.txt`

## Next Steps

- Deploy to cloud VM: See [DEPLOYMENT.md](DEPLOYMENT.md)
- Set up calendar integration: See `src/calendar_integration.py`
- Customize configuration: Edit `config/config.yaml`

