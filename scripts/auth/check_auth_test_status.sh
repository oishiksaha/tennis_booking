#!/bin/bash
# Check status of authentication duration test

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "Authentication Duration Test Status"
echo "=================================="
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
echo "1. Process status:"
ps aux | grep test_auth_duration.py | grep -v grep || echo "   Test is not running"

echo ""
echo "2. Latest log entries (last 20 lines):"
if [ -f /tmp/auth_duration_test.log ]; then
    tail -20 /tmp/auth_duration_test.log
else
    echo "   Log file not found yet"
fi

echo ""
echo "3. Test summary:"
if [ -f /tmp/auth_duration_test.log ]; then
    TOTAL_TESTS=$(grep -c "Test #" /tmp/auth_duration_test.log 2>/dev/null | head -1 || echo "0")
    SUCCESS_TESTS=$(grep -c "SUCCESS" /tmp/auth_duration_test.log 2>/dev/null | head -1 || echo "0")
    FAILED_TESTS=$(grep -c "FAILED" /tmp/auth_duration_test.log 2>/dev/null | head -1 || echo "0")
    EXPIRED=$(grep -c "AUTHENTICATION EXPIRED" /tmp/auth_duration_test.log 2>/dev/null | head -1 || echo "0")
    
    # Handle empty results
    TOTAL_TESTS=${TOTAL_TESTS:-0}
    SUCCESS_TESTS=${SUCCESS_TESTS:-0}
    FAILED_TESTS=${FAILED_TESTS:-0}
    EXPIRED=${EXPIRED:-0}
    
    echo "   Total tests: $TOTAL_TESTS"
    echo "   Successful: $SUCCESS_TESTS"
    echo "   Failed: $FAILED_TESTS"
    if [ "$EXPIRED" -gt 0 ] 2>/dev/null; then
        echo "   ⚠️  Authentication has expired!"
        grep "AUTHENTICATION EXPIRED" /tmp/auth_duration_test.log 2>/dev/null | tail -1
    fi
else
    echo "   No log file found"
fi
ENDSSH

