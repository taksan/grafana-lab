"""
FastAPI application for log generator management
"""
import time
import random
import threading
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Response
from pydantic import BaseModel
import uvicorn
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

from log_generator import LogGeneratorConfig, run_log_generator, get_region_ip_ranges

# Initialize FastAPI app
app = FastAPI(title="Log Generator API", version="1.0.0")

# Global configuration instance
config = LogGeneratorConfig()

# Prometheus Metrics
logs_generated_total = Counter('logs_generated_total', 'Total number of logs generated')
http_requests_total = Counter('http_requests_total', 'Total HTTP requests by method and status', ['method', 'status_code'])
ddos_active_gauge = Gauge('ddos_simulation_active', 'Whether DDoS simulation is currently active')
ddos_duration_gauge = Gauge('ddos_simulation_remaining_seconds', 'Remaining seconds of DDoS simulation')
api_requests_total = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
log_generation_interval = Gauge('log_generation_interval_seconds', 'Current log generation interval', ['type'])

# Initialize interval gauges
log_generation_interval.labels(type='min').set(config.min_interval)
log_generation_interval.labels(type='max').set(config.max_interval)


# API Models
class IntervalUpdate(BaseModel):
    """Model for updating log generation interval."""
    min_interval: float
    max_interval: float


class DDoSSimulation(BaseModel):
    """Model for DDoS simulation parameters."""
    duration_seconds: int
    region: Optional[str] = None


# API Endpoints
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    # Update dynamic metrics
    ddos_active_gauge.set(1 if config.ddos_active else 0)
    if config.ddos_active:
        ddos_duration_gauge.set(max(0, config.ddos_end_time - time.time()))
    else:
        ddos_duration_gauge.set(0)
    
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """API status and information."""
    api_requests_total.labels(endpoint='/', method='GET').inc()
    return {
        "service": "Log Generator API",
        "status": "running",
        "config": {
            "min_interval": config.min_interval,
            "max_interval": config.max_interval,
            "ddos_active": config.ddos_active,
            "ddos_region": config.ddos_region if config.ddos_active else None
        }
    }


@app.post("/update_interval")
async def update_interval(interval: IntervalUpdate):
    """Update log generation interval."""
    api_requests_total.labels(endpoint='/update_interval', method='POST').inc()
    
    if interval.min_interval < 0 or interval.max_interval < 0:
        return {"error": "Intervals must be positive"}
    if interval.min_interval > interval.max_interval:
        return {"error": "min_interval must be less than or equal to max_interval"}
    
    config.min_interval = interval.min_interval
    config.max_interval = interval.max_interval
    
    # Update Prometheus gauges
    log_generation_interval.labels(type='min').set(config.min_interval)
    log_generation_interval.labels(type='max').set(config.max_interval)
    
    return {
        "status": "success",
        "message": "Interval updated",
        "min_interval": config.min_interval,
        "max_interval": config.max_interval
    }


@app.post("/simulate_ddos")
async def simulate_ddos(ddos: DDoSSimulation):
    """Simulate DDoS attack from a specific region."""
    api_requests_total.labels(endpoint='/simulate_ddos', method='POST').inc()
    
    if ddos.duration_seconds <= 0:
        return {"error": "Duration must be positive"}
    
    # Select random region if not specified
    regions = list(get_region_ip_ranges().keys())
    selected_region = ddos.region if ddos.region in regions else random.choice(regions)
    
    config.ddos_active = True
    config.ddos_region = selected_region
    config.ddos_end_time = time.time() + ddos.duration_seconds
    
    # Update Prometheus metrics
    ddos_active_gauge.set(1)
    
    return {
        "status": "success",
        "message": f"DDoS simulation started from {selected_region}",
        "region": selected_region,
        "duration_seconds": ddos.duration_seconds,
        "end_time": datetime.fromtimestamp(config.ddos_end_time).isoformat()
    }


@app.get("/status")
async def get_status():
    """Get current generator status."""
    api_requests_total.labels(endpoint='/status', method='GET').inc()
    return {
        "min_interval": config.min_interval,
        "max_interval": config.max_interval,
        "ddos_active": config.ddos_active,
        "ddos_region": config.ddos_region if config.ddos_active else None,
        "ddos_remaining": max(0, config.ddos_end_time - time.time()) if config.ddos_active else 0
    }


if __name__ == "__main__":
    # Prepare metrics dictionary for log generator
    metrics_dict = {
        'logs_generated_total': logs_generated_total,
        'http_requests_total': http_requests_total,
        'ddos_active_gauge': ddos_active_gauge
    }
    
    # Start log generator in background thread
    generator_thread = threading.Thread(target=run_log_generator, args=(config, metrics_dict), daemon=True)
    generator_thread.start()
    
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
