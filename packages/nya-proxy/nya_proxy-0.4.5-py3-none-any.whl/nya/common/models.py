"""
Data models for request handling in NyaProxy.
"""

import asyncio
import time
from typing import TYPE_CHECKING, Optional, Self

from httpx import Headers

if TYPE_CHECKING:
    from fastapi import Request
    from starlette.datastructures import URL


class ProxyRequest:
    """
    Structured representation of an API request for processing.

    This class encapsulates all the data and metadata needed to handle
    a request throughout the proxy processing pipeline.
    """

    def __init__(
        self,
        method: str,
        _url: "URL",
        headers: Optional[Headers],
        content: Optional[bytes],
        ip: str = None,
    ):
        self.method: str = method

        # Lower number = higher priority (1=retry, 2=priority, 3=normal)
        self.priority: int = 3

        # original url from the proxy request
        self._url: "URL" = _url

        # final url to be requested, will be set later
        self.url: Optional[str] = None

        self.headers: Headers = headers
        self.content: Optional[bytes] = content

        # API Related metadata
        self.api_name: str = None
        self.api_key: Optional[str] = None

        self.ip: str = ip
        self.user: Optional[str] = None

        # Number of attempts made for this request
        self.attempts: int = 0
        # Timestamp when added to queue
        self.added_at: float = time.time()

        # Whether to apply rate limiting for this request
        self._rate_limited: bool = False

        self.future: Optional[asyncio.Future] = None

    @classmethod
    async def from_request(cls, request: "Request") -> "ProxyRequest":
        """
        Create a ProxyRequest instance from a FastAPI Request object.
        """

        return cls(
            method=request.method,
            _url=request.url,
            headers=Headers(request.headers),
            content=await request.body(),
            ip=request.client.host,
        )

    def __lt__(self, other: Self):
        """
        Compare for heap ordering (priority first, then timestamp).
        """
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.added_at < other.added_at
