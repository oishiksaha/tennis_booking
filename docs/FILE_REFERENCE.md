# File Reference Guide

**Last Updated**: January 18, 2026

This document provides detailed explanations for every file in the tennis-booking-bot project.

## Root Directory Files

### `README.md`
- **Purpose**: Main project documentation and entry point
- **Contents**: Project overview, features, quick start, links to detailed docs
- **When to read**: First time exploring the project

### `requirements.txt`
- **Purpose**: Python package dependencies
- **Contents**: List of required Python packages with versions
- **Usage**: `pip install -r requirements.txt`
- **Key dependencies**: playwright, pyyaml, python-dotenv, schedule, msal

### `run.sh`
- **Purpose**: Convenient wrapper script to run the bot
- **Contents**: Activates virtual environment and runs main.py
- **Usage**: `bash run.sh` or `./run.sh`
- **Note**: Quick entry point for local development

---

## Configuration Files

### `config/config.yaml`
- **Purpose**: Main configuration file for the bot
- **Contents**:
  - Booking times (7 AM, 8 AM, 5 PM, 6 PM, 7 PM)
  - Booking window (7 days ahead)
  - Court preferences
  - URLs (base and program pages)
  - CSS selectors for web elements
  - Booking behavior settings (retries, timeouts)
  - Test mode settings
  - Logging configuration
- **Usage**: Edit to change booking behavior without modifying code
- **Important**: This is the primary way to configure the bot

---

## Source Code (`src/`)

### `src/__init__.py`
- **Purpose**: Makes `src/` a Python package
- **Contents**: Empty file (package marker)
- **Note**: Required for Python imports

### `src/main.py`
- **Purpose**: Main entry point for the bot
- **Contents**:
  - CLI argument parsing (`--schedule`, `--authenticate`, `--manual`, `--headless`, `--test-now`)
  - Orchestrates all components
  - Sets up logging
  - Handles different execution modes
- **Key functions**:
  - `run_booking()`: Execute booking attempt
  - `run_scheduled()`: Run scheduler for continuous operation
  - `authenticate_only()`: Just authenticate and save state
  - `main()`: Entry point
- **Usage**: `python -m src.main [options]`

### `src/config_loader.py`
- **Purpose**: Loads and manages configuration from YAML
- **Contents**:
  - `Config` class that reads `config.yaml`
  - Properties for all configuration values
  - Environment variable overrides
  - Test mode configuration access
- **Key features**: Type-safe configuration access, environment variable support

### `src/auth.py`
- **Purpose**: Handles SSO authentication
- **Contents**:
  - `AuthHandler` class
  - Browser context persistence (saves/loads cookies)
  - Authentication checking (profile button detection)
  - Manual authentication flow
- **Key methods**:
  - `is_authenticated()`: Check if user is logged in
  - `authenticate()`: Manual login flow
  - `ensure_authenticated()`: Ensure user is logged in
  - `save_browser_state()`: Save cookies for future use
- **Important**: Uses Playwright's storage state to persist authentication

### `src/booking_engine.py`
- **Purpose**: Core booking logic
- **Contents**:
  - `BookingEngine` class
  - Court selection logic
  - Date navigation (fast navigation to target dates)
  - Time slot finding and selection
  - Booking flow (select → register → checkout)
  - Test mode support
- **Key methods**:
  - `attempt_booking()`: Main booking logic
  - `find_available_slots()`: Find open time slots
  - `navigate_to_target_date_fast()`: Optimized date navigation
  - `get_target_date()`: Calculate target date (7 days ahead or test mode)
- **Important**: This is where the actual booking happens

### `src/bookings_manager.py`
- **Purpose**: View and cancel existing bookings
- **Contents**:
  - `BookingsManager` class
  - Navigation to profile/bookings page
  - Booking extraction from HTML
  - Cancellation flow
- **Key methods**:
  - `get_my_bookings()`: Get list of all bookings
  - `cancel_booking()`: Cancel a specific booking
  - `view_bookings_page()`: Navigate to bookings page
- **Usage**: Used by manual mode for viewing/canceling bookings

### `src/manual_mode.py`
- **Purpose**: Interactive manual mode for testing and manual booking
- **Contents**:
  - `ManualMode` class
  - Interactive menu system
  - Options for checking availability, booking, viewing bookings, canceling
- **Key features**:
  - Option 1: Check availability (7 days from today)
  - Option 2: Book a specific court/time
  - Option 3: View my bookings
  - Option 4: Cancel a booking
  - Option 5: Check availability for specific date
  - Option 6: View all open slots (all dates, all courts)
- **Usage**: `python -m src.main --manual`

### `src/availability.py`
- **Purpose**: Check court availability
- **Contents**:
  - `check_availability()` function
  - Date navigation
  - Slot extraction
  - Availability reporting
- **Usage**: Used by manual mode and booking engine

### `src/scheduler.py`
- **Purpose**: Schedule bookings at specific times
- **Contents**:
  - `BookingScheduler` class
  - Uses `schedule` library
  - Continuous execution loop
- **Key features**: Schedules bookings at configured times, runs continuously
- **Usage**: `python -m src.main --schedule` (local development)

### `src/calendar_integration.py`
- **Purpose**: Microsoft Outlook calendar integration (future feature)
- **Contents**:
  - `OutlookCalendar` class
  - Microsoft Graph API integration
  - Calendar event fetching
- **Status**: Not currently used, prepared for future calendar conflict checking
- **Note**: Requires Azure AD app registration

---

## Scripts (`scripts/`)

### Authentication Scripts (`scripts/auth/`)

#### `test_authentication.py`
- **Purpose**: Test if authentication is valid
- **Usage**: `python scripts/auth/test_authentication.py`
- **Output**: Success/failure status with detailed checks

#### `auth_keepalive.py`
- **Purpose**: Keep authentication alive by visiting booking page every 10 minutes
- **Usage**: `python scripts/auth/auth_keepalive.py`
- **Features**: Prevents session expiration, auto re-auth if needed
- **Production**: Should run continuously on VM

#### `test_auth_duration.py`
- **Purpose**: Test how long authentication lasts
- **Usage**: `python scripts/auth/test_auth_duration.py`
- **Features**: Tests every 2 minutes until expiration

#### `check_auth_expiry.py`
- **Purpose**: Analyze cookie expiry from browser state
- **Usage**: `python scripts/auth/check_auth_expiry.py`
- **Output**: Shows which cookies expire when

#### `test_auth_local.sh` / `test_auth_vm.sh`
- **Purpose**: Quick authentication tests
- **Usage**: `bash scripts/auth/test_auth_local.sh` or `test_auth_vm.sh`

#### `reauth_vm.sh`
- **Purpose**: Re-authenticate on VM
- **Usage**: `bash scripts/auth/reauth_vm.sh`
- **Note**: Requires local browser (opens browser on VM)

#### `start_auth_keepalive.sh`
- **Purpose**: Start keep-alive service on VM
- **Usage**: `bash scripts/auth/start_auth_keepalive.sh`

#### `start_auth_test.sh`
- **Purpose**: Start authentication duration test on VM
- **Usage**: `bash scripts/auth/start_auth_test.sh`

#### `check_auth_test_status.sh` / `check_auth_test_summary.sh`
- **Purpose**: Check status of authentication tests
- **Usage**: `bash scripts/auth/check_auth_test_status.sh`

#### `view_auth_keepalive_log.sh` / `view_auth_test_log.sh`
- **Purpose**: View authentication service logs
- **Usage**: `bash scripts/auth/view_auth_keepalive_log.sh`

#### `monitor_auth_test.sh`
- **Purpose**: Monitor authentication test in real-time
- **Usage**: `bash scripts/auth/monitor_auth_test.sh`

### Deployment Scripts (`scripts/deployment/`)

#### `deploy_to_gcp.sh`
- **Purpose**: Deploy bot to GCP VM
- **Usage**: `bash scripts/deployment/deploy_to_gcp.sh`
- **Features**: Creates archive, uploads to VM, extracts files

#### `setup_gcp_vm.sh`
- **Purpose**: Set up GCP VM with dependencies
- **Usage**: Run on VM: `bash scripts/deployment/setup_gcp_vm.sh`
- **Features**: Installs Python, Playwright, system dependencies

#### `setup_gcp_prerequisites.sh`
- **Purpose**: Set up GCP prerequisites (APIs, network, billing)
- **Usage**: `bash scripts/deployment/setup_gcp_prerequisites.sh`
- **Features**: Enables Compute Engine API, creates network, links billing

#### `diagnose_ssh.sh`
- **Purpose**: Diagnose SSH connectivity issues
- **Usage**: `bash scripts/deployment/diagnose_ssh.sh`

### Monitoring Scripts (`scripts/monitoring/`)

#### `view_vm_logs.sh`
- **Purpose**: View production booking logs from VM
- **Usage**: `bash scripts/monitoring/view_vm_logs.sh`
- **Output**: Last 50 lines of cron.log

#### `check_cron_jobs.sh`
- **Purpose**: Check cron job status and schedule
- **Usage**: `bash scripts/monitoring/check_cron_jobs.sh`
- **Output**: Lists all configured cron jobs with times

### Setup Scripts (`scripts/setup/`)

#### `setup_production.sh`
- **Purpose**: Complete production setup
- **Usage**: `bash scripts/setup/setup_production.sh`
- **Features**: Disables test mode, verifies auth, sets up cron

#### `setup_cron.sh`
- **Purpose**: Set up cron jobs for scheduled bookings
- **Usage**: `bash scripts/setup/setup_cron.sh` (on VM)
- **Features**: Reads booking times from config.yaml, creates cron jobs

#### `setup_launchd.sh`
- **Purpose**: Set up macOS LaunchAgent for local scheduling
- **Usage**: `bash scripts/setup/setup_launchd.sh` (local macOS)
- **Features**: Runs bot automatically on login (local development)

### Utility Scripts (`scripts/utils/`)

#### `check_auth.py`
- **Purpose**: Interactive authentication checker
- **Usage**: `python scripts/utils/check_auth.py`
- **Features**: Opens visible browser, allows manual login

#### `test_auth_selectors.py`
- **Purpose**: Test authentication selectors
- **Usage**: `python scripts/utils/test_auth_selectors.py`

#### `analyze_bookings_html.py`
- **Purpose**: Analyze bookings page HTML structure
- **Usage**: `python scripts/utils/analyze_bookings_html.py`
- **Features**: Helps understand page structure for debugging

#### `quick_check.sh`
- **Purpose**: Quick script to check authentication and show available courts
- **Usage**: `bash scripts/utils/quick_check.sh`

---

## Documentation Files (`docs/`)

### `INDEX.md`
- **Purpose**: Table of contents for all documentation
- **Contents**: Links to all docs with descriptions
- **Usage**: Start here to find what you need

### `QUICKSTART.md`
- **Purpose**: Fast setup guide
- **Contents**: Step-by-step setup instructions
- **Usage**: First-time setup

### `MODES.md`
- **Purpose**: Explains Auto Mode vs Manual Mode
- **Contents**: When to use each mode, how they work

### `GCP_DEPLOYMENT.md`
- **Purpose**: Complete GCP VM deployment guide
- **Contents**: VM creation, deployment, authentication, cron setup

### `PRODUCTION_SETUP.md`
- **Purpose**: Production setup checklist
- **Contents**: Steps to enable production bookings

### `AUTHENTICATION_INFO.md`
- **Purpose**: Authentication details and best practices
- **Contents**: Cookie expiry, session management, refresh strategies

### `KEEPALIVE_ANALYSIS.md`
- **Purpose**: Analysis of keep-alive service
- **Contents**: Pros/cons, costs, environmental impact

### `SCRIPTS_REFERENCE.md`
- **Purpose**: Complete reference for all scripts
- **Contents**: Detailed documentation for every script

### `QUICK_COMMANDS.md`
- **Purpose**: Quick command reference
- **Contents**: Most common commands in one place

### `SSH_TROUBLESHOOTING.md`
- **Purpose**: SSH connectivity troubleshooting
- **Contents**: Common issues and solutions

### `FILE_ORGANIZATION.md`
- **Purpose**: File organization guide
- **Contents**: Directory structure, naming conventions

### `FILE_REFERENCE.md` (this file)
- **Purpose**: Detailed explanation of every file
- **Contents**: What each file does, when to use it

---

## Data Files (`data/`)

### `data/browser_state/browser_state.json`
- **Purpose**: Saved browser authentication state
- **Contents**: Cookies, local storage, session data
- **Usage**: Automatically loaded to maintain authentication
- **Important**: Contains sensitive authentication data (excluded from git)

---

## Log Files (`logs/`)

### `logs/booking_bot.log`
- **Purpose**: Main log file for booking operations
- **Contents**: All booking attempts, errors, successes
- **Features**: Rotating log (max 10MB, keeps 5 backups)
- **Usage**: Monitor booking results, debug issues

---

## Virtual Environment (`venv/`)

### `venv/`
- **Purpose**: Python virtual environment
- **Contents**: Isolated Python packages
- **Usage**: Activated automatically by scripts
- **Note**: Excluded from git (recreated with `python -m venv venv`)

---

## File Relationships

### Core Flow
1. `main.py` → reads `config.yaml` via `config_loader.py`
2. `main.py` → uses `auth.py` for authentication
3. `main.py` → uses `booking_engine.py` for booking
4. `booking_engine.py` → uses `availability.py` to find slots
5. `manual_mode.py` → uses `bookings_manager.py` to view/cancel

### Scripts Flow
- **Deployment**: `setup_gcp_prerequisites.sh` → `setup_gcp_vm.sh` → `deploy_to_gcp.sh`
- **Production**: `setup_production.sh` → `setup_cron.sh` → cron runs `main.py`
- **Auth**: `test_authentication.py` → `auth_keepalive.py` (production)

---

## Key Files to Understand

### For Users
1. `config/config.yaml` - Configure booking behavior
2. `README.md` - Project overview
3. `docs/QUICKSTART.md` - Get started

### For Developers
1. `src/main.py` - Entry point and orchestration
2. `src/booking_engine.py` - Core booking logic
3. `src/auth.py` - Authentication handling
4. `src/config_loader.py` - Configuration management

### For Operations
1. `scripts/setup/setup_production.sh` - Production setup
2. `scripts/monitoring/view_vm_logs.sh` - View logs
3. `scripts/auth/auth_keepalive.py` - Keep auth alive
4. `scripts/monitoring/check_cron_jobs.sh` - Check schedule

---

## File Modification Guidelines

### Safe to Modify
- `config/config.yaml` - Configuration changes
- Documentation files (`docs/*.md`)
- Scripts in `scripts/` (except core deployment scripts)

### Be Careful Modifying
- `src/booking_engine.py` - Core booking logic
- `src/auth.py` - Authentication logic
- `scripts/setup/setup_cron.sh` - Cron configuration

### Don't Modify
- `venv/` - Virtual environment (recreated)
- `data/browser_state/browser_state.json` - Auto-generated
- `logs/*.log` - Auto-generated

---

## See Also

- **[FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)** - File structure and organization
- **[SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)** - Detailed script documentation
- **[INDEX.md](INDEX.md)** - Documentation index

