# Utility Scripts

This folder contains utility scripts for development, testing, and debugging.

## Scripts

### `check_auth.py`
Interactive authentication checker with manual re-authentication.
- Opens visible browser
- Allows manual login if needed
- Shows available courts
- Good for first-time setup and debugging

**Usage:**
```bash
python scripts/utils/check_auth.py
```

### `test_auth_selectors.py`
Test script for authentication selectors.
- Tests CSS selectors for authentication elements
- Useful for debugging selector issues

**Usage:**
```bash
python scripts/utils/test_auth_selectors.py
```

### `analyze_bookings_html.py`
HTML analysis tool for bookings page.
- Parses and analyzes booking page HTML
- Useful for debugging booking extraction

**Usage:**
```bash
python scripts/utils/analyze_bookings_html.py
```

### `quick_check.sh`
Quick check script for bot status.

**Usage:**
```bash
bash scripts/utils/quick_check.sh
```

## Note

For automated authentication testing, use `scripts/test_authentication.py` instead.

