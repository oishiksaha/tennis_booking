# Tennis Booking Bot - Documentation Index

**Last Updated**: January 18, 2026

This index provides quick access to all important documentation for the Tennis Booking Bot project.

## 📚 Quick Navigation

### Getting Started
- **[README.md](../README.md)** - Main project overview and features
- **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
- **[MODES.md](MODES.md)** - Understanding Auto Mode vs Manual Mode

### Deployment & Production
- **[GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)** - Complete GCP VM deployment guide
- **[PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)** - Production setup checklist and weekly booking configuration
- **[SSH_TROUBLESHOOTING.md](SSH_TROUBLESHOOTING.md)** - Troubleshooting SSH connectivity issues

### Authentication
- **[AUTHENTICATION_INFO.md](AUTHENTICATION_INFO.md)** - Authentication behavior, cookie expiry, and best practices

### Technical Details
- **[PROFILE_BUTTON_FIX.md](PROFILE_BUTTON_FIX.md)** - Technical fix for profile button visibility detection
- **[SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md)** - Complete reference guide for all scripts
- **[QUICK_COMMANDS.md](QUICK_COMMANDS.md)** - Quick command reference
- **[NOTIFICATIONS_SETUP.md](NOTIFICATIONS_SETUP.md)** - Email/SMS notification setup
- **[IMPROVEMENTS_RECOMMENDED.md](IMPROVEMENTS_RECOMMENDED.md)** - Recommended improvements and best practices

## 📁 Complete File Organization

- **[FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)** - File structure and organization guide
- **[FILE_REFERENCE.md](FILE_REFERENCE.md)** - **Detailed explanation of every file** (what each file does, when to use it)

## 📖 Documentation Details

### Getting Started

#### README.md
- **Location**: Root directory
- **Purpose**: Main project documentation
- **Contents**:
  - Project overview
  - Features list
  - Basic setup instructions
  - Quick usage examples
- **When to read**: First time exploring the project

#### QUICKSTART.md
- **Location**: `docs/`
- **Purpose**: Fast setup guide
- **Contents**:
  - Step-by-step local setup
  - First-time authentication
  - Running the bot
  - Basic configuration
- **When to read**: Setting up for the first time

#### MODES.md
- **Location**: `docs/`
- **Purpose**: Understand operating modes
- **Contents**:
  - Auto Mode vs Manual Mode comparison
  - When to use each mode
  - Configuration differences
  - Switching between modes
- **When to read**: Understanding how the bot works

### Deployment & Production

#### GCP_DEPLOYMENT.md
- **Location**: `docs/`
- **Purpose**: Complete GCP deployment guide
- **Contents**:
  - Prerequisites and setup
  - VM creation
  - Project deployment
  - Authentication setup on VM
  - Cron job configuration
  - Monitoring and maintenance
- **When to read**: Deploying to GCP for production use

#### PRODUCTION_SETUP.md
- **Location**: `docs/`
- **Purpose**: Production readiness checklist
- **Contents**:
  - Pre-flight checklist
  - Test mode configuration
  - Authentication verification
  - Cron job setup
  - Log monitoring
  - Weekly booking schedule
  - Troubleshooting guide
- **When to read**: Before enabling production bookings

#### SSH_TROUBLESHOOTING.md
- **Location**: `docs/`
- **Purpose**: Fix SSH connectivity issues
- **Contents**:
  - Common SSH errors
  - Diagnostic steps
  - Solutions and workarounds
  - Network troubleshooting
- **When to read**: When having trouble connecting to VM

### Authentication

#### AUTHENTICATION_INFO.md
- **Location**: `docs/`
- **Purpose**: Authentication behavior and management
- **Contents**:
  - Session cookie behavior
  - Authentication duration
  - Browser state management
  - Refresh strategies
  - Best practices
- **When to read**: Understanding authentication lifecycle

### Technical Details

#### PROFILE_BUTTON_FIX.md
- **Location**: `docs/`
- **Purpose**: Technical documentation of a fix
- **Contents**:
  - Issue description
  - Root cause analysis
  - Solution implementation
  - Technical details
- **When to read**: Understanding profile button detection logic

## 🔍 Finding What You Need

### "I want to set up the bot for the first time"
→ Start with [README.md](../README.md), then [QUICKSTART.md](QUICKSTART.md)

### "I want to deploy to GCP"
→ Read [GCP_DEPLOYMENT.md](GCP_DEPLOYMENT.md)

### "I want to enable production weekly bookings"
→ Read [PRODUCTION_SETUP.md](PRODUCTION_SETUP.md)

### "I'm having authentication issues"
→ Read [AUTHENTICATION_INFO.md](AUTHENTICATION_INFO.md)

### "I can't connect to my VM"
→ Read [SSH_TROUBLESHOOTING.md](SSH_TROUBLESHOOTING.md)

### "I want to check cron job schedule"
→ Run `bash scripts/monitoring/check_cron_jobs.sh`
→ See [QUICK_COMMANDS.md](QUICK_COMMANDS.md) for quick reference

### "I want to understand how the bot works"
→ Read [MODES.md](MODES.md)

## 📁 File Organization

```
tennis-booking-bot/
├── README.md                    # Main project readme (root)
├── requirements.txt             # Python dependencies
├── run.sh                       # Main entry point script
├── config/                      # Configuration files
├── src/                         # Source code
├── scripts/                     # Scripts and utilities
│   └── utils/                  # Utility scripts
├── docs/                        # All documentation
│   ├── INDEX.md                # This file - table of contents
│   ├── QUICKSTART.md           # Quick setup guide
│   ├── MODES.md                # Operating modes explanation
│   ├── GCP_DEPLOYMENT.md       # GCP deployment guide
│   ├── PRODUCTION_SETUP.md     # Production setup guide
│   ├── AUTHENTICATION_INFO.md  # Authentication details
│   ├── SSH_TROUBLESHOOTING.md  # SSH troubleshooting
│   ├── PROFILE_BUTTON_FIX.md   # Technical fix documentation
│   └── FILE_ORGANIZATION.md    # File organization guide
├── data/                        # Runtime data
└── logs/                        # Log files
```

See **[FILE_ORGANIZATION.md](FILE_ORGANIZATION.md)** for detailed file organization guide.

## 🔄 Maintenance

When adding new documentation:
1. Add entry to this INDEX.md
2. Place file in `docs/` directory
3. Update "Last Updated" date at top
4. Add to appropriate section

When removing documentation:
1. Remove from INDEX.md
2. Delete or archive the file
3. Update this index

## 📝 Notes

- All important documentation is in the `docs/` folder
- Root `README.md` provides quick overview
- Technical fixes and temporary docs are archived in `docs/`
- Redundant or outdated files have been removed

