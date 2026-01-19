# Scripts Directory

This directory contains utility scripts organized by category.

## Directory Structure

```
scripts/
├── auth/              # Authentication-related scripts
├── deployment/        # GCP deployment scripts
├── monitoring/        # Log viewing and monitoring scripts
├── setup/            # Setup and configuration scripts
└── utils/            # Utility scripts and helpers
```

## Quick Reference

### Authentication (`auth/`)
- `test_authentication.py` - Test authentication status
- `auth_keepalive.py` - Keep authentication alive (production)
- `test_auth_duration.py` - Test how long authentication lasts
- `start_auth_keepalive.sh` - Start keep-alive service on VM
- `test_auth_local.sh` / `test_auth_vm.sh` - Quick auth tests

### Deployment (`deployment/`)
- `deploy_to_gcp.sh` - Deploy bot to GCP VM
- `setup_gcp_vm.sh` - Set up GCP VM with dependencies
- `setup_gcp_prerequisites.sh` - Set up GCP prerequisites

### Monitoring (`monitoring/`)
- `view_vm_logs.sh` - View production booking logs
- `check_cron_jobs.sh` - Check cron job status

### Setup (`setup/`)
- `setup_production.sh` - Complete production setup
- `setup_cron.sh` - Set up cron jobs for scheduled bookings
- `setup_launchd.sh` - Set up macOS launchd (local)

### Utilities (`utils/`)
- Helper scripts for development and debugging

## Usage

Most scripts can be run from the project root:

```bash
# Authentication
bash scripts/auth/test_auth_vm.sh

# Deployment
bash scripts/deployment/deploy_to_gcp.sh

# Monitoring
bash scripts/monitoring/view_vm_logs.sh

# Setup
bash scripts/setup/setup_production.sh
```

For detailed documentation, see [docs/SCRIPTS_REFERENCE.md](../docs/SCRIPTS_REFERENCE.md).

