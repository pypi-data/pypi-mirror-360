from dataclasses import dataclass
from enum import Enum


class HTTPMethod(str, Enum):
    """Valid HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class SearchMode(str, Enum):
    """Search mode."""

    REGEX = "regex"
    BM25 = "bm25"
    JARO_WINKLER = "jaro_winkler"


@dataclass
class ConnectionResult:
    """Result of a database connection test."""

    connected: bool
    message: str
