"""NYC MTA Train - Simple class for getting train arrivals"""

from datetime import datetime
from typing import List

from .exceptions import InvalidTrainError
from .models.arrivals import Arrival
from .utils.constants import FEED_URLS, get_direction_names
from .utils.gtfs import fetch_gtfs_feed, filter_by_direction, parse_train_arrivals
from .utils.subway_lines import get_valid_trains


class Train:
    """Get NYC MTA train arrivals for any subway line"""

    def __init__(self, train_id: str, timeout: float = 30.0):
        """
        Create a Train instance

        Args:
            train_id: Train line ID (e.g., 'F', 'N', '1', 'A', 'L')
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.train_id = train_id.upper()
        self.feed_url = FEED_URLS.get(self.train_id)
        if not self.feed_url:
            raise InvalidTrainError(train_id, get_valid_trains())

        self.timeout = timeout
        self.direction_names = get_direction_names(self.train_id)

    def get_arrivals(
        self, stop_id: str, direction: str = "both", min_minutes: int = 0
    ) -> List[Arrival]:
        """
        Get train arrivals at a stop

        Args:
            stop_id: Stop ID (without N/S suffix, e.g., 'F24', 'R16')
            direction: 'N' (northbound), 'S' (southbound), or 'both'
            min_minutes: Minimum minutes away to include (default: 0)

        Returns:
            List of Arrival objects sorted by arrival time

        Example:
            >>> train = Train('F')
            >>> arrivals = train.get_arrivals('F24')  # 7 Av station
            >>> for arrival in arrivals:
            ...     print(f"F train in {arrival.minutes_away} minutes")
        """
        # Fetch and parse GTFS feed with configured timeout
        feed = fetch_gtfs_feed(self.feed_url, timeout=self.timeout)
        raw_arrivals = parse_train_arrivals(feed, self.train_id, stop_id, min_minutes)

        # Filter by direction if specified
        if direction != "both":
            raw_arrivals = filter_by_direction(raw_arrivals, direction)

        # Convert to Arrival objects
        arrivals = []
        for raw in raw_arrivals:
            arrival = Arrival(
                train_id=self.train_id,
                arrival_time=datetime.fromtimestamp(raw["arrival_time"]),
                minutes_away=raw["minutes_away"],
                direction=raw["direction"],
                stop_id=raw["stop_id"],
            )
            arrivals.append(arrival)

        return arrivals

    def get_next_arrivals(
        self, stop_id: str, direction: str = "both", count: int = 3
    ) -> List[Arrival]:
        """
        Get next few arrivals at a stop

        Args:
            stop_id: Stop ID (without N/S suffix)
            direction: 'N', 'S', or 'both'
            count: Number of arrivals to return (default: 3)

        Returns:
            List of next arrival objects

        Example:
            >>> train = Train('F')
            >>> next_trains = train.get_next_arrivals('F24', count=2)  # 7 Av station
        """
        arrivals = self.get_arrivals(stop_id, direction, min_minutes=0)
        return arrivals[:count]

    def __str__(self) -> str:
        return f"{self.train_id} Train"

    def __repr__(self) -> str:
        return f"Train('{self.train_id}')"
