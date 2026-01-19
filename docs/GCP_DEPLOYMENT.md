# GCP Deployment Guide - Scheduled Execution

This guide walks you through deploying the tennis booking bot to GCP with scheduled execution at specific times.

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed on your local machine
   ```bash
   # Install gcloud CLI
   # Visit: https://cloud.google.com/sdk/docs/install
   ```

3. **GCP Project** created
   ```bash
   gcloud projects create YOUR_PROJECT_ID
   gcloud config set project YOUR_PROJECT_ID
   ```

## Quick Start (Automated)

### Step 1: Run Quick Start Script

From your local machine:

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run quick start (creates VM and deploys)
bash scripts/gcp_quick_start.sh
```

### Step 2: Authenticate

**Option A: Copy Existing Browser State (Recommended)**

If you've already authenticated locally:

```bash
# Copy browser state from local to VM
gcloud compute scp data/browser_state/browser_state.json \
  ubuntu@tennis-bot-vm:~/tennis-booking-bot/data/browser_state/ \
  --zone=us-central1-a
```

**Option B: Authenticate on VM**

```bash
# SSH into VM
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a

# Authenticate
cd ~/tennis-booking-bot
source venv/bin/activate
python src/main.py --authenticate
```

### Step 3: Set Up Cron Jobs

```bash
# SSH into VM
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a

# Run cron setup
bash ~/tennis-booking-bot/scripts/setup_cron.sh
```

### Step 4: Test

```bash
# Test the bot manually
cd ~/tennis-booking-bot
source venv/bin/activate
python src/main.py --headless
```

## Manual Setup

### Step 1: Create VM

```bash
gcloud compute instances create tennis-bot-vm \
  --zone=us-central1-a \
  --machine-type=e2-micro \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=10GB \
  --tags=tennis-bot
```

### Step 2: Deploy Bot

```bash
# From local machine
bash scripts/deploy_to_gcp.sh
```

### Step 3: Set Up VM

```bash
# SSH into VM
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a

# Run setup
cd ~/tennis-booking-bot
bash scripts/setup_gcp_vm.sh
```

### Step 4: Authenticate

See Step 2 in Quick Start above.

### Step 5: Set Up Cron

```bash
bash ~/tennis-booking-bot/scripts/setup_cron.sh
```

## Browser State Persistence

The bot automatically saves your authentication state to:
```
~/tennis-booking-bot/data/browser_state/browser_state.json
```

This file persists between runs, so you'll stay logged in. The bot will:
1. Load saved state on startup
2. Check if still authenticated
3. Re-authenticate only if needed
4. Save state after each run

## Scheduled Execution Times

The cron jobs are set to run 5 minutes before each booking window:

- **6:55 AM** - Before 7 AM booking window
- **7:55 AM** - Before 8 AM booking window  
- **4:55 PM** - Before 5 PM booking window
- **5:55 PM** - Before 6 PM booking window
- **6:55 PM** - Before 7 PM booking window

To modify times, edit cron:
```bash
crontab -e
```

## Monitoring

### View Logs

```bash
# SSH into VM
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a

# View cron logs
tail -f ~/tennis-booking-bot/logs/cron.log

# View service logs (if using systemd)
journalctl -u tennis-booking-bot -f
```

### Check Cron Jobs

```bash
# List cron jobs
crontab -l

# Check cron service
sudo systemctl status cron
```

### Test Manually

```bash
cd ~/tennis-booking-bot
source venv/bin/activate
python src/main.py --headless
```

## Cost Management

### Current Setup (Always-On VM)
- **Cost**: ~$6-8/month (e2-micro running 24/7)
- **Pros**: Simple, reliable, always ready
- **Cons**: Higher cost than scheduled start/stop

### Cost Optimization (Advanced)

To reduce costs further, you can set up VM start/stop scheduling:

1. Use Cloud Scheduler to start VM before booking times
2. Run bot via startup script
3. Stop VM after booking completes

This can reduce costs to ~$1-2/month but requires more setup.

## Troubleshooting

### Authentication Issues

```bash
# Check browser state file exists
ls -la ~/tennis-booking-bot/data/browser_state/

# Re-authenticate if needed
cd ~/tennis-booking-bot
source venv/bin/activate
python src/main.py --authenticate
```

### Cron Not Running

```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog

# Verify timezone
timedatectl
```

### Bot Not Working

```bash
# Check Python environment
cd ~/tennis-booking-bot
source venv/bin/activate
which python

# Test manually
python src/main.py --headless

# Check logs
tail -f logs/cron.log
```

### VM Issues

```bash
# Check VM status
gcloud compute instances describe tennis-bot-vm --zone=us-central1-a

# Restart VM
gcloud compute instances reset tennis-bot-vm --zone=us-central1-a
```

## Maintenance

### Update Bot Code

```bash
# From local machine
bash scripts/deploy_to_gcp.sh
```

### Update Dependencies

```bash
# SSH into VM
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a

cd ~/tennis-booking-bot
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Backup Browser State

```bash
# Download browser state for backup
gcloud compute scp ubuntu@tennis-bot-vm:~/tennis-booking-bot/data/browser_state/browser_state.json \
  ./data/browser_state/browser_state.json.backup \
  --zone=us-central1-a
```

## Security Notes

1. **Firewall**: The VM only needs outbound internet access (default)
2. **SSH Keys**: Use SSH keys, not passwords
3. **Browser State**: Keep `browser_state.json` secure (contains session cookies)
4. **Credentials**: Never commit `.env` or `browser_state.json` to git

## Support

For issues:
1. Check logs: `tail -f ~/tennis-booking-bot/logs/cron.log`
2. Test manually: `python src/main.py --headless`
3. Check cron: `crontab -l` and `grep CRON /var/log/syslog`

