"""Custom exceptions for py-nycmta package"""

from typing import Optional


class MTAError(Exception):
    """Base exception for all MTA-related errors"""

    pass


class MTAAPIError(MTAError):
    """Exception raised when MTA API returns an error"""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class MTAConnectionError(MTAError):
    """Exception raised when unable to connect to MTA API"""

    pass


class MTATimeoutError(MTAError):
    """Exception raised when MTA API request times out"""

    pass


class MTADataError(MTAError):
    """Exception raised when MTA API returns invalid or malformed data"""

    pass


class InvalidTrainError(MTAError):
    """Exception raised when an invalid train ID is provided"""

    def __init__(self, train_id: str, valid_trains: list):
        self.train_id = train_id
        self.valid_trains = valid_trains
        valid_trains_str = ", ".join(sorted(valid_trains))
        super().__init__(
            f"Unknown train ID: {train_id}. Valid trains: {valid_trains_str}"
        )


class InvalidStopError(MTAError):
    """Exception raised when an invalid stop ID is provided"""

    def __init__(self, stop_id: str):
        self.stop_id = stop_id
        super().__init__(f"Invalid stop ID: {stop_id}")


class NoDataError(MTAError):
    """Exception raised when no arrival data is available"""

    def __init__(self, train_id: str, stop_id: str):
        self.train_id = train_id
        self.stop_id = stop_id
        super().__init__(
            f"No arrival data available for {train_id} train at stop {stop_id}"
        )


class RateLimitError(MTAAPIError):
    """Exception raised when API rate limit is exceeded"""

    def __init__(self, retry_after: Optional[int] = None):
        self.retry_after = retry_after
        message = "API rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, status_code=429)
