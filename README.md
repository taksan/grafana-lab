# Grafana + Prometheus Lab with Log Generator

A complete monitoring lab environment featuring Grafana, Prometheus, and a custom log generator application with DDoS simulation capabilities.

## 🏗️ Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│  Log Generator  │─────▶│  Prometheus  │─────▶│   Grafana   │
│   (FastAPI)     │      │   (Metrics)  │      │ (Dashboards)│
│   Port: 8001    │      │  Port: 9090  │      │  Port: 3001 │
└────────┬────────┘      └──────────────┘      └──────┬──────┘
         │                                             │
         │ logs          ┌──────────────┐             │
         └──────────────▶│ Grafana Alloy│             │
                         │ (Collector)  │             │
                         └──────┬───────┘             │
                                │                     │
                                ▼                     │
                         ┌──────────────┐             │
                         │     Loki     │─────────────┘
                         │(Log Storage) │
                         │  Port: 3100  │
                         └──────────────┘
```

## 📦 Components

### 1. Log Generator
- **FastAPI** application that generates realistic HTTP access logs
- Simulates traffic from different geographic regions
- Exposes Prometheus metrics at `/metrics`
- REST API for controlling log generation behavior
- DDoS simulation feature

### 2. Prometheus
- Scrapes metrics from the log generator every 5 seconds
- Stores time-series data
- Accessible at `http://localhost:9090`

### 3. Loki
- Aggregates and stores logs from the log generator
- Provides powerful log querying with LogQL
- Accessible at `http://localhost:3100`

### 4. Grafana Alloy
- Modern telemetry collector (replaces Promtail)
- Collects logs from Docker containers
- Parses JSON log format
- Extracts labels for efficient querying
- Sends logs to Loki
- Built-in web UI at port 12345

### 5. Grafana
- Pre-configured with Prometheus and Loki datasources
- Auto-provisioned dashboard for log generator metrics
- Query and visualize both metrics and logs
- Default credentials: `admin` / `admin`
- Accessible at `http://localhost:3001`

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Starting the Lab

1. **Clone or navigate to the project directory:**
   ```bash
   cd /home/takeuchi/objective/entrevistas/grafana
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

4. **Access the services:**
   - **Grafana**: http://localhost:3001 (admin/admin)
   - **Prometheus**: http://localhost:9090
   - **Loki**: http://localhost:3100
   - **Alloy UI**: http://localhost:12345
   - **Log Generator API**: http://localhost:8001
   - **API Docs**: http://localhost:8001/docs

### Stopping the Lab

```bash
docker-compose down
```

To remove all data volumes:
```bash
docker-compose down -v
```

## 📊 Grafana Dashboard

The lab includes a pre-configured dashboard with the following panels:

1. **Total Logs Generated** - Counter of all logs produced
2. **Log Generation Rate** - Logs per second over time
3. **HTTP Requests by Method and Status** - Breakdown of request types
4. **DDoS Simulation Status** - Current attack simulation state
5. **DDoS Remaining Time** - Countdown for active simulations
6. **HTTP Status Code Distribution** - Pie chart of response codes
7. **HTTP Method Distribution** - Pie chart of HTTP methods
8. **Min/Max Intervals** - Current log generation intervals
9. **Total API Requests** - API endpoint usage

## 🎮 Using the Log Generator API

### View API Documentation
Open http://localhost:8001/docs for interactive Swagger documentation.

### Check Status
```bash
curl http://localhost:8001/status
```

### Update Log Generation Interval
```bash
curl -X POST http://localhost:8001/update_interval \
  -H "Content-Type: application/json" \
  -d '{
    "min_interval": 0.1,
    "max_interval": 0.5
  }'
```

### Simulate DDoS Attack
Simulate a DDoS attack from a specific region for 60 seconds:

```bash
curl -X POST http://localhost:8001/simulate_ddos \
  -H "Content-Type: application/json" \
  -d '{
    "duration_seconds": 60,
    "region": "Asia"
  }'
```

Available regions:
- `Europe`
- `Asia`
- `South America`
- `Africa`
- `Australia`
- `North America`

If no region is specified, one will be randomly selected.

## 📝 Querying Logs with Loki

### Accessing Logs in Grafana

1. Open Grafana at http://localhost:3001
2. Go to **Explore** (compass icon in left sidebar)
3. Select **Loki** as the datasource
4. Use LogQL to query logs

### Example LogQL Queries

```logql
# All logs from log-generator
{container="log-generator"}

# Only ERROR level logs
{container="log-generator"} |= "ERROR"

# Logs with specific status code
{container="log-generator", status_code="404"}

# Logs from specific HTTP method
{container="log-generator", method="POST"}

# Count logs per second
rate({container="log-generator"}[1m])

# Filter by client IP pattern
{container="log-generator"} | json | client_ip =~ "103\\..*"

# Logs with status codes 5xx
{container="log-generator", status_code=~"5.."}

# Parse and filter by specific user
{container="log-generator"} | json | user_id = "user_42"
```

### Log Labels Available

Promtail automatically extracts these labels from the JSON logs:
- `container` - Container name (log-generator)
- `level` - Log level (INFO, WARN, ERROR)
- `client_ip` - Client IP address
- `user_id` - User ID
- `method` - HTTP method (GET, POST, etc.)
- `status_code` - HTTP status code

## 📈 Prometheus Metrics

The log generator exposes the following metrics:

| Metric Name | Type | Description |
|-------------|------|-------------|
| `logs_generated_total` | Counter | Total number of logs generated |
| `http_requests_total` | Counter | HTTP requests by method and status code |
| `ddos_simulation_active` | Gauge | Whether DDoS simulation is active (0 or 1) |
| `ddos_simulation_remaining_seconds` | Gauge | Remaining seconds of DDoS simulation |
| `api_requests_total` | Counter | Total API requests by endpoint |
| `log_generation_interval_seconds` | Gauge | Current min/max intervals |

### Example Prometheus Queries

```promql
# Rate of log generation per second
rate(logs_generated_total[1m])

# Total 4xx errors
sum(http_requests_total{status_code=~"4.."})

# Percentage of successful requests (2xx)
sum(rate(http_requests_total{status_code=~"2.."}[5m])) / sum(rate(http_requests_total[5m])) * 100

# Request rate by HTTP method
sum by (method) (rate(http_requests_total[1m]))
```

## 🔍 Viewing Logs

To view the raw JSON logs being generated:

```bash
docker-compose logs -f log-generator
```

Example log entry:
```json
{
  "timestamp": "2025-10-15T21:30:00.000000Z",
  "level": "INFO",
  "client_ip": "103.45.123.89",
  "user_id": "user_42",
  "http": {
    "request": {
      "method": "GET",
      "referrer": "https://example.com/page"
    },
    "response": {
      "status_code": 200,
      "bytes": 1234
    },
    "url": "/products/widget/5678",
    "version": "1.1"
  },
  "user_agent": {
    "original": "Mozilla/5.0..."
  },
  "message": "GET /products/widget/5678 - 200"
}
```

## 🛠️ Customization

### Modifying Prometheus Scrape Interval

Edit `prometheus/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'log-generator'
    scrape_interval: 5s  # Change this value
```

Then restart Prometheus:
```bash
docker-compose restart prometheus
```

### Adding More Dashboards

Place additional dashboard JSON files in:
```
grafana/provisioning/dashboards/
```

They will be automatically loaded on Grafana startup.

### Modifying Log Generation Behavior

Edit `log-generator/log_generator.py` to customize:
- IP address ranges
- HTTP methods and status codes
- URL patterns
- Log entry structure

Then rebuild the container:
```bash
docker-compose up -d --build log-generator
```

## 🧪 Testing Scenarios

### Scenario 1: Normal Traffic Monitoring
1. Start the lab
2. Open Grafana dashboard
3. Observe normal traffic patterns

### Scenario 2: High Traffic Simulation
```bash
# Increase log generation rate
curl -X POST http://localhost:8001/update_interval \
  -H "Content-Type: application/json" \
  -d '{"min_interval": 0.01, "max_interval": 0.05}'
```

### Scenario 3: DDoS Attack Detection
```bash
# Simulate 2-minute DDoS from Asia
curl -X POST http://localhost:8001/simulate_ddos \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 120, "region": "Asia"}'
```

Watch the dashboard to see:
- Spike in log generation rate
- DDoS status indicator turns red
- Countdown timer shows remaining time

### Scenario 4: Error Rate Analysis
Monitor the HTTP status code distribution panel to identify:
- High 4xx rates (client errors)
- High 5xx rates (server errors)

## 📁 Project Structure

```
.
├── docker-compose.yml              # Main orchestration file
├── README.md                       # This file
├── log-generator/                  # Log generator application
│   ├── Dockerfile
│   ├── api.py                      # FastAPI application
│   ├── log_generator.py            # Log generation logic
│   └── requirements.txt
├── prometheus/
│   └── prometheus.yml              # Prometheus configuration
└── grafana/
    └── provisioning/
        ├── datasources/
        │   └── prometheus.yml      # Auto-configured datasource
        └── dashboards/
            ├── dashboard.yml       # Dashboard provider config
            └── log-generator-dashboard.json  # Pre-built dashboard
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Ensure ports are not in use
netstat -tuln | grep -E '3000|8000|9090'
```

### Grafana shows "No data"
1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify log-generator is running: `docker-compose ps`
3. Check metrics endpoint: http://localhost:8001/metrics

### Metrics not updating
```bash
# Restart the log generator
docker-compose restart log-generator

# Check Prometheus scrape status
curl http://localhost:9090/api/v1/targets
```

### Dashboard not appearing
```bash
# Restart Grafana
docker-compose restart grafana

# Check provisioning logs
docker-compose logs grafana | grep -i provision
```

## 🎓 Learning Objectives

This lab helps you learn:
- ✅ Setting up Grafana and Prometheus with Docker Compose
- ✅ Instrumenting applications with Prometheus metrics
- ✅ Creating custom Grafana dashboards
- ✅ Monitoring application behavior in real-time
- ✅ Simulating and detecting traffic anomalies
- ✅ Writing PromQL queries for metrics analysis

## 📝 License

This is a lab/educational project. Feel free to modify and use as needed.

## 🤝 Contributing

This is a personal lab environment, but suggestions are welcome!

---

**Happy Monitoring! 📊🚀**
