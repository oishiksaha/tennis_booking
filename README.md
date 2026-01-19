# Tennis Booking Bot

Automated tennis court booking system using Playwright to book courts daily at specified times.

## Features

- **Two Modes**:
  - **Auto Mode**: Automated daily bookings at specified times (7 AM, 8 AM, 5 PM, 6 PM, 7 PM)
  - **Manual Mode**: Interactive mode for testing, checking availability, and manual booking
- **SSO Authentication**: Handles authentication with persistent browser state
- **Flexible Scheduling**: Configurable booking times via YAML config
- **Availability Checker**: View available slots for testing and planning
- **Calendar Integration**: Optional Microsoft Outlook calendar integration (future)

## Quick Start

See **[docs/QUICKSTART.md](docs/QUICKSTART.md)** for detailed setup instructions.

### Quick Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **First-Time Authentication**
   ```bash
   python -m src.main --authenticate
   ```

3. **Run the Bot**
   ```bash
   # Single booking attempt
   python -m src.main
   
   # Scheduled mode (runs continuously)
   python -m src.main --schedule
   
   # Manual mode (interactive)
   python -m src.main --manual
   ```

## Documentation

📚 **See [docs/INDEX.md](docs/INDEX.md) for complete documentation index**

Key guides:
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[MODES.md](docs/MODES.md)** - Understanding Auto vs Manual mode
- **[GCP_DEPLOYMENT.md](docs/GCP_DEPLOYMENT.md)** - Deploy to GCP VM
- **[PRODUCTION_SETUP.md](docs/PRODUCTION_SETUP.md)** - Production configuration
- **[AUTHENTICATION_INFO.md](docs/AUTHENTICATION_INFO.md)** - Authentication details

**Scheduled mode (runs continuously, checking for booking times):**
```bash
python src/main.py --schedule
```

**Manual mode (interactive testing and manual booking):**
```bash
python src/main.py --manual
```

**Check availability:**
```bash
python src/availability.py
```

## Configuration

Edit `config/config.yaml` to:
- Change booking times
- Set court preferences
- Adjust timeouts and retry settings

## Deployment to Cloud VM

See `scripts/setup_cloud.sh` for cloud VM setup instructions.

## Project Structure

```
tennis-booking-bot/
├── src/                    # Source code
├── config/                 # Configuration files
├── data/                   # Data storage (browser state, etc.)
├── scripts/                # Deployment scripts
└── requirements.txt        # Python dependencies
```

## Notes

- Booking window is 7 days ahead
- Browser state is saved in `data/browser_state/` (gitignored)
- Logs are saved in `logs/` directory

