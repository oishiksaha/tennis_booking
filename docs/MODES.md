# Operating Modes

The tennis booking bot has two distinct modes for different use cases.

## Auto Mode

**Purpose**: Automatic daily bookings when you're not actively using the system.

### Usage
```bash
# Run continuously (for production)
python src/main.py --schedule

# Single booking attempt (for testing auto mode)
python src/main.py
```

### How It Works

1. **Scheduling**: The bot runs continuously and checks every minute if it's time to book
2. **Timing**: Books exactly on the hour when slots open
   - Example: 7:00 PM Thursday books for next Thursday at 7:00 PM
   - Slots open exactly on the hour, so the bot runs at :00 to book immediately
3. **Automatic**: No user interaction required
4. **Headless**: Can run in headless mode for cloud deployment

### When to Use
- Production deployment on cloud VM
- Daily automatic bookings
- When you're not actively using the system
- Hands-off operation

### Configuration
- Booking times are set in `config/config.yaml` (default: 7 AM, 8 AM, 5 PM, 6 PM, 7 PM)
- The bot books 7 days ahead automatically
- Books any available court (or specific courts if configured)

## Manual Mode

**Purpose**: Interactive testing, debugging, and manual booking selection.

### Usage
```bash
python src/main.py --manual
```

### Features

The manual mode provides an interactive menu with the following options:

1. **Check Available Courts and Slots**
   - Shows all available courts
   - Displays all available slots for the target date (7 days ahead)
   - Shows time, court name, and availability status
   - Useful for seeing what's available before booking

2. **Book a Specific Slot**
   - After checking availability, you can select a specific slot to book
   - Shows numbered list of available slots
   - Confirms before booking
   - Useful for manual booking when you want to choose

3. **Check Availability for Specific Date**
   - Check availability for any number of days ahead
   - Useful for planning ahead

4. **Test Selectors (Debug Mode)**
   - Tests if CSS selectors are working correctly
   - Shows what elements are found
   - Browser stays open for inspection
   - **Essential for testing and fixing selectors**

5. **Exit**
   - Cleanly exits the manual mode

### When to Use
- **Testing and debugging**: Verify selectors work correctly
- **Development**: Test booking flow before deploying auto mode
- **Manual booking**: When you want to choose a specific slot
- **Troubleshooting**: Debug why auto mode isn't working
- **Getting tags right**: Use selector test mode to verify elements

### Workflow for Testing

1. Run manual mode: `python src/main.py --manual`
2. Use "Test selectors" option to verify elements are found
3. Use "Check available courts and slots" to see if booking flow works
4. Use "Book a specific slot" to test the full booking process
5. Once everything works, switch to auto mode

## Key Differences

| Feature | Auto Mode | Manual Mode |
|---------|-----------|-------------|
| **Interaction** | None (fully automatic) | Interactive menu |
| **Use Case** | Production, daily use | Testing, debugging, manual booking |
| **Browser** | Can be headless | Always visible (for interaction) |
| **Timing** | Exactly on the hour | Anytime you run it |
| **Selection** | Books first available | You choose which slot |
| **Best For** | Cloud deployment | Development and testing |

## Timing Information

### When Slots Open

**Important**: Courts open on the hour. For example:
- 7:00 PM Thursday → Next Thursday 7:00 PM slot opens
- 8:00 AM Monday → Next Monday 8:00 AM slot opens

The auto mode scheduler is configured to run exactly at :00 (e.g., 7:00:00 PM) with a 2-second delay to ensure the slot is available.

### Booking Window

- Default: 7 days ahead
- Configurable in `config/config.yaml`
- Auto mode books for exactly 7 days ahead
- Manual mode can check any number of days ahead

## Switching Between Modes

You can switch between modes at any time:

1. **From Manual to Auto**: 
   - Exit manual mode
   - Run: `python src/main.py --schedule`

2. **From Auto to Manual**:
   - Stop the scheduler (Ctrl+C)
   - Run: `python src/main.py --manual`

Both modes use the same:
- Authentication (browser state is shared)
- Configuration file
- Booking engine logic

## Recommendations

1. **Start with Manual Mode**: 
   - Test everything works
   - Verify selectors
   - Test booking flow

2. **Then Use Auto Mode**:
   - Once manual mode works perfectly
   - Deploy to cloud VM
   - Run in scheduled mode

3. **Use Manual Mode for Troubleshooting**:
   - If auto mode fails, switch to manual
   - Use selector test mode to debug
   - Fix issues, then switch back to auto

