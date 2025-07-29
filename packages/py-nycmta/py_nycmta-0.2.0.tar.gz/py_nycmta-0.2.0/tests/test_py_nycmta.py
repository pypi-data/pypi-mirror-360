"""Core tests for py-nycmta package"""

import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from py_nycmta import Arrival, Train
from py_nycmta.exceptions import (
    InvalidTrainError,
    MTAAPIError,
    MTAConnectionError,
    MTADataError,
    MTATimeoutError,
)


class TestTrainClass:
    """Test Train class functionality"""

    def test_valid_train_creation(self):
        """Test creating trains with valid IDs"""
        # Test all valid subway lines
        valid_trains = [
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "J",
            "L",
            "M",
            "N",
            "Q",
            "R",
            "W",
            "Z",
        ]

        for train_id in valid_trains:
            train = Train(train_id)
            assert train.train_id == train_id.upper()
            assert train.feed_url is not None
            assert train.timeout == 30.0

    def test_case_insensitive_train_id(self):
        """Test that train IDs are case insensitive"""
        train = Train("f")
        assert train.train_id == "F"

        train = Train("a")
        assert train.train_id == "A"

    def test_invalid_train_id(self):
        """Test error handling for invalid train IDs"""
        with pytest.raises(InvalidTrainError, match="Unknown train ID"):
            Train("X")

        with pytest.raises(InvalidTrainError, match="Valid trains:"):
            Train("INVALID")

    def test_custom_timeout(self):
        """Test creating train with custom timeout"""
        train = Train("F", timeout=60.0)
        assert train.timeout == 60.0

    def test_string_representation(self):
        """Test __str__ and __repr__ methods"""
        train = Train("F")
        assert str(train) == "F Train"
        assert repr(train) == "Train('F')"


class TestArrivalClass:
    """Test Arrival dataclass"""

    def test_arrival_creation(self):
        """Test creating Arrival instances"""
        arrival = Arrival(
            train_id="F",
            arrival_time=datetime.now(),
            minutes_away=5,
            direction="N",
            stop_id="F24N",
        )
        assert arrival.train_id == "F"
        assert arrival.minutes_away == 5
        assert arrival.direction == "N"
        assert arrival.stop_id == "F24N"

    def test_arrival_status_property(self):
        """Test the status property"""
        arrival = Arrival(
            train_id="F",
            arrival_time=datetime.now(),
            minutes_away=5,
            direction="N",
            stop_id="F24N",
        )
        assert arrival.status == "5 mins"

        # Test singular minute
        arrival.minutes_away = 1
        assert arrival.status == "1 min"

        # Test zero minutes
        arrival.minutes_away = 0
        assert arrival.status == "0 mins"


class TestNetworkErrors:
    """Test network error handling"""

    @patch("py_nycmta.utils.gtfs.httpx.get")
    def test_connection_error(self, mock_get):
        """Test handling of connection errors"""
        import httpx

        mock_get.side_effect = httpx.ConnectError("Connection failed")

        train = Train("F")
        with pytest.raises(MTAConnectionError):
            train.get_arrivals("F24")

    @patch("py_nycmta.utils.gtfs.httpx.get")
    def test_timeout_error(self, mock_get):
        """Test handling of timeout errors"""
        import httpx

        mock_get.side_effect = httpx.TimeoutException("Request timed out")

        train = Train("F")
        with pytest.raises(MTATimeoutError):
            train.get_arrivals("F24")

    @patch("py_nycmta.utils.gtfs.httpx.get")
    def test_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        import httpx

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Server error", request=Mock(), response=mock_response
        )
        mock_get.return_value = mock_response

        train = Train("F")
        with pytest.raises(MTAAPIError) as exc_info:
            train.get_arrivals("F24")
        assert exc_info.value.status_code == 500


class TestDataParsing:
    """Test GTFS data parsing"""

    @patch("py_nycmta.utils.gtfs.httpx.get")
    def test_malformed_data(self, mock_get):
        """Test handling of malformed GTFS data"""
        mock_response = Mock()
        mock_response.content = b"invalid protobuf data"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        train = Train("F")
        with pytest.raises(MTADataError):
            train.get_arrivals("F24")

    @patch("py_nycmta.utils.gtfs.httpx.get")
    def test_empty_response(self, mock_get):
        """Test handling of empty response"""
        from google.transit import gtfs_realtime_pb2

        # Create a valid but empty GTFS feed with required header
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.header.gtfs_realtime_version = "2.0"
        feed.header.timestamp = int(time.time())

        mock_response = Mock()
        mock_response.content = feed.SerializeToString()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        train = Train("F")
        # Should return empty list for valid but empty feed
        arrivals = train.get_arrivals("F24")
        assert arrivals == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
