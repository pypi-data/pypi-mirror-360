"""Simple data models for train arrivals"""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Arrival:
    """Single train arrival"""

    train_id: str
    arrival_time: datetime
    minutes_away: int
    direction: str  # 'N' or 'S'
    stop_id: str  # Full stop ID with direction

    @property
    def status(self) -> str:
        """Human-readable status"""
        if self.minutes_away == 1:
            return "1 min"
        return f"{self.minutes_away} mins"


@dataclass
class StopInfo:
    """Information about a subway stop"""

    stop_id: str
    stop_name: str
    trains: List[str]  # List of train IDs that serve this stop


@dataclass
class TrainInfo:
    """Information about a train line"""

    train_id: str
    name: str
    feed_url: str
    stops: List[str]  # List of stop IDs served by this train
