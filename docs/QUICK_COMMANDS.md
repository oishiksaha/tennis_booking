# Quick Command Reference

**Last Updated**: January 18, 2026

Quick reference for common commands. See [SCRIPTS_REFERENCE.md](SCRIPTS_REFERENCE.md) for detailed documentation.

## 🔍 Check Status

**Check cron jobs:**
```bash
bash scripts/monitoring/check_cron_jobs.sh
```

**Check authentication:**
```bash
bash scripts/auth/test_auth_vm.sh
```

**View production logs:**
```bash
bash scripts/monitoring/view_vm_logs.sh
```

## 🚀 Production

**Set up production (disable test mode, verify auth, set up cron):**
```bash
bash scripts/setup/setup_production.sh
```

**Set up cron jobs only:**
```bash
# On VM
bash scripts/setup/setup_cron.sh
```

## 🔐 Authentication

**Test authentication locally:**
```bash
bash scripts/auth/test_auth_local.sh
```

**Test authentication on VM:**
```bash
bash scripts/auth/test_auth_vm.sh
```

**Re-authenticate on VM:**
```bash
bash scripts/auth/reauth_vm.sh
```

**Start keep-alive service:**
```bash
bash scripts/auth/start_auth_keepalive.sh
```

## 📦 Deployment

**Deploy to GCP:**
```bash
bash scripts/deployment/deploy_to_gcp.sh
```

## 📝 Notes

- All scripts assume you're in the project root directory
- VM scripts use `gcloud compute ssh` automatically
- Most scripts handle authentication and setup automatically

