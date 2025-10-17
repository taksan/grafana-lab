# Grafana + Prometheus Lab with Traffic Generator

A complete monitoring lab environment featuring Grafana, Prometheus, Loki, and a sophisticated traffic generator with geocoding, user flows, and DDoS simulation capabilities.

## 🏗️ Architecture

```
┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  User Database   │────▶│ Traffic Gen     │────▶│   Prometheus     │
│   Port: 9500     │     │  Port: 9001     │     │   Port: 9090     │
└──────────────────┘     └────────┬────────┘     └──────────────────┘
                                  │
┌──────────────────┐              │ logs                    │
│ Server Assign    │              ▼                         │
│   Port: 9600     │       ┌──────────────┐                │
└──────────────────┘       │   Promtail   │                │
                           │  Port: 9080  │                │
                           └──────┬───────┘                │
                                  │                         │
                                  ▼                         │
                           ┌──────────────┐                │
                           │     Loki     │                │
                           │  Port: 3100  │                │
                           └──────┬───────┘                │
                                  │                         │
                                  ▼                         ▼
                           ┌─────────────────────────────────┐
                           │          Grafana                │
                           │         Port: 3001              │
                           └─────────────────────────────────┘
```

## 📦 Components

### 1. Traffic Generator
- **FastAPI** application that generates realistic HTTP access logs
- **Geocoding**: Simulates traffic from 11 countries, 30+ cities with accurate coordinates
- **User Flows**: Multi-step user journeys (login, browse, checkout, etc.)
- **Realistic Errors**: Context-aware error generation
- Exposes Prometheus metrics at `/metrics` including geographic data
- REST API for controlling traffic generation behavior
- DDoS simulation feature by region

### 2. User Database
- Provides realistic user data for traffic simulation
- REST API for user management
- Accessible at `http://localhost:9500`

### 3. Server Assignment
- Manages server assignment logic
- Accessible at `http://localhost:9600`

### 4. Prometheus
- Scrapes metrics from the traffic generator every 5 seconds
- Stores time-series data
- Accessible at `http://localhost:9090`

### 5. Loki
- Aggregates and stores logs from the traffic generator
- Provides powerful log querying with LogQL
- Accessible at `http://localhost:3100`

### 6. Promtail
- Log collector agent for Loki
- Uses Docker service discovery to automatically detect containers
- Parses JSON log format
- Extracts labels for efficient querying
- Accessible at `http://localhost:9080`

> **Note on Grafana Alloy**: We initially planned to use Grafana Alloy (the next-generation replacement for Promtail), but encountered a bug where `discovery.docker` fails to discover any containers on certain systems. This is a known issue tracked at [grafana/alloy#3054](https://github.com/grafana/alloy/issues/3054). We've switched to Promtail which has mature and reliable Docker service discovery.

### 7. Grafana
- Pre-configured with Prometheus and Loki datasources
- Auto-provisioned dashboard for traffic generator metrics
- Query and visualize both metrics and logs
- **Geomap support** for geographic visualization
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
   - **Promtail**: http://localhost:9080
   - **Traffic Generator API**: http://localhost:9001
   - **API Docs**: http://localhost:9001/docs
   - **User Database**: http://localhost:9500
   - **Server Assignment**: http://localhost:9600

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

## 🎮 Using the Traffic Generator API

### View API Documentation
Open http://localhost:9001/docs for interactive Swagger documentation.

### Check Status
```bash
curl http://localhost:9001/status
```

### Update Traffic Generation Interval
```bash
curl -X POST http://localhost:9001/update_interval \
  -H "Content-Type: application/json" \
  -d '{
    "min_interval": 0.1,
    "max_interval": 0.5
  }'
```

### Simulate DDoS Attack
Simulate a DDoS attack from a specific region for 60 seconds:

```bash
curl -X POST http://localhost:9001/simulate_ddos \
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
# All logs from traffic-generator
{container="traffic-generator"}

# Only ERROR level logs
{container="traffic-generator"} |= "ERROR"

# Logs with specific status code
{container="traffic-generator", status_code="404"}

# Logs from specific HTTP method
{container="traffic-generator", method="POST"}

# Count logs per second
rate({container="traffic-generator"}[1m])

# Filter by client IP pattern
{container="traffic-generator"} | json | client_ip =~ "103\\..*"

# Logs with status codes 5xx
{container="traffic-generator", status_code=~"5.."}

# Parse and filter by specific user
{container="traffic-generator"} | json | user_id = 1

# Logs from specific country
{container="traffic-generator", country_name="United States"}

# Logs from specific city
{container="traffic-generator", city_name="Tokyo"}
```

### Log Labels Available

Promtail automatically extracts these labels from the JSON logs:
- `container` - Container name (traffic-generator)
- `container_id` - Docker container ID
- `level` - Log level (INFO, WARN, ERROR)
- `method` - HTTP method (GET, POST, etc.)
- `status_code` - HTTP status code
- `country_name` - Country name (e.g., "United States")
- `city_name` - City name (e.g., "New York")

## 📈 Prometheus Metrics

The traffic generator exposes the following metrics:

| Metric Name | Type | Description |
|-------------|------|-------------|
| `logs_generated_total` | Counter | Total number of logs generated |
| `http_requests_total` | Counter | HTTP requests by method and status code |
| `http_requests_by_location_total` | Counter | **HTTP requests by geographic location (country, city, lat, lon)** |
| `ddos_simulation_active` | Gauge | Whether DDoS simulation is active (0 or 1) |
| `ddos_simulation_remaining_seconds` | Gauge | Remaining seconds of DDoS simulation |
| `api_requests_total` | Counter | Total API requests by endpoint |
| `traffic_generation_interval_seconds` | Gauge | Current min/max intervals |
| `active_flows_total` | Gauge | Number of active user flows |

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
docker-compose logs -f traffic-generator
```

Example log entry:
```json
{
  "timestamp": "2025-10-17T10:34:16.450671Z",
  "level": "INFO",
  "client_ip": "66.149.50.20",
  "user_id": 1,
  "user_name": "Leah Cole",
  "session_id": "22b90e02-c17c-4ffe-b1af-94bcaab3cc0a",
  "http": {
    "request": {
      "method": "GET",
      "referrer": "http://www.baldwin.com/posts/blog/searchprivacy.html"
    },
    "response": {
      "status_code": 200,
      "bytes": 4979
    },
    "url": "categories/explore",
    "version": "1.1"
  },
  "user_agent": {
    "original": "Mozilla/5.0 (Windows CE; he-IL; rv:1.9.2.20) Gecko/8341-02-22 19:56:21.590637 Firefox/3.6.2"
  },
  "message": "GET categories/explore - 200",
  "geocode": {
    "location": {
      "lat": 43.6532,
      "lon": -79.3832
    },
    "country_iso_code": "CA",
    "country_name": "Canada",
    "city_name": "Toronto"
  }
}
```

## 🛠️ Customization

### Modifying Prometheus Scrape Interval

Edit `prometheus/prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'traffic-generator'
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

### Modifying Traffic Generation Behavior

Edit `traffic-generator/traffic_generator.py` to customize:
- IP address ranges and geocoding data
- HTTP methods and status codes
- URL patterns
- User flows
- Error generation logic

Then rebuild the container:
```bash
docker-compose up -d --build traffic-generator
```

## 🧪 Testing Scenarios

### Scenario 1: Normal Traffic Monitoring
1. Start the lab
2. Open Grafana dashboard
3. Observe normal traffic patterns

### Scenario 2: High Traffic Simulation
```bash
# Increase log generation rate
curl -X POST http://localhost:9001/update_interval \
  -H "Content-Type: application/json" \
  -d '{"min_interval": 0.01, "max_interval": 0.05}'
```

### Scenario 3: DDoS Attack Detection
```bash
# Simulate 2-minute DDoS from Asia
curl -X POST http://localhost:9001/simulate_ddos \
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
