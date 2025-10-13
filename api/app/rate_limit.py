from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict
from fastapi import Request, HTTPException


class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)

    def check_rate_limit(self, key: str, max_requests: int, window_seconds: int):
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        request_times = self.requests[key]
        while request_times and request_times[0] < cutoff:
            request_times.popleft()

        if len(request_times) >= max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")

        request_times.append(now)


rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"
