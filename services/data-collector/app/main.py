"""Data Collector Service for Agentic SRE.

This service acts as a secure proxy and unified API for all underlying
observability platforms (e.g., Datadog, Prometheus, Loki).
The Agentic Core communicates with this service, which then uses the
appropriate credentials to fetch data from the real source.
"""
from __future__ import annotations

import asyncio
import random

from fastapi import Body, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Cortex Data Collector",
    description="A unified API for collecting observability data.",
    version="1.0.0",
)


class MetricsRequest(BaseModel):
    service: str
    metric_name: str
    time_window: str = "1h"


class LogsRequest(BaseModel):
    service: str
    search_term: str
    time_window: str = "1h"


@app.get("/health")
def health_check() -> dict[str, str]:
    """Simple liveness probe."""

    return {"service": "Data Collector", "status": "healthy"}


@app.post("/metrics")
async def get_metrics(request: MetricsRequest):  # noqa: D401, ANN201
    """Mock endpoint for fetching metrics (simulate Prometheus/Datadog)."""

    print("Fetching metrics for:", request.dict())
    await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate latency

    mock_data = {
        "service": request.service,
        "metric": request.metric_name,
        "time_window": request.time_window,
        "data_points": [
            {"timestamp": i, "value": random.uniform(100, 500)} for i in range(10)
        ],
        "summary": f"Mock p99 latency is {random.randint(200, 800)}ms.",
    }
    return {"status": "success", "data": mock_data}


@app.post("/logs")
async def get_logs(request: LogsRequest):  # noqa: D401, ANN201
    """Mock endpoint for fetching logs (simulate Loki/Splunk)."""

    print("Fetching logs for:", request.dict())
    await asyncio.sleep(random.uniform(1.0, 2.5))  # Simulate slower log queries

    mock_data = {
        "service": request.service,
        "search_term": request.search_term,
        "log_count": random.randint(5, 500),
        "logs": [
            f"ERROR: DB connection timeout for user {random.randint(1000, 9999)}",
            f"WARN: Cache miss for key: {request.search_term}",
        ],
        "summary": f"Found {random.randint(5, 500)} logs matching '{request.search_term}'.",
    }
    return {"status": "success", "data": mock_data}

# Additional endpoints (e.g., /traces) can be added as needed.
