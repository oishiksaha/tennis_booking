#!/bin/bash
# Deploy tennis booking bot to GCP VM
# Run this from your local machine

set -e

# Configuration - UPDATE THESE VALUES
VM_NAME="${VM_NAME:-tennis-bot-vm}"
ZONE="${ZONE:-us-central1-a}"
VM_USER="${VM_USER:-ubuntu}"  # Default to ubuntu for Ubuntu VMs
PROJECT_DIR="tennis-booking-bot"

echo "=========================================="
echo "Deploying Tennis Booking Bot to GCP"
echo "=========================================="
echo "VM Name: $VM_NAME"
echo "Zone: $ZONE"
echo "User: $VM_USER"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check prerequisites
echo "Checking GCP prerequisites..."

# Enable Compute Engine API
gcloud services enable compute.googleapis.com --quiet 2>/dev/null || true

# Create default network if it doesn't exist
if ! gcloud compute networks describe default &> /dev/null; then
    echo "Creating default network..."
    gcloud compute networks create default --subnet-mode=auto
fi

# Check billing account
CURRENT_PROJECT=$(gcloud config get-value project)
BILLING_ACCOUNT=$(gcloud billing projects describe "$CURRENT_PROJECT" --format="value(billingAccountName)" 2>/dev/null || echo "")

if [ -z "$BILLING_ACCOUNT" ]; then
    echo "WARNING: No billing account linked to project."
    echo "Please link your educational billing account:"
    echo "  1. List accounts: gcloud billing accounts list"
    echo "  2. Link account: gcloud billing projects link $CURRENT_PROJECT --billing-account=BILLING_ACCOUNT_ID"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if VM exists
echo "Checking if VM exists..."
if ! gcloud compute instances describe "$VM_NAME" --zone="$ZONE" &> /dev/null; then
    echo "VM not found. Creating VM..."
    gcloud compute instances create "$VM_NAME" \
        --zone="$ZONE" \
        --machine-type=e2-micro \
        --image-family=ubuntu-2204-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=10GB \
        --tags=tennis-bot \
        --metadata=startup-script='#!/bin/bash
apt-get update
apt-get install -y python3 python3-pip python3-venv git'
    
    echo "Waiting for VM to be ready..."
    sleep 30
else
    echo "VM found."
fi

# Get VM IP
VM_IP=$(gcloud compute instances describe "$VM_NAME" --zone="$ZONE" --format="get(networkInterfaces[0].accessConfigs[0].natIP)")
echo "VM IP: $VM_IP"

# Upload project files
echo ""
echo "Uploading project files..."
echo "Creating archive (excluding venv, .git, etc.)..."

# Create a temporary directory for the archive
TEMP_DIR=$(mktemp -d)
ARCHIVE_FILE="$TEMP_DIR/tennis-bot-deploy.tar.gz"

# Create tar archive excluding unnecessary files
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv' \
    --exclude='data/browser_state/*.json' \
    --exclude='logs/*.log' \
    --exclude='.DS_Store' \
    --exclude='*.swp' \
    -czf "$ARCHIVE_FILE" \
    -C "$(pwd)" .

# Upload the archive
echo "Uploading archive..."
gcloud compute scp \
    --zone="$ZONE" \
    "$ARCHIVE_FILE" \
    "$VM_USER@$VM_NAME:~/tennis-bot-deploy.tar.gz"

# Extract on remote VM
echo "Extracting files on VM..."
gcloud compute ssh "$VM_USER@$VM_NAME" --zone="$ZONE" --command="
    mkdir -p ~/tennis-booking-bot
    cd ~/tennis-booking-bot
    tar -xzf ~/tennis-bot-deploy.tar.gz
    rm ~/tennis-bot-deploy.tar.gz
    mkdir -p data/browser_state logs
"

# Clean up local archive
rm -rf "$TEMP_DIR"

# Make scripts executable
echo ""
echo "Making scripts executable..."
gcloud compute ssh "$VM_USER@$VM_NAME" --zone="$ZONE" --command="
    chmod +x ~/tennis-booking-bot/scripts/*.sh 2>/dev/null || true
"

# Run setup script on VM
echo ""
echo "Running setup script on VM..."
gcloud compute ssh "$VM_USER@$VM_NAME" --zone="$ZONE" --command="
    cd ~/tennis-booking-bot && bash scripts/setup_gcp_vm.sh
"

echo ""
echo "=========================================="
echo "Deployment complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. SSH into VM: gcloud compute ssh $VM_USER@$VM_NAME --zone=$ZONE"
echo "2. Authenticate: cd ~/tennis-booking-bot && source venv/bin/activate && python src/main.py --authenticate"
echo "3. Set up cron: bash ~/tennis-booking-bot/scripts/setup_cron.sh"
echo ""
echo "Or copy your browser_state.json:"
echo "  gcloud compute scp data/browser_state/browser_state.json $VM_USER@$VM_NAME:~/tennis-booking-bot/data/browser_state/ --zone=$ZONE"
echo ""

