#!/bin/bash
# Setup GCP prerequisites: network and billing account
# Run this before deploying the bot

set -e

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

CURRENT_PROJECT=$(gcloud config get-value project)
echo "Current project: $CURRENT_PROJECT"
echo ""

# Enable Compute Engine API
echo "Enabling Compute Engine API..."
gcloud services enable compute.googleapis.com --quiet

# Create default network if it doesn't exist
echo "Checking for default network..."
if ! gcloud compute networks describe default &> /dev/null; then
    echo "Creating default network..."
    gcloud compute networks create default --subnet-mode=auto
    echo "Default network created."
else
    echo "Default network already exists."
fi

# Check and link billing account
echo ""
echo "Checking billing account..."
BILLING_ACCOUNT=$(gcloud billing projects describe "$CURRENT_PROJECT" --format="value(billingAccountName)" 2>/dev/null || echo "")

if [ -z "$BILLING_ACCOUNT" ]; then
    echo "No billing account linked."
    echo ""
    echo "Available billing accounts:"
    gcloud billing accounts list --format="table(name,displayName,open)"
    echo ""
    
    # Try to find educational account
    EDUCATIONAL_ACCOUNT=$(gcloud billing accounts list --format="value(name)" --filter="open=true" | head -1)
    
    if [ -n "$EDUCATIONAL_ACCOUNT" ]; then
        echo "Found billing account: $EDUCATIONAL_ACCOUNT"
        read -p "Link this account to project? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gcloud billing projects link "$CURRENT_PROJECT" --billing-account="$EDUCATIONAL_ACCOUNT"
            echo "Billing account linked successfully!"
        else
            echo "Skipping billing account link."
            echo "To link manually, run:"
            echo "  gcloud billing projects link $CURRENT_PROJECT --billing-account=BILLING_ACCOUNT_ID"
        fi
    else
        echo "No open billing accounts found."
        echo "Please link a billing account manually:"
        echo "  gcloud billing accounts list"
        echo "  gcloud billing projects link $CURRENT_PROJECT --billing-account=BILLING_ACCOUNT_ID"
    fi
else
    echo "Billing account already linked: $BILLING_ACCOUNT"
    BILLING_INFO=$(gcloud billing accounts describe "$BILLING_ACCOUNT" --format="value(displayName)" 2>/dev/null || echo "Unknown")
    echo "Account name: $BILLING_INFO"
fi

echo ""
echo "=========================================="
echo "Prerequisites check complete!"
echo "=========================================="

