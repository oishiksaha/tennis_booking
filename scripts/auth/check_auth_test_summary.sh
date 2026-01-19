#!/bin/bash
# Check authentication test summary with detailed timing information

export CLOUDSDK_PYTHON=/opt/homebrew/bin/python3

echo "=========================================="
echo "Authentication Test Summary"
echo "=========================================="
echo ""

gcloud compute ssh ubuntu@tennis-bot-vm --zone=us-central1-a << 'ENDSSH'
cd ~/tennis-booking-bot

echo "Current time: $(date)"
echo ""

if [ ! -f /tmp/auth_duration_test.log ]; then
    echo "❌ Log file not found"
    exit 1
fi

echo "=== Test Status ==="
if pgrep -f test_auth_duration.py > /dev/null; then
    echo "✓ Test is RUNNING"
    PID=$(pgrep -f test_auth_duration.py | head -1)
    echo "  Process ID: $PID"
else
    echo "✗ Test is NOT running (may have completed or stopped)"
fi

echo ""
echo "=== Test Summary ==="

# Extract start time
START_TIME=$(grep "Authentication Duration Test Started:" /tmp/auth_duration_test.log | tail -1 | sed 's/.*Started: //' | sed 's/ .*//')
if [ -n "$START_TIME" ]; then
    echo "Start time: $START_TIME"
fi

# Count tests
TOTAL_TESTS=$(grep -c "^\[.*\] Test #" /tmp/auth_duration_test.log 2>/dev/null || echo "0")
SUCCESS_TESTS=$(grep -c "✓ SUCCESS" /tmp/auth_duration_test.log 2>/dev/null || echo "0")
FAILED_TESTS=$(grep -c "✗ FAILED" /tmp/auth_duration_test.log 2>/dev/null || echo "0")

echo "Total tests: $TOTAL_TESTS"
echo "Successful: $SUCCESS_TESTS"
echo "Failed: $FAILED_TESTS"

# Check if expired
if grep -q "AUTHENTICATION EXPIRED" /tmp/auth_duration_test.log; then
    echo ""
    echo "⚠️  AUTHENTICATION EXPIRED"
    EXPIRED_LINE=$(grep "AUTHENTICATION EXPIRED" /tmp/auth_duration_test.log | tail -1)
    echo "$EXPIRED_LINE"
    
    # Get elapsed time until expiry
    ELAPSED_LINE=$(grep -A 3 "AUTHENTICATION EXPIRED" /tmp/auth_duration_test.log | grep "Elapsed time:" | tail -1)
    if [ -n "$ELAPSED_LINE" ]; then
        echo "$ELAPSED_LINE"
    fi
    
    TIME_TO_FAILURE=$(grep -A 4 "AUTHENTICATION EXPIRED" /tmp/auth_duration_test.log | grep "Time until first failure:" | tail -1)
    if [ -n "$TIME_TO_FAILURE" ]; then
        echo "$TIME_TO_FAILURE"
    fi
else
    echo ""
    echo "✓ Authentication still valid (test may still be running)"
fi

echo ""
echo "=== Last 5 Test Results ==="
tail -5 /tmp/auth_duration_test.log | grep "^\[" || echo "No test results yet"

echo ""
echo "=== Full Log Location ==="
echo "/tmp/auth_duration_test.log"
echo ""
echo "To view full log: tail -50 /tmp/auth_duration_test.log"
ENDSSH

