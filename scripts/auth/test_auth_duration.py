#!/usr/bin/env python3
"""Test authentication every 2 minutes and log results to track exactly when it expires."""
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from src.config_loader import Config
from src.auth import AuthHandler

def test_authentication():
    """Test if authentication is still valid. Returns (success: bool, message: str)."""
    config = Config()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            try:
                auth_handler = AuthHandler(config)
                context = auth_handler.create_browser_context(browser, headless=True)
                page = context.new_page()
                
                # Test authentication
                result = auth_handler.ensure_authenticated(page, context, headless=True)
                
                browser.close()
                
                if result:
                    return True, "Authentication valid"
                else:
                    return False, "Authentication failed - browser state expired or invalid"
                    
            except Exception as e:
                browser.close()
                return False, f"Error: {str(e)}"
                
    except Exception as e:
        return False, f"Critical error: {str(e)}"

def main():
    """Main loop - test authentication every 2 minutes."""
    log_file = Path("/tmp/auth_duration_test.log")
    test_interval = 120  # 2 minutes in seconds
    
    print("=" * 60)
    print("Authentication Duration Test (Every 2 Minutes)")
    print("=" * 60)
    print(f"Log file: {log_file}")
    print(f"Testing authentication every {test_interval // 60} minutes...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Write header to log
    start_time = datetime.now()
    with open(log_file, 'a') as f:
        f.write(f"\n{'='*60}\n")
        f.write(f"Authentication Duration Test Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test interval: {test_interval} seconds (2 minutes)\n")
        f.write(f"{'='*60}\n")
    
    test_count = 0
    first_failure_time = None
    
    try:
        while True:
            test_count += 1
            timestamp = datetime.now()
            timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            
            # Calculate elapsed time since start
            elapsed = timestamp - start_time
            elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
            
            print(f"[{timestamp_str}] Test #{test_count} (elapsed: {elapsed_str}): Testing...", end=' ', flush=True)
            
            success, message = test_authentication()
            
            if success:
                status = "✓ SUCCESS"
                print(status)
            else:
                status = "✗ FAILED"
                print(f"{status} - {message}")
                if first_failure_time is None:
                    first_failure_time = timestamp
            
            # Log result with elapsed time
            with open(log_file, 'a') as f:
                f.write(f"[{timestamp_str}] Test #{test_count} (elapsed: {elapsed_str}): {status} - {message}\n")
            
            # If authentication failed, log it prominently
            if not success:
                with open(log_file, 'a') as f:
                    f.write(f"{'!'*60}\n")
                    f.write(f"AUTHENTICATION EXPIRED at {timestamp_str}\n")
                    f.write(f"Elapsed time: {elapsed_str}\n")
                    f.write(f"Total tests before expiry: {test_count}\n")
                    if first_failure_time:
                        time_to_failure = first_failure_time - start_time
                        f.write(f"Time until first failure: {str(time_to_failure).split('.')[0]}\n")
                    f.write(f"{'!'*60}\n")
                print(f"\n⚠️  Authentication expired!")
                print(f"   Elapsed time: {elapsed_str}")
                print(f"   Total tests: {test_count}")
                print(f"   Check log: {log_file}")
                break
            
            # Wait 2 minutes before next test
            next_test_time = timestamp + timedelta(seconds=test_interval)
            print(f"   Next test at {next_test_time.strftime('%H:%M:%S')}...")
            time.sleep(test_interval)
            
    except KeyboardInterrupt:
        print("\n\nTest stopped by user")
        with open(log_file, 'a') as f:
            f.write(f"\nTest stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total tests completed: {test_count}\n")
        print(f"Total tests completed: {test_count}")
        print(f"Log saved to: {log_file}")

if __name__ == '__main__':
    main()

