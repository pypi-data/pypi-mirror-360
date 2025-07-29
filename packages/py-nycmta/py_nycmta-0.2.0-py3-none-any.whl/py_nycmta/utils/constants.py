"""Constants for NYC MTA feeds and train configurations"""

from typing import List

# Import the subway line and station constants

# GTFS Feed URLs
FEED_URLS = {
    # BDFM trains
    "B": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "D": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "F": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    "M": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm",
    # ACE trains
    "A": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "C": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    "E": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace",
    # JZ trains
    "J": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    "Z": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-jz",
    # NQRW trains
    "N": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "Q": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "R": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    "W": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-nqrw",
    # L train
    "L": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l",
    # G train
    "G": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-g",
    # Numbered trains
    "1": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "2": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "3": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "4": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "5": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "6": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
    "7": "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs",
}

# Direction mappings for trains
DIRECTION_NAMES = {
    # Most trains use Manhattan/Brooklyn
    "default": ("manhattan", "brooklyn"),
    # G train is special
    "G": ("queens", "brooklyn"),
}


# Get direction names for a train
def get_direction_names(train_id: str) -> tuple:
    """Get human-readable direction names for a train"""
    return DIRECTION_NAMES.get(train_id, DIRECTION_NAMES["default"])


# Feed groups (for fetching multiple trains at once)
FEED_GROUPS = {
    "nyct%2Fgtfs-bdfm": ["B", "D", "F", "M"],
    "nyct%2Fgtfs-ace": ["A", "C", "E"],
    "nyct%2Fgtfs-jz": ["J", "Z"],
    "nyct%2Fgtfs-nqrw": ["N", "Q", "R", "W"],
    "nyct%2Fgtfs-l": ["L"],
    "nyct%2Fgtfs-g": ["G"],
    "nyct%2Fgtfs": ["1", "2", "3", "4", "5", "6", "7"],
}


# Reverse mapping to get feed ID from URL
def get_feed_id(feed_url: str) -> str:
    """Extract feed ID from URL"""
    return feed_url.split("/")[-1]


# Get all trains that use the same feed
def get_trains_in_feed(train_id: str) -> List[str]:
    """Get all trains that share the same GTFS feed"""
    feed_url = FEED_URLS.get(train_id)
    if not feed_url:
        return []

    feed_id = get_feed_id(feed_url)
    return FEED_GROUPS.get(feed_id, [])
