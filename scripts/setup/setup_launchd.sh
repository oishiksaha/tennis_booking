#!/bin/bash
# Setup LaunchAgent for macOS to run tennis booking bot automatically
# This will start the bot when you log in and keep it running

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLIST_NAME="com.tennis.booking.bot"
PLIST_FILE="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"

echo "Setting up LaunchAgent for Tennis Booking Bot..."
echo ""

# Create LaunchAgents directory if it doesn't exist
mkdir -p "$HOME/Library/LaunchAgents"

# Create plist file
cat > "$PLIST_FILE" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${SCRIPT_DIR}/venv/bin/python</string>
        <string>-m</string>
        <string>src.main</string>
        <string>--schedule</string>
        <string>--headless</string>
    </array>
    <key>WorkingDirectory</key>
    <string>${SCRIPT_DIR}</string>
    <key>StandardOutPath</key>
    <string>${SCRIPT_DIR}/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>${SCRIPT_DIR}/logs/launchd.error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>
        <string>${SCRIPT_DIR}</string>
    </dict>
</dict>
</plist>
EOF

echo "Created LaunchAgent plist at: $PLIST_FILE"
echo ""
echo "To start the service:"
echo "  launchctl load $PLIST_FILE"
echo ""
echo "To stop the service:"
echo "  launchctl unload $PLIST_FILE"
echo ""
echo "To check status:"
echo "  launchctl list | grep ${PLIST_NAME}"
echo ""
echo "To view logs:"
echo "  tail -f ${SCRIPT_DIR}/logs/launchd.log"
echo ""

