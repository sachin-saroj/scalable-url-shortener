# Observability & Production Operations Handbook

LinkForge implements production-grade structured logging, service health checks, and a metrics engine to provide real-time visibility into application performance.

---

## 1. Structured Logging

LinkForge uses `structlog` for structured logging.

### Environment Behavior

*   **Development / Testing (`APP_ENV=development` or `APP_ENV=testing`)**: Logs are printed in a human-friendly, colorized console output:
    ```text
    2026-06-09T19:25:30.123456Z [info     ] http_request_completed       client_ip=127.0.0.1 duration_ms=12.45 method=GET path=/api/v1/urls request_id=61df1f5b-166f-409c-bc09-90604b92b6a2 service=linkforge status_code=200
    ```
*   **Production (`APP_ENV=production`)**: Logs are printed as single-line, structured JSON strings. These are fully indexable and queryable by log collectors (e.g., Datadog, ELK Stack, GCP Cloud Logging):
    ```json
    {"event": "http_request_completed", "client_ip": "127.0.0.1", "duration_ms": 12.45, "method": "GET", "path": "/api/v1/urls", "request_id": "61df1f5b-166f-409c-bc09-90604b92b6a2", "service": "linkforge", "status_code": 200, "level": "info", "logger": "http.access", "timestamp": "2026-06-09T19:25:30.123456Z"}
    ```

### Request Context Binding

Every request goes through the observability middleware which extracts or generates a `request_id` (propagated via `X-Request-ID` header). This request ID is bound to the async task execution context using python `contextvars`.
Any log statements executed by DB services, encoders, validators, or handlers during that request's thread of execution will automatically include the `request_id` context.

---

## 2. Prometheus Metrics

LinkForge exposes standard Prometheus metrics at the `/metrics` endpoint.

### Exposed Metrics

| Metric Name | Type | Labels | Description |
| :--- | :--- | :--- | :--- |
| `linkforge_http_requests_total` | Counter | `method`, `path`, `status_code` | Total HTTP requests processed. |
| `linkforge_http_request_duration_seconds` | Histogram | `method`, `path` | Request processing latency distribution. |
| `linkforge_cache_operations_total` | Counter | `operation`, `status` | Redis cache operations tracking (`operation` can be `get`, `set`, `delete`, `get_analytics`, `set_analytics`; `status` can be `hit`, `miss`, `success`, `error`). |

---

## 3. Health & Probes

To integrate with container orchestrators and load balancers, LinkForge exposes three distinct health check endpoints:

*   **`/health`**: Standard backward-compatible check. Pings Redis and reports degraded state on connectivity loss.
*   **`/health/live`**: **Liveness Probe**. Instantly returns `200 OK` if the Python service process is running. Minimizes overhead and prevents cascade failures during heavy load.
*   **`/health/ready`**: **Readiness Probe**. Performs live connectivity tests on the PostgreSQL connection pool (via `SELECT 1`) and the Redis instance (via `PING`). Used by load balancers and deployment services (like Kubernetes, Cloud Run, Render) to determine if traffic should be routed to this container.

---

## 4. Local Observability Stack

You can verify and test metrics compilation locally using the provided Prometheus & Grafana stack.

### Running the Stack

1.  Spin up the entire stack:
    ```bash
    docker-compose up --build -d
    ```
2.  Verify containers are running:
    ```bash
    docker-compose ps
    ```
    This launches the database, redis, backend, celery, prometheus, and grafana.

### Scouring Metrics & Dashboarding

*   **Prometheus**: Visit `http://localhost:9090` to access the Prometheus expression browser. You can query `linkforge_http_requests_total` directly.
*   **Grafana**: Visit `http://localhost:3000`.
    *   **Username**: `admin`
    *   **Password**: `admin`
    *   The **LinkForge System Dashboard** is pre-provisioned and auto-loaded. It displays real-time charts for HTTP request volume, latency percentiles (P95/P99), cache hit/miss rates, and overall cache hit ratios.
