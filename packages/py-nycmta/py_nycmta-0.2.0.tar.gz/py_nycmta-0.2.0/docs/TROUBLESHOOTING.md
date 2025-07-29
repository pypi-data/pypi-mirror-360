# Troubleshooting Guide

This guide covers common issues and solutions when using py-nycmta.

## Common Issues

### 1. Import Errors

**Problem:** `ModuleNotFoundError: No module named 'py_nycmta'`

**Solution:**
```bash
# Install the package
pip install py-nycmta

# Or if using a virtual environment
pip install -e .  # for development install
```

**Problem:** `ImportError: cannot import name 'Train' from 'py_nycmta'`

**Solution:**
Ensure you're using the correct import:
```python
from py_nycmta import Train  # Correct
# not: from py_nycmta.train import Train
```

---

### 2. Invalid Train ID Errors

**Problem:** `InvalidTrainError: Unknown train ID: X. Valid trains: ...`

**Solution:**
Use a valid NYC subway line ID:
```python
# Valid train IDs (case-insensitive)
valid_trains = ['F', 'N', '1', 'A', 'L', 'G', 'B', 'D', 'M', 'C', 'E', 'J', 'Z', 'Q', 'R', 'W', '2', '3', '4', '5', '6', '7']

# Examples
train = Train('F')    # ✓ Correct
train = Train('f')    # ✓ Also correct (case-insensitive)
train = Train('X')    # ✗ Error - X train doesn't exist
train = Train('10')   # ✗ Error - no 10 train
```

---

### 3. Network Connection Issues

**Problem:** `MTAConnectionError: Unable to connect to MTA API`

**Possible Causes & Solutions:**

1. **No Internet Connection**
   ```bash
   # Test your connection
   ping google.com
   curl -I https://api-endpoint.mta.info
   ```

2. **Firewall/Proxy Issues**
   ```python
   # If behind a corporate firewall, you may need proxy configuration
   import httpx
   
   # This is handled internally, but you can test connectivity:
   response = httpx.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm')
   ```

3. **DNS Resolution Issues**
   ```bash
   # Test DNS resolution
   nslookup api-endpoint.mta.info
   ```

**Workarounds:**
- Increase timeout: `train = Train('F', timeout=60.0)`
- Check your network configuration
- Try from a different network

---

### 4. Timeout Issues

**Problem:** `MTATimeoutError: MTA API request timed out`

**Solutions:**

1. **Increase Timeout**
   ```python
   # Default timeout is 30 seconds
   train = Train('F', timeout=60.0)  # Increase to 60 seconds
   ```

2. **Check Network Speed**
   ```bash
   # Test download speed
   curl -w "Total time: %{time_total}s\n" -o /dev/null -s https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm
   ```

3. **Retry Pattern**
   ```python
   from py_nycmta import Train, MTATimeoutError
   import time
   
   def get_arrivals_with_retry(train, stop_id, max_retries=3):
       for attempt in range(max_retries):
           try:
               return train.get_arrivals(stop_id)
           except MTATimeoutError:
               if attempt < max_retries - 1:
                   time.sleep(2 ** attempt)  # Exponential backoff
                   continue
               raise
   ```

---

### 5. Rate Limiting

**Problem:** `RateLimitError: API rate limit exceeded`

**Solutions:**

1. **Wait and Retry**
   ```python
   from py_nycmta import Train, RateLimitError
   import time
   
   try:
       train = Train('F')
       arrivals = train.get_arrivals('F24')
   except RateLimitError as e:
       if e.retry_after:
           print(f"Rate limited. Waiting {e.retry_after} seconds...")
           time.sleep(e.retry_after)
           arrivals = train.get_arrivals('F24')  # Retry
   ```

2. **Reduce Request Frequency**
   ```python
   # Don't make requests more frequently than every 30 seconds
   import time
   
   last_request = 0
   min_interval = 30  # seconds
   
   def get_arrivals_throttled(train, stop_id):
       global last_request
       now = time.time()
       if now - last_request < min_interval:
           time.sleep(min_interval - (now - last_request))
       
       last_request = time.time()
       return train.get_arrivals(stop_id)
   ```

---

### 6. No Data Available

**Problem:** Empty results or no arrivals returned

**Debugging Steps:**

1. **Verify Stop ID**
   ```python
   # Common stop IDs
   stops = {
       'Times Square': 'R16',
       'Union Square': 'R20', 
       'Jay St-MetroTech': 'F24',
       'Atlantic Av-Barclays': 'D24'
   }
   
   # Make sure you're using the base stop ID (without N/S suffix)
   train = Train('F')
   arrivals = train.get_arrivals('F24')  # ✓ Correct
   # Not: train.get_arrivals('F24N')     # ✗ Don't include direction
   ```

2. **Check Service Status**
   ```python
   # Try multiple trains at the same stop
   trains = ['F', 'A', 'C', 'R']
   stop_id = 'F24'
   
   for train_id in trains:
       try:
           train = Train(train_id)
           arrivals = train.get_arrivals(stop_id)
           if arrivals:
               print(f"{train_id} train has {len(arrivals)} arrivals")
           else:
               print(f"No {train_id} train arrivals")
       except Exception as e:
           print(f"Error getting {train_id} train: {e}")
   ```

3. **Check Time of Day**
   ```python
   # Some trains have limited service during certain hours
   from datetime import datetime
   
   now = datetime.now()
   print(f"Current time: {now}")
   
   # Late night service (1 AM - 5 AM) may have limited trains
   if 1 <= now.hour <= 5:
       print("Note: Limited late night service")
   ```

---

### 7. Data Parsing Issues

**Problem:** `MTADataError: Invalid GTFS data received from MTA API`

**Possible Causes:**

1. **Temporary MTA API Issues**
   - Wait a few minutes and try again
   - Check MTA service advisories

2. **Network Interference**
   ```python
   # Test raw API response
   import httpx
   
   response = httpx.get('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm')
   print(f"Status: {response.status_code}")
   print(f"Content-Type: {response.headers.get('content-type')}")
   print(f"Content-Length: {len(response.content)}")
   ```

---

### 8. Performance Issues

**Problem:** Slow response times

**Optimization Tips:**

1. **Use Appropriate Timeouts**
   ```python
   # Don't use unnecessarily long timeouts
   train = Train('F', timeout=30.0)  # 30s is usually sufficient
   ```

2. **Filter Results Early**
   ```python
   # Get only what you need
   train = Train('F')
   
   # Get only northbound trains
   northbound = train.get_arrivals('F24', direction='N')
   
   # Get only next 2 trains
   next_trains = train.get_next_arrivals('F24', count=2)
   
   # Skip trains arriving very soon
   later_trains = train.get_arrivals('F24', min_minutes=2)
   ```

3. **Reuse Train Instances**
   ```python
   # ✓ Good: Reuse train instance
   train = Train('F')
   stops = ['F24', 'F20', 'F18']
   
   for stop in stops:
       arrivals = train.get_arrivals(stop)
   
   # ✗ Inefficient: Creating new instances
   for stop in stops:
       train = Train('F')  # Don't do this
       arrivals = train.get_arrivals(stop)
   ```

---

### 9. Common Stop ID Issues

**Problem:** No results for seemingly valid stop IDs

**Solutions:**

1. **Check Stop ID Format**
   ```python
   # MTA stop IDs are usually 2-3 characters + numbers
   valid_formats = [
       'F24',   # F train, stop 24
       'R16',   # R train, stop 16
       'A32',   # A train, stop 32
       'G22'    # G train, stop 22
   ]
   
   # Don't include direction suffixes
   invalid_formats = [
       'F24N',  # ✗ Don't include N/S
       'F24S',  # ✗ Don't include N/S
   ]
   ```

2. **Verify Train Serves Stop**
   ```python
   # Not all trains serve all stops
   # Check MTA map or try multiple trains:
   
   stop_id = 'F24'  # Jay St-MetroTech
   trains_at_stop = ['F', 'A', 'C', 'R']  # Trains that serve this stop
   
   for train_id in trains_at_stop:
       train = Train(train_id)
       arrivals = train.get_arrivals(stop_id)
       print(f"{train_id}: {len(arrivals)} arrivals")
   ```

---

### 10. Development and Testing

**Problem:** Testing without hitting the real API

**Solution:** Use mocks
```python
from unittest.mock import patch, Mock
from py_nycmta import Train

# Mock the GTFS feed fetch
@patch('py_nycmta.utils.gtfs.fetch_gtfs_feed')
def test_arrivals(mock_fetch):
    # Create mock response
    mock_feed = Mock()
    mock_fetch.return_value = mock_feed
    
    train = Train('F')
    # This will use the mock instead of hitting the real API
    arrivals = train.get_arrivals('F24')
```

---

## Getting Help

### 1. Check MTA Service Status
- Visit [MTA Service Status](https://new.mta.info/alerts)
- Check for planned service changes

### 2. Debug Information
When reporting issues, include:

```python
import sys
import py_nycmta

print(f"Python version: {sys.version}")
print(f"py-nycmta version: {py_nycmta.__version__}")

# Test basic connectivity
try:
    train = py_nycmta.Train('F')
    print("✓ Train creation successful")
    
    arrivals = train.get_arrivals('F24')
    print(f"✓ API call successful: {len(arrivals)} arrivals")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}: {e}")
```

### 3. Common Solutions Checklist
- [ ] Check internet connection
- [ ] Verify train ID is valid
- [ ] Ensure stop ID format is correct
- [ ] Try increasing timeout
- [ ] Check MTA service advisories
- [ ] Test with a different train/stop combination
- [ ] Update to latest version: `pip install --upgrade py-nycmta`

### 4. Report Bugs
If you encounter persistent issues:
1. Check existing issues at: https://github.com/dvd-rsnw/py-nycmta/issues
2. Create a new issue with:
   - Error message and full traceback
   - Python version and OS
   - py-nycmta version
   - Minimal code to reproduce the issue
   - Debug information from above

---

## Performance Expectations

**Normal Response Times:**
- Network request: 1-3 seconds
- Data parsing: <100ms
- Total time: 1-5 seconds typically

**When to Expect Slower Performance:**
- First request after MTA feed refresh (every 30 seconds)
- During high traffic periods (rush hour)
- Network congestion
- MTA API maintenance

**Memory Usage:**
- Train instance: ~1KB
- Arrival data: ~100 bytes per arrival
- GTFS feed processing: 1-5MB temporarily during parsing