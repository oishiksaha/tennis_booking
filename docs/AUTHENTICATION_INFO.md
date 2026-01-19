# Authentication Duration Analysis

## Key Findings

### Session Cookies (No Expiry)
The critical authentication cookies are **session cookies** that don't have expiration timestamps:
- `DISSESSIONAuthnDelegation` - Harvard SSO session
- `TGC` (Ticket Granting Cookie) - CAS authentication ticket
- `ASP.NET_SessionId` - Application session
- `__RequestVerificationToken` - CSRF protection

These cookies are saved in the browser state but can be invalidated by the server after:
- Period of inactivity (typically 30 minutes to a few hours)
- Server-side session timeout
- Security policy changes

### Long-Lived Cookies
Some cookies have long expiry (months/years):
- `DT`, `ln`, `luf_*` - Harvard login preferences (expire in ~1 year)
- `cookieControl` - Cookie consent (expires in ~1 year)
- `_ga`, `_ga_*` - Google Analytics (expires in ~1 year)

These help with preferences but don't maintain authentication.

## Best Practices

1. **Refresh authentication regularly**: Run `--authenticate` every few days or when authentication fails
2. **Monitor authentication**: Use `scripts/check_auth_expiry.py` to see cookie status
3. **Automated refresh**: Consider setting up a weekly authentication refresh on the VM

## Testing Authentication Duration

### Manual Test
1. Authenticate: `python -m src.main --authenticate`
2. Wait X hours/days
3. Test: `python -m src.main --headless --test-now`
4. If it fails, authentication expired

### Automated Test Script
You can create a script that:
- Authenticates
- Waits a specific time
- Tests authentication
- Reports results

## Recommendation

For the VM:
- Refresh authentication weekly (via cron job)
- Or refresh when authentication fails (the bot will log errors)
- The saved browser state works, but session cookies may expire after inactivity

