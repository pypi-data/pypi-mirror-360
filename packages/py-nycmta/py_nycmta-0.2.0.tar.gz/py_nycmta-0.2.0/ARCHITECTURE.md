# PyPI Package Architecture Design

## Package Name: py-nycmta

## Core Principles
1. **Lightweight**: Minimal dependencies (only httpx and protobuf)
2. **Specific**: Each train class does one thing - fetch arrivals for that train
3. **Simple**: No complex inheritance hierarchies or abstractions
4. **Type-safe**: Full type hints for better IDE support

## Package Structure

```
py_nycmta/
├── __init__.py          # Package exports
├── trains/              # Train-specific classes
│   ├── __init__.py
│   ├── base.py         # Minimal base class
│   ├── f_train.py      # FTrain class
│   ├── n_train.py      # NTrain class
│   └── ...             # Other train classes
├── models/             # Simple data models
│   ├── __init__.py
│   └── arrivals.py     # Dataclasses for arrivals
├── utils/              # Shared utilities
│   ├── __init__.py
│   ├── gtfs.py         # GTFS parsing functions
│   └── constants.py    # Feed URLs and mappings
└── data/               # Static data files
    ├── stations.py     # Station mappings
    └── lines.py        # Line to stops mapping

```

## Class Design

### Base Class (minimal)
```python
class TrainBase:
    """Minimal base class for all trains"""
    def __init__(self):
        self.feed_url: str = ""
        self.train_id: str = ""
    
    def get_arrivals(self, stop_id: str) -> List[Arrival]:
        """Get arrivals for this train at a stop"""
        pass
```

### Specific Train Classes
```python
class FTrain(TrainBase):
    """F Train - 6th Avenue Local"""
    def __init__(self):
        self.feed_url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm"
        self.train_id = "F"
```

### Data Models (using dataclasses)
```python
@dataclass
class Arrival:
    """Single train arrival"""
    arrival_time: datetime
    minutes_away: int
    direction: str
    destination: str
    train_id: str
    
@dataclass
class StopInfo:
    """Information about a subway stop"""
    stop_id: str
    stop_name: str
    trains: List[str]
```

## Usage Examples

### Simple Usage
```python
from py_nycmta import FTrain

f_train = FTrain()
arrivals = f_train.get_arrivals("F24")  # 7 Av

for arrival in arrivals:
    print(f"F train to {arrival.destination} in {arrival.minutes_away} minutes")
```

### Multiple Trains at a Station
```python
from py_nycmta import FTrain, GTrain, RTrain

stop_id = "F24"  # 7 Av
trains = [FTrain(), GTrain(), RTrain()]

for train in trains:
    arrivals = train.get_arrivals(stop_id)
    # Process arrivals
```

### Get All Trains at a Stop
```python
from py_nycmta import get_trains_at_stop

arrivals = get_trains_at_stop("R16")  # Times Square
# Returns arrivals for all trains serving this stop
```

## Key Differences from API

1. **No routing**: Each class fetches its own data directly
2. **No validation**: Lightweight - assumes valid stop IDs
3. **No caching**: Stateless, fetch fresh data each time
4. **Simple errors**: Basic exceptions, not HTTP errors
5. **Minimal models**: Just arrival time and basic info

## Dependencies

- httpx: For HTTP requests
- protobuf: For parsing GTFS data
- python-dateutil: For timezone handling (optional)

No web framework dependencies!