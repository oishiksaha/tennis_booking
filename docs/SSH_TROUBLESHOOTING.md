# SSH Troubleshooting Guide

## Quick Diagnostics

Run the diagnostic script:
```bash
bash scripts/diagnose_ssh.sh
```

## Common Issues and Solutions

### 1. Intermittent Timeouts

**Symptoms:** Commands hang or timeout after a few seconds

**Solutions:**
- Use simpler commands (avoid complex pipes/redirects)
- Use the `start_vm_test_simple.sh` script (uses here-document)
- Break complex commands into multiple simpler SSH calls
- Add `--ssh-flag="-o ConnectTimeout=10"` to gcloud commands

### 2. Connection Refused

**Symptoms:** `ERROR: (gcloud.compute.ssh) [/usr/bin/ssh] exited with return code [255]`

**Solutions:**
```bash
# Check VM status
gcloud compute instances describe tennis-bot-vm --zone=us-central1-a --format="get(status)"

# If not RUNNING, start it
gcloud compute instances start tennis-bot-vm --zone=us-central1-a

# Reset SSH if needed
gcloud compute instances reset tennis-bot-vm --zone=us-central1-a
```

### 3. Firewall Issues

**Symptoms:** Can't connect to port 22

**Solutions:**
```bash
# Check firewall rules
gcloud compute firewall-rules list --filter="allowed.ports:22"

# Create SSH rule if missing
gcloud compute firewall-rules create default-allow-ssh \
    --allow tcp:22 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow SSH from anywhere"
```

### 4. SSH Key Issues

**Symptoms:** Authentication failures

**Solutions:**
```bash
# Generate new SSH key
ssh-keygen -t rsa -f ~/.ssh/google_compute_engine -C ""

# Or let gcloud handle it automatically (it will prompt)
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a
```

### 5. Complex Command Timeouts

**Symptoms:** Long commands with pipes/redirects hang

**Solutions:**

**Option A: Use here-document (recommended)**
```bash
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot
source venv/bin/activate
python scripts/run_test_at_12pm.py
ENDSSH
```

**Option B: Use separate SSH calls**
```bash
# Step 1: Start the script
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a \
    --command="cd ~/tennis-booking-bot && nohup python script.py > log.txt 2>&1 &"

# Step 2: Check status separately
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a \
    --command="ps aux | grep script.py"
```

**Option C: Use the helper scripts**
```bash
bash scripts/start_vm_test_simple.sh
bash scripts/view_vm_12pm_log.sh
```

## Best Practices

1. **Keep commands simple**: Avoid complex pipes and redirects in single SSH commands
2. **Use helper scripts**: The `start_vm_test_simple.sh` script handles complexity
3. **Check VM resources**: If VM is overloaded, commands may timeout
4. **Use nohup for long-running tasks**: Prevents disconnection issues
5. **Monitor with separate commands**: Check logs/status with separate SSH calls

## Testing SSH

Simple test:
```bash
gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a --command="echo 'SSH works'"
```

If this works, SSH is fine - the issue is with complex command chaining.

## Getting VM Console Access

If SSH completely fails, use serial console:
```bash
gcloud compute instances get-serial-port-output tennis-bot-vm --zone=us-central1-a
```

## Network Troubleshooting

Check VM IP and connectivity:
```bash
# Get VM IP
gcloud compute instances describe tennis-bot-vm --zone=us-central1-a \
    --format="get(networkInterfaces[0].accessConfigs[0].natIP)"

# Test SSH port (if you have nc/netcat)
nc -zv <VM_IP> 22
```

