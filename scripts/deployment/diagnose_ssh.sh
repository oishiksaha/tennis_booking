#!/bin/bash
# Diagnose SSH connectivity issues with GCP VM

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

VM_NAME="tennis-bot-vm"
ZONE="us-central1-a"

echo "=========================================="
echo "SSH Connectivity Diagnostics"
echo "=========================================="
echo ""

# 1. Check VM status
echo "1. Checking VM status..."
STATUS=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(status)" 2>/dev/null)
if [ "$STATUS" = "RUNNING" ]; then
    echo "   ✓ VM is RUNNING"
else
    echo "   ✗ VM status: $STATUS"
    echo "   → Start VM: gcloud compute instances start $VM_NAME --zone=$ZONE"
    exit 1
fi
echo ""

# 2. Check firewall rules
echo "2. Checking firewall rules for SSH..."
SSH_RULE=$(gcloud compute firewall-rules list --filter="allowed.ports:22" --format="get(name)" | head -1)
if [ -n "$SSH_RULE" ]; then
    echo "   ✓ Found SSH firewall rule: $SSH_RULE"
else
    echo "   ✗ No SSH firewall rule found"
    echo "   → Create rule: gcloud compute firewall-rules create default-allow-ssh --allow tcp:22 --source-ranges 0.0.0.0/0"
fi
echo ""

# 3. Get VM IP
echo "3. Getting VM external IP..."
VM_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)" 2>/dev/null)
if [ -n "$VM_IP" ]; then
    echo "   ✓ VM IP: $VM_IP"
else
    echo "   ✗ Could not get VM IP"
    exit 1
fi
echo ""

# 4. Test network connectivity
echo "4. Testing network connectivity (ping)..."
if ping -c 2 -W 2 $VM_IP &>/dev/null; then
    echo "   ✓ VM is reachable via ping"
else
    echo "   ⚠️  VM not responding to ping (may be normal if ICMP is blocked)"
fi
echo ""

# 5. Test SSH port
echo "5. Testing SSH port (22)..."
if nc -z -w 3 $VM_IP 22 2>/dev/null; then
    echo "   ✓ SSH port 22 is open"
else
    echo "   ✗ SSH port 22 is not accessible"
    echo "   → Check firewall rules and VM network settings"
fi
echo ""

# 6. Test SSH with verbose output
echo "6. Testing SSH connection (verbose)..."
echo "   Attempting SSH connection..."
if gcloud compute ssh ubuntu@$VM_NAME --zone=$ZONE --command="echo 'SSH test successful'" 2>&1 | head -5; then
    echo "   ✓ SSH connection successful"
else
    echo "   ✗ SSH connection failed"
    echo ""
    echo "   Troubleshooting steps:"
    echo "   a) Try: gcloud compute ssh ubuntu@$VM_NAME --zone=$ZONE --troubleshoot"
    echo "   b) Check VM serial console: gcloud compute instances get-serial-port-output $VM_NAME --zone=$ZONE"
    echo "   c) Reset SSH keys: gcloud compute instances reset $VM_NAME --zone=$ZONE"
fi
echo ""

# 7. Check SSH keys
echo "7. Checking SSH keys..."
if [ -f ~/.ssh/google_compute_engine ]; then
    echo "   ✓ Found GCP SSH key: ~/.ssh/google_compute_engine"
else
    echo "   ⚠️  No GCP SSH key found (will be generated on first connection)"
fi
echo ""

# 8. Check gcloud configuration
echo "8. Checking gcloud configuration..."
PROJECT=$(gcloud config get-value project 2>/dev/null)
ACCOUNT=$(gcloud config get-value account 2>/dev/null)
echo "   Project: $PROJECT"
echo "   Account: $ACCOUNT"
echo ""

echo "=========================================="
echo "Diagnostics complete"
echo "=========================================="

