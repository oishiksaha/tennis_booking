# File Organization Guide

**Last Updated**: January 18, 2026

This document describes the organization of all files in the tennis-booking-bot project.

## Directory Structure

```
tennis-booking-bot/
├── README.md                    # Main project overview
├── requirements.txt             # Python dependencies
├── run.sh                       # Main entry point script
│
├── config/                      # Configuration files
│   └── config.yaml             # Main configuration file
│
├── src/                        # Source code
│   ├── __init__.py
│   ├── main.py                 # Main entry point
│   ├── auth.py                 # Authentication handler
│   ├── booking_engine.py       # Core booking logic
│   ├── bookings_manager.py     # View/cancel bookings
│   ├── config_loader.py        # Configuration loader
│   ├── manual_mode.py          # Interactive manual mode
│   ├── scheduler.py            # Task scheduling
│   ├── availability.py         # Availability checker
│   └── calendar_integration.py # Calendar integration (future)
│
├── scripts/                    # Scripts and utilities
│   ├── utils/                  # Utility scripts
│   │   ├── README.md
│   │   ├── check_auth.py       # Interactive auth checker
│   │   ├── test_auth_selectors.py
│   │   ├── analyze_bookings_html.py
│   │   └── quick_check.sh
│   │
│   ├── deploy*.sh             # Deployment scripts
│   ├── setup_*.sh             # Setup scripts
│   ├── test_*.py              # Test scripts
│   ├── view_*.sh              # Log viewer scripts
│   └── ...                    # Other operational scripts
│
├── docs/                       # Documentation
│   ├── INDEX.md               # Table of contents
│   ├── QUICKSTART.md          # Quick setup guide
│   ├── MODES.md               # Operating modes
│   ├── GCP_DEPLOYMENT.md      # GCP deployment
│   ├── PRODUCTION_SETUP.md    # Production setup
│   ├── AUTHENTICATION_INFO.md # Authentication details
│   ├── SSH_TROUBLESHOOTING.md # SSH troubleshooting
│   ├── PROFILE_BUTTON_FIX.md  # Technical fix docs
│   └── FILE_ORGANIZATION.md   # This file
│
├── data/                       # Data files
│   ├── browser_state/         # Saved browser contexts
│   └── *.html                 # Saved HTML for debugging
│
├── logs/                       # Log files
│   └── booking_bot.log        # Main log file
│
└── venv/                       # Python virtual environment
```

## File Categories

### Root Directory Files

**README.md**
- Main project documentation
- Quick overview and links to detailed docs
- **Keep in root** (standard practice)

**requirements.txt**
- Python package dependencies
- **Keep in root** (standard Python project structure)

**run.sh**
- Main entry point script
- Convenient wrapper to run the bot
- **Keep in root** (primary entry point)

### Source Code (`src/`)

All Python source code for the bot:
- Core functionality modules
- Main entry point
- Business logic

### Scripts (`scripts/`)

**Main Scripts:**
- Deployment scripts (`deploy*.sh`, `setup_*.sh`)
- Test scripts (`test_*.py`, `run_test_*.py`)
- Log viewers (`view_*.sh`)
- VM management scripts

**Utility Scripts (`scripts/utils/`):**
- Development and debugging tools
- Interactive utilities
- HTML analysis tools

### Documentation (`docs/`)

All markdown documentation files:
- See `docs/INDEX.md` for complete index
- Organized by topic
- Easy to navigate

### Configuration (`config/`)

Configuration files:
- `config.yaml` - Main configuration

### Data (`data/`)

Runtime data:
- `browser_state/` - Saved authentication state
- `*.html` - Saved HTML for debugging

### Logs (`logs/`)

Log files:
- Rotating log files
- Production logs

## File Naming Conventions

### Scripts
- **Deployment**: `deploy*.sh`, `setup_*.sh`
- **Testing**: `test_*.py`, `run_test_*.py`
- **Viewing**: `view_*.sh`
- **Utilities**: In `scripts/utils/`

### Documentation
- All in `docs/` folder
- Descriptive names
- See `docs/INDEX.md` for organization

### Source Code
- Module names: `snake_case.py`
- Clear, descriptive names

## Adding New Files

### New Python Module
→ Add to `src/` directory

### New Script
→ Add to `scripts/` directory
→ If it's a utility/debugging tool, add to `scripts/utils/`

### New Documentation
→ Add to `docs/` directory
→ Update `docs/INDEX.md`

### New Configuration
→ Add to `config/` directory

## Maintenance

When organizing files:
1. Keep root directory clean (only essential files)
2. Group related files in subdirectories
3. Use descriptive names
4. Update this document if structure changes

