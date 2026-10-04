from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import List
import math

app = FastAPI()

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "*",
    # Lets browser JavaScript read Access-Control-Allow-Origin on the response
    "Access-Control-Expose-Headers": "Access-Control-Allow-Origin",
}


@app.middleware("http")
async def cors_headers(request: Request, call_next):
    if request.method == "OPTIONS":
        return Response(status_code=200, headers=CORS_HEADERS)

    response = await call_next(request)
    for key, value in CORS_HEADERS.items():
        response.headers[key] = value
    return response


DATA = [
    # APAC
    {"region": "apac", "latency_ms": 181.15, "uptime_pct": 97.44},
    {"region": "apac", "latency_ms": 162.94, "uptime_pct": 97.185},
    {"region": "apac", "latency_ms": 150.02, "uptime_pct": 99.494},
    {"region": "apac", "latency_ms": 172.66, "uptime_pct": 97.794},
    {"region": "apac", "latency_ms": 113.42, "uptime_pct": 97.246},
    {"region": "apac", "latency_ms": 136.38, "uptime_pct": 97.129},
    {"region": "apac", "latency_ms": 117.27, "uptime_pct": 98.893},
    {"region": "apac", "latency_ms": 137.81, "uptime_pct": 98.566},
    {"region": "apac", "latency_ms": 148.38, "uptime_pct": 99.414},
    {"region": "apac", "latency_ms": 124.00, "uptime_pct": 98.339},
    {"region": "apac", "latency_ms": 216.89, "uptime_pct": 99.335},
    {"region": "apac", "latency_ms": 212.66, "uptime_pct": 97.601},

    # EMEA
    {"region": "emea", "latency_ms": 211.69, "uptime_pct": 98.824},
    {"region": "emea", "latency_ms": 162.70, "uptime_pct": 98.836},
    {"region": "emea", "latency_ms": 215.50, "uptime_pct": 99.089},
    {"region": "emea", "latency_ms": 135.92, "uptime_pct": 97.636},
    {"region": "emea", "latency_ms": 128.62, "uptime_pct": 98.250},
    {"region": "emea", "latency_ms": 150.22, "uptime_pct": 97.745},
    {"region": "emea", "latency_ms": 148.65, "uptime_pct": 97.822},
    {"region": "emea", "latency_ms": 175.41, "uptime_pct": 98.430},
    {"region": "emea", "latency_ms": 213.77, "uptime_pct": 98.727},
    {"region": "emea", "latency_ms": 213.43, "uptime_pct": 99.362},
    {"region": "emea", "latency_ms": 134.01, "uptime_pct": 97.717},
    {"region": "emea", "latency_ms": 195.08, "uptime_pct": 99.184},

    # AMER
    {"region": "amer", "latency_ms": 132.30, "uptime_pct": 98.654},
    {"region": "amer", "latency_ms": 124.79, "uptime_pct": 98.746},
    {"region": "amer", "latency_ms": 198.48, "uptime_pct": 98.232},
    {"region": "amer", "latency_ms": 135.38, "uptime_pct": 98.204},
    {"region": "amer", "latency_ms": 206.08, "uptime_pct": 97.655},
    {"region": "amer", "latency_ms": 204.66, "uptime_pct": 97.408},
    {"region": "amer", "latency_ms": 191.99, "uptime_pct": 97.116},
    {"region": "amer", "latency_ms": 113.75, "uptime_pct": 99.405},
    {"region": "amer", "latency_ms": 198.37, "uptime_pct": 97.519},
    {"region": "amer", "latency_ms": 169.00, "uptime_pct": 99.231},
    {"region": "amer", "latency_ms": 183.50, "uptime_pct": 97.657},
    {"region": "amer", "latency_ms": 203.40, "uptime_pct": 98.190},
]


class RequestBody(BaseModel):
    regions: List[str]
    threshold_ms: float


def percentile(values, pct):
    values = sorted(values)
    if not values:
        return 0.0
    position = (len(values) - 1) * pct / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return values[lower]
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


@app.post("/")
def metrics(request: RequestBody):
    result = {}
    for region in request.regions:
        records = [r for r in DATA if r["region"] == region]
        if not records:
            result[region] = {"avg_latency": 0, "p95_latency": 0, "avg_uptime": 0, "breaches": 0}
            continue

        latencies = [r["latency_ms"] for r in records]
        uptimes = [r["uptime_pct"] for r in records]
        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(percentile(latencies, 95), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(1 for lat in latencies if lat > request.threshold_ms),
        }
    return JSONResponse(content=result)
