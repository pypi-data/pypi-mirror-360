"""GTFS feed parsing utilities"""

import time
from typing import List, Optional

import httpx
from google.transit import gtfs_realtime_pb2  # type: ignore[import-untyped]

from ..exceptions import (
    MTAAPIError,
    MTAConnectionError,
    MTADataError,
    MTATimeoutError,
    RateLimitError,
)
from .retry import exponential_backoff_with_jitter, retry_on_failure


@retry_on_failure(
    max_attempts=3,
    backoff_strategy=exponential_backoff_with_jitter,
    retry_exceptions=(MTAConnectionError, MTATimeoutError),
)
def fetch_gtfs_feed(
    feed_url: str, timeout: float = 30.0
) -> gtfs_realtime_pb2.FeedMessage:
    """
    Fetch and parse a GTFS feed from URL with proper error handling

    Args:
        feed_url: URL to fetch GTFS feed from
        timeout: Request timeout in seconds (default: 30.0)

    Returns:
        Parsed GTFS feed message

    Raises:
        MTAConnectionError: If unable to connect to the API
        MTATimeoutError: If the request times out
        MTAAPIError: If the API returns an error status
        RateLimitError: If rate limit is exceeded
        MTADataError: If the response data is invalid
    """
    try:
        response = httpx.get(feed_url, timeout=timeout)

        # Check for rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError(retry_after)

        # Raise for other HTTP errors
        response.raise_for_status()

    except httpx.ConnectError as e:
        raise MTAConnectionError(f"Unable to connect to MTA API: {e}") from e
    except httpx.TimeoutException as e:
        raise MTATimeoutError(f"MTA API request timed out: {e}") from e
    except httpx.HTTPStatusError as e:
        raise MTAAPIError(
            f"MTA API returned error: {e.response.status_code}", e.response.status_code
        ) from e
    except Exception as e:
        raise MTAConnectionError(f"Unexpected error connecting to MTA API: {e}") from e

    try:
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        raise MTADataError(f"Invalid GTFS data received from MTA API: {e}") from e


def parse_train_arrivals(
    feed: gtfs_realtime_pb2.FeedMessage,
    train_id: str,
    stop_id: str,
    min_minutes: int = 0,
) -> List[dict]:
    """
    Parse train arrivals from GTFS feed

    Args:
        feed: Parsed GTFS feed
        train_id: Train line ID (e.g., 'F', 'N', '1')
        stop_id: Stop ID without direction suffix
        min_minutes: Minimum minutes away to include

    Returns:
        List of arrival dictionaries with keys:
        - arrival_time: Unix timestamp
        - minutes_away: Minutes until arrival
        - direction: 'N' or 'S'
        - stop_id: Full stop ID with direction
    """
    arrivals = []
    current_time = int(time.time())

    # Prepare directional stop IDs
    base_stop_id = stop_id.rstrip("NS")
    northbound_id = f"{base_stop_id}N"
    southbound_id = f"{base_stop_id}S"
    stop_ids = [northbound_id, southbound_id]

    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue

        trip_update = entity.trip_update

        # Filter for requested train
        if trip_update.trip.route_id != train_id:
            continue

        for stop_time_update in trip_update.stop_time_update:
            if stop_time_update.stop_id not in stop_ids:
                continue

            if not stop_time_update.HasField("arrival"):
                continue

            arrival_time = stop_time_update.arrival.time
            time_until = arrival_time - current_time
            minutes_until = time_until // 60

            # Skip if too soon or already passed
            if minutes_until < min_minutes:
                continue

            direction = "N" if stop_time_update.stop_id.endswith("N") else "S"

            arrivals.append(
                {
                    "arrival_time": arrival_time,
                    "minutes_away": minutes_until,
                    "direction": direction,
                    "stop_id": stop_time_update.stop_id,
                }
            )

    # Sort by arrival time
    arrivals.sort(key=lambda x: x["arrival_time"])

    return arrivals


def get_trip_destination(
    feed: gtfs_realtime_pb2.FeedMessage, trip_id: str
) -> Optional[str]:
    """Get the destination/headsign for a trip"""
    for entity in feed.entity:
        if entity.HasField("trip_update"):
            trip_update = entity.trip_update
            if trip_update.trip.trip_id == trip_id:
                # Try to get headsign from trip descriptor
                if trip_update.trip.HasField("headsign"):
                    return str(trip_update.trip.headsign)
                # Otherwise get last stop
                if trip_update.stop_time_update:
                    last_stop = trip_update.stop_time_update[-1]
                    return str(last_stop.stop_id.rstrip("NS"))
    return None


def filter_by_direction(arrivals: List[dict], direction: str) -> List[dict]:
    """
    Filter arrivals by direction

    Args:
        arrivals: List of arrival dictionaries
        direction: 'N', 'S', or 'both'

    Returns:
        Filtered list of arrivals
    """
    if direction == "both":
        return arrivals

    return [arr for arr in arrivals if arr["direction"] == direction.upper()]
