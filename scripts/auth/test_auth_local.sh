#!/bin/bash
# Quick script to test authentication locally

cd "$(dirname "$0")/.."
source venv/bin/activate
python scripts/test_authentication.py

