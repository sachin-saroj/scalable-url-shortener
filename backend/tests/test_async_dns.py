import asyncio
import socket
from unittest.mock import patch

import pytest

from app.utils.validators import is_valid_url_async


@pytest.mark.asyncio
async def test_async_dns_does_not_block_event_loop():
    def slow_getaddrinfo(*args, **kwargs):
        import time

        time.sleep(0.3)
        # return dummy host info resolving to standard IP (not private)
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))]

    fast_task_completed = False

    async def fast_task():
        nonlocal fast_task_completed
        await asyncio.sleep(0.05)
        fast_task_completed = True

    with patch("socket.getaddrinfo", side_effect=slow_getaddrinfo):
        # Run the async URL validation concurrently with a fast async task
        dns_coro = is_valid_url_async("http://example.com")
        dns_task = asyncio.create_task(dns_coro)
        other_task = asyncio.create_task(fast_task())

        await asyncio.gather(dns_task, other_task)

        is_valid, _ = dns_task.result()
        assert is_valid is True
        assert fast_task_completed is True
