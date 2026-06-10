"""
Prometheus Metrics definition.
───────────────────────────────
Defines Prometheus metrics for application monitoring.
"""

from prometheus_client import Counter, Histogram

# HTTP request counters & histograms
HTTP_REQUESTS_TOTAL = Counter(
    "linkforge_http_requests_total",
    "Total number of HTTP requests processed",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "linkforge_http_request_duration_seconds",
    "HTTP request processing latency in seconds",
    ["method", "path"],
)

# Redis Cache Operations
CACHE_OPERATIONS_TOTAL = Counter(
    "linkforge_cache_operations_total",
    "Total number of cache operations performed",
    ["operation", "status"],  # operation: get, set, delete; status: hit, miss, success, error
)
