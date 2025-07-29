# API Reference

## py_nycmta.Train

### Class: `Train(train_id, timeout=30.0)`

Main class for getting NYC MTA train arrival times.

**Parameters:**
- `train_id` (str): Train line ID (case-insensitive). Valid values: 'F', 'N', '1', 'A', 'L', 'G', 'B', 'D', 'M', 'C', 'E', 'J', 'Z', 'Q', 'R', 'W', '2', '3', '4', '5', '6', '7'
- `timeout` (float, optional): Request timeout in seconds. Default: 30.0

**Raises:**
- `InvalidTrainError`: If train_id is not a valid NYC subway line

**Example:**
```python
from py_nycmta import Train

# Create train instance with default timeout
f_train = Train('F')

# Create train instance with custom timeout
slow_train = Train('N', timeout=60.0)
```

---

### Method: `get_arrivals(stop_id, direction='both', min_minutes=0)`

Get train arrivals at a specific stop.

**Parameters:**
- `stop_id` (str): MTA stop ID without direction suffix (e.g., 'F24', 'R16')
- `direction` (str, optional): Filter by direction. Options: 'N' (northbound), 'S' (southbound), 'both'. Default: 'both'
- `min_minutes` (int, optional): Minimum minutes away to include in results. Default: 0

**Returns:**
- `List[Arrival]`: List of arrival objects sorted by arrival time

**Raises:**
- `MTAConnectionError`: Unable to connect to MTA API
- `MTATimeoutError`: Request timed out
- `MTAAPIError`: API returned an error status
- `RateLimitError`: API rate limit exceeded
- `MTADataError`: Invalid or malformed response data

**Example:**
```python
train = Train('F')

# Get all arrivals
arrivals = train.get_arrivals('F24')

# Get only northbound arrivals
northbound = train.get_arrivals('F24', direction='N')

# Get arrivals at least 5 minutes away
later_arrivals = train.get_arrivals('F24', min_minutes=5)
```

---

### Method: `get_next_arrivals(stop_id, direction='both', count=3)`

Get the next few arrivals at a stop.

**Parameters:**
- `stop_id` (str): MTA stop ID without direction suffix
- `direction` (str, optional): Filter by direction. Default: 'both'
- `count` (int, optional): Number of arrivals to return. Default: 3

**Returns:**
- `List[Arrival]`: List of next arrival objects (limited to count)

**Example:**
```python
train = Train('F')

# Get next 2 arrivals
next_trains = train.get_next_arrivals('F24', count=2)

# Get next northbound arrival only
next_north = train.get_next_arrivals('F24', direction='N', count=1)
```

---

## py_nycmta.Arrival

### Class: `Arrival`

Data class representing a single train arrival.

**Attributes:**
- `train_id` (str): Train line ID (e.g., 'F', 'N', '1')
- `arrival_time` (datetime): Expected arrival time
- `minutes_away` (int): Minutes until arrival
- `direction` (str): Direction of travel ('N' or 'S')
- `stop_id` (str): Full stop ID with direction (e.g., 'F24N')

**Properties:**
- `status` (str): Human-readable status (e.g., "5 mins", "1 min")

**Example:**
```python
train = Train('F')
arrivals = train.get_arrivals('F24')

for arrival in arrivals:
    print(f"Train: {arrival.train_id}")
    print(f"Direction: {arrival.direction}")
    print(f"Minutes away: {arrival.minutes_away}")
    print(f"Status: {arrival.status}")
    print(f"Arrival time: {arrival.arrival_time}")
    print(f"Stop: {arrival.stop_id}")
```

---

## Exceptions

### `MTAError`
Base exception for all MTA-related errors.

### `MTAAPIError(message, status_code=None)`
Exception raised when MTA API returns an error.

**Attributes:**
- `status_code` (int): HTTP status code from API response

### `MTAConnectionError(message)`
Exception raised when unable to connect to MTA API.

### `MTATimeoutError(message)`
Exception raised when MTA API request times out.

### `MTADataError(message)`
Exception raised when MTA API returns invalid or malformed data.

### `InvalidTrainError(train_id, valid_trains)`
Exception raised when an invalid train ID is provided.

**Attributes:**
- `train_id` (str): The invalid train ID that was provided
- `valid_trains` (list): List of valid train IDs

### `RateLimitError(retry_after=None)`
Exception raised when API rate limit is exceeded.

**Attributes:**
- `retry_after` (int): Seconds to wait before retrying (if provided by API)

**Example Error Handling:**
```python
from py_nycmta import Train, MTAConnectionError, MTATimeoutError, RateLimitError

try:
    train = Train('F')
    arrivals = train.get_arrivals('F24')
except MTAConnectionError:
    print("Unable to connect to MTA API")
except MTATimeoutError:
    print("Request timed out")
except RateLimitError as e:
    if e.retry_after:
        print(f"Rate limited. Retry after {e.retry_after} seconds")
    else:
        print("Rate limited")
```

---

## Common Stop IDs

### Manhattan
- `R16` - Times Square-42nd St (N,Q,R,W,S,1,2,3,7)
- `R20` - Union Square-14th St (N,Q,R,W,L,4,5,6)
- `A32` - West 4th St-Washington Sq (A,C,E,B,D,F,M)
- `R22` - 23rd St (N,Q,R,W,F,M)

### Brooklyn
- `F24` - Jay St-MetroTech (F,A,C,R)
- `F20` - Bergen St (F,G)
- `F18` - Carroll St (F,G)
- `D24` - Atlantic Av-Barclays Ctr (N,Q,R,W,B,D,2,3,4,5)

### Queens
- `R09` - 59th St-Lexington Ave (N,Q,R,W,4,5,6)
- `G22` - Court Sq (E,M,G,7)

### Note on Stop IDs
- Use the base stop ID without direction suffix (e.g., 'F24' not 'F24N' or 'F24S')
- The library automatically handles northbound (N) and southbound (S) directions
- Find stop IDs at [MTA Developer Resources](http://web.mta.info/developers/developer-data-terms.html)

---

## Configuration

### Timeouts
```python
# Default timeout (30 seconds)
train = Train('F')

# Custom timeout (60 seconds)
train = Train('F', timeout=60.0)
```

### Retry Behavior
The library automatically retries failed requests with exponential backoff:
- **Max attempts**: 3
- **Retry exceptions**: Connection errors, timeouts
- **Backoff strategy**: Exponential with jitter (1s, 2s, 4s + random jitter)
- **Rate limit handling**: Automatic retry with server-specified delay (up to 5 minutes)

### Network Requirements
- Internet connection required
- Access to `api-endpoint.mta.info`
- No authentication required
- Real-time data (no caching for maximum freshness)

---

## Performance Notes

- Each request fetches fresh data from MTA's real-time feeds
- Response times typically 1-3 seconds
- Large feeds are filtered efficiently for specific trains/stops
- Memory usage scales with number of concurrent Train instances
- No persistent connections or sessions maintained