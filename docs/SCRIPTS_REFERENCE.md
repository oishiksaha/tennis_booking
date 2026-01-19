# Scripts Reference Guide

**Last Updated**: January 18, 2026

This document provides a reference for all scripts in the `scripts/` directory.

## Directory Structure

Scripts are organized into categories:

```
scripts/
├── auth/              # Authentication-related scripts
├── deployment/        # GCP deployment scripts
├── monitoring/        # Log viewing and monitoring scripts
├── setup/            # Setup and configuration scripts
└── utils/            # Utility scripts and helpers
```

## Script Categories

### 🔧 Setup Scripts (`setup/`)

**`setup_cron.sh`**
- Sets up cron jobs for automated weekly bookings
- Reads booking times from `config.yaml`
- Creates cron jobs that run at exact booking times
- **Usage**: `bash scripts/setup/setup_cron.sh` (on VM)

**`setup_production.sh`**
- Complete production setup script
- Disables test mode
- Verifies authentication
- Sets up cron jobs
- **Usage**: `bash scripts/setup/setup_production.sh`

**`setup_launchd.sh`**
- Set up macOS launchd for local scheduling
- **Usage**: `bash scripts/setup/setup_launchd.sh` (local macOS)

### 🔐 Authentication Scripts (`auth/`)

**`test_authentication.py`**
- Automated authentication test
- Works in headless mode
- Returns exit code (0 = success, 1 = failure)
- **Usage**: `python scripts/auth/test_authentication.py`

**`test_auth_local.sh`**
- Quick local authentication test
- **Usage**: `bash scripts/auth/test_auth_local.sh`

**`test_auth_vm.sh`**
- Quick VM authentication test
- **Usage**: `bash scripts/auth/test_auth_vm.sh`

**`test_auth_duration.py`**
- Test how long authentication lasts
- Checks every 2 minutes until expiry (for precise timing)
- **Usage**: `python scripts/auth/test_auth_duration.py`

**`start_auth_test.sh`**
- Start authentication duration test on VM (every 2 minutes)
- **Usage**: `bash scripts/auth/start_auth_test.sh`

**`auth_keepalive.py`**
- Keep authentication alive by visiting booking page every 10 minutes
- Prevents session expiration due to inactivity
- Saves refreshed browser state automatically
- **Usage**: `python scripts/auth/auth_keepalive.py`

**`start_auth_keepalive.sh`**
- Start authentication keep-alive service on VM
- **Usage**: `bash scripts/auth/start_auth_keepalive.sh`

**`view_auth_keepalive_log.sh`**
- View authentication keep-alive service log
- **Usage**: `bash scripts/auth/view_auth_keepalive_log.sh`

**`check_auth_test_status.sh`**
- Check status of authentication test
- **Usage**: `bash scripts/auth/check_auth_test_status.sh`

**`view_auth_test_log.sh`**
- View authentication test log
- **Usage**: `bash scripts/auth/view_auth_test_log.sh`

**`check_auth_expiry.py`**
- Check authentication cookie expiry
- **Usage**: `python scripts/auth/check_auth_expiry.py`

**`reauth_vm.sh`**
- Re-authenticate on VM
- **Usage**: `bash scripts/auth/reauth_vm.sh`

### 🚀 Deployment Scripts

**`deploy_to_gcp.sh`**
- Deploy bot to GCP VM
- Uploads project files
- **Usage**: `bash scripts/deploy_to_gcp.sh`

**`setup_gcp_vm.sh`**
- Set up GCP VM with dependencies
- Installs Python, Playwright, etc.
- **Usage**: Run on new GCP VM

**`setup_gcp_prerequisites.sh`**
- Set up GCP prerequisites
- Enables APIs, creates network, links billing
- **Usage**: Run before creating VM

### 🛠️ Utility Scripts (`utils/`)

**`check_auth.py`**
- Interactive authentication checker
- Opens visible browser
- Allows manual login
- **Usage**: `python scripts/utils/check_auth.py`

**`test_auth_selectors.py`**
- Test authentication selectors
- **Usage**: `python scripts/utils/test_auth_selectors.py`

**`analyze_bookings_html.py`**
- Analyze bookings page HTML
- **Usage**: `python scripts/utils/analyze_bookings_html.py`

**`quick_check.sh`**
- Quick script to check authentication and show available courts
- **Usage**: `bash scripts/utils/quick_check.sh`
- **Usage**: `python scripts/utils/analyze_bookings_html.py`

**`quick_check.sh`**
- Quick check script
- **Usage**: `bash scripts/utils/quick_check.sh`

### 🔍 Troubleshooting Scripts (`deployment/`)

**`diagnose_ssh.sh`**
- Diagnose SSH connectivity issues
- **Usage**: `bash scripts/deployment/diagnose_ssh.sh`

### 💻 Local Development Scripts (`setup/`)

**`setup_launchd.sh`**
- Set up macOS LaunchAgent
- Runs bot automatically on login
- **Usage**: `bash scripts/setup/setup_launchd.sh`
- **Usage**: `bash scripts/setup_launchd.sh`

## Script Organization

```
scripts/
├── utils/                      # Utility scripts
│   ├── check_auth.py
│   ├── test_auth_selectors.py
│   ├── analyze_bookings_html.py
│   └── quick_check.sh
│
├── Production Scripts
│   ├── setup_cron.sh
│   ├── setup_production.sh
│   └── view_vm_logs.sh
│
├── Authentication Scripts
│   ├── test_authentication.py
│   ├── test_auth_*.sh
│   ├── check_auth_expiry.py
│   └── reauth_vm.sh
│
├── Deployment Scripts
│   ├── deploy_to_gcp.sh
│   ├── setup_gcp_vm.sh
│   └── setup_gcp_prerequisites.sh
│
└── Other Scripts
    ├── debug_profile_button.py
    ├── diagnose_ssh.sh
    └── setup_launchd.sh
```

## Quick Reference

### Most Common Tasks

**Set up production:**
```bash
bash scripts/setup/setup_production.sh
```

**Test authentication:**
```bash
bash scripts/auth/test_auth_vm.sh
```

**View logs:**
```bash
bash scripts/monitoring/view_vm_logs.sh
```

**Check cron jobs:**
```bash
bash scripts/monitoring/check_cron_jobs.sh
```

**Deploy to GCP:**
```bash
bash scripts/deployment/deploy_to_gcp.sh
```

**Re-authenticate:**
```bash
bash scripts/auth/reauth_vm.sh
```

**Start keep-alive service:**
```bash
bash scripts/auth/start_auth_keepalive.sh
```

## Notes

- All scripts assume they're run from the project root
- Scripts in `utils/` are for development/debugging
- Production scripts are for VM deployment
- Authentication scripts work in headless mode

