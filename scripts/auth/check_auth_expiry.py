#!/usr/bin/env python3
"""Check authentication expiry from browser state."""
import json
from pathlib import Path
from datetime import datetime

def check_auth_expiry():
    """Check when authentication cookies expire."""
    state_file = Path("data/browser_state/browser_state.json")
    
    if not state_file.exists():
        print("Browser state file not found")
        return
    
    with open(state_file, 'r') as f:
        state = json.load(f)
    
    print("=" * 60)
    print("Authentication Cookie Expiry Analysis")
    print("=" * 60)
    
    cookies = state.get('cookies', [])
    if not cookies:
        print("No cookies found in browser state")
        return
    
    print(f"\nFound {len(cookies)} cookies")
    print("\nCookie expiry information:")
    
    now = datetime.now()
    expiring_soon = []
    expired = []
    no_expiry = []
    
    for cookie in cookies:
        name = cookie.get('name', 'Unknown')
        domain = cookie.get('domain', 'Unknown')
        expires = cookie.get('expires', -1)
        
        if expires == -1:
            no_expiry.append((name, domain, "Session cookie (expires when browser closes)"))
        else:
            expiry_time = datetime.fromtimestamp(expires)
            time_until = expiry_time - now
            
            if time_until.total_seconds() < 0:
                expired.append((name, domain, expiry_time, "EXPIRED"))
            elif time_until.total_seconds() < 86400:  # Less than 24 hours
                expiring_soon.append((name, domain, expiry_time, time_until))
            else:
                days = time_until.days
                hours = (time_until.seconds // 3600)
                print(f"  {name} ({domain}): Expires in {days} days, {hours} hours ({expiry_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    if expired:
        print("\n⚠️  EXPIRED COOKIES:")
        for name, domain, expiry_time, _ in expired:
            print(f"  {name} ({domain}): Expired on {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    if expiring_soon:
        print("\n⚠️  EXPIRING SOON (within 24 hours):")
        for name, domain, expiry_time, time_until in expiring_soon:
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            print(f"  {name} ({domain}): Expires in {hours}h {minutes}m ({expiry_time.strftime('%Y-%m-%d %H:%M:%S')})")
    
    if no_expiry:
        print("\n📝 SESSION COOKIES (no expiry, valid until browser closes):")
        for name, domain, note in no_expiry[:5]:  # Show first 5
            print(f"  {name} ({domain}): {note}")
        if len(no_expiry) > 5:
            print(f"  ... and {len(no_expiry) - 5} more session cookies")
    
    # Check for authentication-related cookies
    auth_cookies = [c for c in cookies if any(keyword in c.get('name', '').lower() for keyword in ['auth', 'session', 'token', 'login', 'sso', 'oidc'])]
    if auth_cookies:
        print(f"\n🔐 Found {len(auth_cookies)} authentication-related cookies:")
        for cookie in auth_cookies[:10]:  # Show first 10
            name = cookie.get('name', 'Unknown')
            domain = cookie.get('domain', 'Unknown')
            expires = cookie.get('expires', -1)
            if expires == -1:
                print(f"  {name} ({domain}): Session cookie")
            else:
                expiry_time = datetime.fromtimestamp(expires)
                time_until = expiry_time - now
                if time_until.total_seconds() < 0:
                    print(f"  {name} ({domain}): EXPIRED")
                else:
                    days = time_until.days
                    hours = (time_until.seconds // 3600)
                    print(f"  {name} ({domain}): Expires in {days}d {hours}h")

if __name__ == '__main__':
    check_auth_expiry()

