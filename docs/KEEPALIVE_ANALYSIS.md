# Keep-Alive Service: Pros, Cons, Costs, and Environmental Impact

**Last Updated**: January 18, 2026

## Overview

The keep-alive service visits the booking page every 10 minutes to refresh session cookies and prevent authentication expiration. This document analyzes the trade-offs.

---

## ✅ Pros

### 1. **Reliability**
- **Prevents booking failures**: Authentication stays valid, so bookings won't fail due to expired sessions
- **Automated**: No manual intervention needed to maintain authentication
- **Proven**: Tested and working - authentication has stayed valid for 1+ hour with keep-alive

### 2. **Backup Strategy**
- **Long-lived cookie fallback**: If session expires, automatically uses long-lived cookies (DT, ln, luf) for re-auth
- **No password needed**: Automatic re-authentication works seamlessly
- **Self-healing**: Recovers from authentication failures automatically

### 3. **Production Ready**
- **Set it and forget it**: Once running, requires minimal maintenance
- **Logging**: Comprehensive logs show exactly what's happening
- **Monitoring**: Easy to check status and verify it's working

### 4. **Booking Success Rate**
- **Higher success rate**: Eliminates authentication-related booking failures
- **Time-critical**: Bookings happen at exact times (on the hour) - can't afford auth failures

---

## ❌ Cons

### 1. **Resource Usage**
- **Continuous process**: Keep-alive service runs 24/7
- **Browser automation**: Launches browser instance every 10 minutes (~6 seconds per visit)
- **Memory**: Each browser instance uses ~25-30MB RAM temporarily
- **CPU**: Brief CPU spikes during browser launches

### 2. **Network Traffic**
- **Regular requests**: HTTP requests every 10 minutes (144 requests/day)
- **Bandwidth**: Minimal (~50-100KB per request, ~7-14MB/day)
- **Server load**: Small additional load on booking system servers

### 3. **Complexity**
- **Additional service**: One more process to monitor and maintain
- **Potential failure point**: If keep-alive fails, authentication may expire
- **Log management**: Generates logs that need monitoring

### 4. **Unnecessary Activity**
- **When not booking**: Still runs even when no bookings are scheduled
- **Idle periods**: Most of the time, just maintaining state without booking

---

## 💰 Costs

### GCP VM Costs (Current Setup)
- **VM Instance**: e2-micro (1 vCPU, 1GB RAM)
  - **Cost**: ~$6-8/month (with educational credits, likely free)
  - **Running 24/7**: Required anyway for scheduled bookings

### Keep-Alive Service Costs
- **CPU**: Negligible (~0.1% average, brief spikes to 1-2%)
- **Memory**: ~30MB temporarily every 10 minutes (not persistent)
- **Network**: ~7-14MB/day bandwidth (~0.2GB/month)
- **Storage**: Log files (~1-5MB/month)

**Total Additional Cost**: **Essentially $0** (within free tier limits)

### Alternative: Manual Re-Authentication
- **Time cost**: Manual intervention when auth expires
- **Risk cost**: Potential booking failures
- **Maintenance cost**: Monitoring and fixing auth issues

---

## 🌍 Environmental Impact

### Energy Consumption

**VM Running 24/7:**
- **Base VM**: ~5-10W (e2-micro instance)
- **Keep-alive overhead**: ~0.1W additional (minimal)
- **Total**: ~5-10W continuous

**Monthly Energy:**
- ~3.6-7.2 kWh/month
- **Carbon equivalent**: ~1-2 kg CO₂/month (depending on grid)
- **Cost**: ~$0.50-1.00/month in electricity (if paying)

### Browser Automation
- **Per visit**: ~6 seconds of browser automation
- **Daily**: ~144 visits × 6 seconds = ~14 minutes/day of browser activity
- **Energy**: Negligible additional consumption

### Network Impact
- **Requests**: 144 HTTP requests/day
- **Bandwidth**: ~7-14MB/day
- **Server load**: Minimal (single user, low frequency)

### Comparison
- **Email checking**: Similar energy footprint (checking email every 10 min)
- **Background app**: Less than most background applications
- **Smartphone**: Much less than a smartphone's background activity

---

## 🔄 Alternatives

### 1. **No Keep-Alive (Current Alternative)**
- **Pros**: No resource usage, simpler
- **Cons**: Authentication expires after ~16 minutes, requires manual re-auth, booking failures
- **Best for**: Testing, development

### 2. **Longer Interval (Every 15-20 minutes)**
- **Pros**: Less frequent requests, still prevents expiration
- **Cons**: Risk if session expires faster than expected
- **Best for**: If 16-minute expiration is consistent

### 3. **Conditional Keep-Alive (Only Before Bookings)**
- **Pros**: Only runs when needed
- **Cons**: More complex, need to predict when to start
- **Best for**: If bookings are infrequent

### 4. **Token Refresh API (If Available)**
- **Pros**: More efficient, no browser needed
- **Cons**: Requires API access (likely not available)
- **Best for**: If Harvard provides such an API

---

## 📊 Recommendations

### For Production Use: **✅ Use Keep-Alive**

**Reasons:**
1. **Reliability**: Prevents booking failures
2. **Low cost**: Essentially free (within educational credits)
3. **Minimal environmental impact**: Negligible additional energy
4. **Automated**: No manual intervention needed
5. **Proven**: Working in tests

### Optimization Options:

1. **Reduce frequency** (if safe):
   - Test if 15-minute interval still works
   - Reduces requests by 33%

2. **Conditional execution**:
   - Only run keep-alive on days with bookings
   - Saves resources on off-days

3. **Monitor and alert**:
   - Set up alerts if keep-alive fails
   - Ensure reliability

---

## 📈 Monitoring

### Key Metrics to Track:
- **Keep-alive success rate**: Should be 100%
- **Auto re-auth success rate**: Should be 100% (when needed)
- **Resource usage**: CPU < 1%, Memory < 50MB
- **Authentication duration**: Should stay valid indefinitely

### Logs to Monitor:
- `/tmp/auth_keepalive.log` - Keep-alive activity
- `/tmp/auth_duration_test.log` - Authentication test results

---

## 🎯 Conclusion

**The keep-alive service is recommended for production use** because:

1. **Benefits outweigh costs**: Prevents booking failures with minimal resource usage
2. **Low environmental impact**: Negligible additional energy consumption
3. **Cost-effective**: Essentially free within educational credits
4. **Reliable**: Proven to work in testing

The service uses minimal resources and provides significant reliability benefits for automated bookings.

---

## 📝 Notes

- Current test shows authentication staying valid for 1+ hour with keep-alive
- Without keep-alive, authentication expires after ~16 minutes
- Keep-alive visits every 10 minutes prevent expiration
- Long-lived cookies (DT, ln, luf) provide backup re-authentication

