# Grafana Observability Lab

A complete observability lab demonstrating **Grafana**, **Prometheus**, and **Loki** for metrics and logs monitoring. Includes a sophisticated traffic generator that produces realistic HTTP access logs with geocoding, user flows, and DDoS simulation capabilities.

## 🏗️ Architecture

```
┌──────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  User Database   │────▶│ Traffic Gen     │────▶│   Prometheus     │
│   Port: 9500     │     │  Port: 9001     │     │   Port: 9090     │
└──────────────────┘     └────────┬────────┘     └──────────────────┘
                                  │
┌──────────────────┐              │ logs                    │
│ Server Assign    │              ▼                         │
│   Port: 9600     │       ┌──────────────┐                 │
└──────────────────┘       │   Promtail   │                 │
                           │  Port: 9080  │                 │
                           └──────┬───────┘                 │
                                  │                         │
                                  ▼                         │
                           ┌──────────────┐                 │
                           │     Loki     │                 │
                           │  Port: 3100  │                 │
                           └──────┬───────┘                 │
                                  │                         │
                                  ▼                         ▼
                           ┌─────────────────────────────────┐
                           │          Grafana                │
                           │         Port: 3001              │
                           └─────────────────────────────────┘
```

## 📦 Observability Stack

### Grafana
The central visualization and dashboarding platform for the entire observability stack.

- **Pre-configured datasources**: Prometheus (metrics) and Loki (logs)
- **Auto-provisioned dashboard**: Traffic generator monitoring with geographic visualization
- **Explore mode**: Interactive query builder for both metrics and logs
- **Geomap support**: Visualize traffic by geographic location
- **Default credentials**: `admin` / `admin`
- **Access**: http://localhost:3001

### Prometheus
Time-series database for metrics collection and storage.

- **Scrapes metrics** from traffic generator every 5 seconds
- **PromQL**: Powerful query language for metrics analysis
- **Targets view**: Monitor scrape health and status
- **Access**: http://localhost:9090

### Loki
Log aggregation system optimized for Kubernetes and cloud-native environments.

- **Aggregates logs** from all application containers
- **LogQL**: Query language similar to PromQL for log analysis
- **Label-based indexing**: Efficient log storage and retrieval
- **Access**: http://localhost:3100

### Promtail
Log collection agent that ships logs to Loki.

- **Docker service discovery**: Automatically detects and collects from containers
- **JSON parsing**: Extracts structured fields from application logs
- **Label extraction**: Creates queryable labels for efficient filtering
- **Rootless Docker support**: Works in both standard and rootless environments
- **Access**: http://localhost:9080

> **Note on Grafana Alloy**: We initially planned to use Grafana Alloy (the next-generation replacement for Promtail), but encountered a bug where `discovery.docker` fails to discover containers on certain systems. This is tracked at [grafana/alloy#3054](https://github.com/grafana/alloy/issues/3054). Promtail provides mature and reliable Docker service discovery.

## 🎯 Application Components

### Traffic Generator
FastAPI application that generates realistic HTTP access logs for monitoring.

- **Geocoding**: Simulates traffic from 11 countries, 30+ cities with accurate coordinates
- **User Flows**: Multi-step user journeys (login, browse, checkout, etc.)
- **Realistic Errors**: Context-aware error generation
- **Prometheus metrics**: Exposes `/metrics` endpoint with geographic data
- **REST API**: Control traffic generation behavior dynamically
- **DDoS simulation**: Simulate traffic spikes from specific regions
- **Access**: http://localhost:9001 | **API Docs**: http://localhost:9001/docs

### User Database
Provides realistic user data for traffic simulation.

- REST API for user management
- **Access**: http://localhost:9500

### Server Assignment
Manages server assignment logic for the traffic generator.

- **Access**: http://localhost:9600

## 🚀 Quick Start

### Prerequisites
- Docker
- Docker Compose

### Starting the Lab

1. **Start all services:**
   ```bash
   docker-compose up -d
   ```

2. **(Optional) For rootless Docker:**
   
   If you're using rootless Docker and Promtail fails to connect, create a `.env` file:
   ```bash
   echo "DOCKER_SOCK=/run/user/$(id -u)/docker.sock" > .env
   docker-compose down && docker-compose up -d
   ```

3. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

4. **View real-time logs:**
   ```bash
   docker-compose logs -f traffic-generator
   ```

### Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| **Grafana Dashboard** | http://localhost:3001 | admin / admin |
| **Prometheus** | http://localhost:9090 | - |
| **Loki** | http://localhost:3100 | - |
| **Promtail** | http://localhost:9080 | - |
| **Traffic Generator API** | http://localhost:9001 | - |
| **API Docs (Swagger)** | http://localhost:9001/docs | - |
| **User Database** | http://localhost:9500 | - |
| **Server Assignment** | http://localhost:9600 | - |

### Stopping the Lab

```bash
# Stop services
docker-compose down

# Stop and remove all data volumes
docker-compose down -v
```

## 🎯 Quick Tests

### Check Traffic Generator Status
```bash
curl http://localhost:9001/status | jq
```

### Query Prometheus Metrics
```bash
# Total logs generated
curl -s 'http://localhost:9090/api/v1/query?query=logs_generated_total' | jq

# Log generation rate (per second)
curl -s 'http://localhost:9090/api/v1/query?query=rate(logs_generated_total[1m])' | jq

# HTTP requests by status code
curl -s 'http://localhost:9090/api/v1/query?query=sum(http_requests_total)by(status_code)' | jq
```

### Increase Traffic Rate
```bash
curl -X POST http://localhost:9001/update_interval \
  -H "Content-Type: application/json" \
  -d '{"min_interval": 0.05, "max_interval": 0.2}'
```

### Simulate DDoS Attack
```bash
# 60-second DDoS simulation from Asia
curl -X POST http://localhost:9001/simulate_ddos \
  -H "Content-Type: application/json" \
  -d '{"duration_seconds": 60, "region": "Asia"}'
```

Then watch the Grafana dashboard to see:
- Spike in log generation rate
- DDoS status indicator turns active
- Countdown timer shows remaining time

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

### Using Grafana Explore

1. Open Grafana at http://localhost:3001
2. Click **Explore** (compass icon in left sidebar)
3. Select **Loki** as the datasource
4. Write LogQL queries to filter and analyze logs

### LogQL Query Examples

```logql
# All logs from traffic-generator
{container="traffic-generator"}

# All logs from any fake-traffic-generator service
{service=~"traffic-generator|user-database|server-assignment"}

# Only ERROR level logs
{container="traffic-generator", level="ERROR"}

# Logs with specific status code
{container="traffic-generator", status_code="404"}

# Logs from specific HTTP method
{container="traffic-generator", method="POST"}

# Log rate (logs per second)
rate({container="traffic-generator"}[1m])

# Filter by client IP pattern
{container="traffic-generator"} | json | client_ip =~ "103\\..*"

# All 5xx server errors
{container="traffic-generator", status_code=~"5.."}

# Logs from specific country
{container="traffic-generator", country_name="United States"}

# Logs from specific city
{container="traffic-generator", city_name="Tokyo"}

# Count errors by status code
sum by (status_code) (count_over_time({container="traffic-generator", status_code=~"[45].."}[5m]))
```

### Available Log Labels

Promtail automatically extracts these labels from JSON logs:

| Label | Description | Example Values |
|-------|-------------|----------------|
| `container` | Container name | `traffic-generator`, `user-database`, `server-assignment` |
| `service` | Service label | `traffic-generator`, `user-database`, `server-assignment` |
| `level` | Log level | `INFO`, `WARN`, `ERROR` |
| `method` | HTTP method | `GET`, `POST`, `PUT`, `DELETE` |
| `status_code` | HTTP status code | `200`, `404`, `500` |
| `country_name` | Country name | `United States`, `Japan`, `Brazil` |
| `city_name` | City name | `New York`, `Tokyo`, `São Paulo` |
| `user_name` | User name | Extracted from logs |
| `flow_name` | User flow name | `login`, `browse`, `checkout` |

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
├── .env.example                    # Environment variables for rootless Docker
├── fake-traffic-generator/         # Traffic generator applications
│   ├── traffic-generator/          # Main traffic generator
│   ├── user-database/              # User data service
│   └── server-assignment/          # Server assignment service
├── prometheus/
│   └── prometheus.yml              # Prometheus configuration
├── loki/
│   └── loki-config.yml             # Loki configuration
├── promtail/
│   └── promtail-config.yml         # Promtail configuration
└── grafana/
    └── provisioning/
        ├── datasources/            # Auto-configured datasources
        └── dashboards/             # Pre-built dashboards
```

## 🐛 Troubleshooting

### Services won't start
```bash
# Check logs
docker-compose logs

# Ensure ports are not in use
netstat -tuln | grep -E '3000|8000|9090'
```

### Promtail can't connect to Docker socket (rootless Docker)
If you see errors like "permission denied" or "no such file or directory" for the Docker socket:

1. **Verify your Docker socket location:**
   ```bash
   echo $XDG_RUNTIME_DIR/docker.sock
   # Or check: ls -la /run/user/$(id -u)/docker.sock
   ```

2. **Create a `.env` file with the correct path:**
   ```bash
   echo "DOCKER_SOCK=/run/user/$(id -u)/docker.sock" > .env
   ```

3. **Restart the services:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

4. **Verify Promtail is discovering containers:**
   ```bash
   docker-compose logs promtail | grep -i discovery
   ```

### Grafana shows "No data"
1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify services are running: `docker-compose ps`
3. Check metrics endpoint: http://localhost:9001/metrics
4. Wait 15-30 seconds for initial data collection

### Metrics not updating
```bash
# Restart the traffic generator
docker-compose restart traffic-generator

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

This lab demonstrates key observability concepts:

### Metrics with Prometheus
- ✅ Setting up Prometheus for metrics collection
- ✅ Instrumenting applications with Prometheus client libraries
- ✅ Writing PromQL queries for metrics analysis
- ✅ Understanding metric types (Counter, Gauge)
- ✅ Monitoring application behavior in real-time

### Logs with Loki
- ✅ Configuring Promtail for log collection
- ✅ Using Docker service discovery for automatic log collection
- ✅ Parsing structured JSON logs
- ✅ Writing LogQL queries for log analysis
- ✅ Label-based log indexing and filtering

### Visualization with Grafana
- ✅ Creating custom Grafana dashboards
- ✅ Configuring datasources (Prometheus and Loki)
- ✅ Using Grafana Explore for ad-hoc queries
- ✅ Building panels with PromQL and LogQL
- ✅ Geographic visualization with Geomap

### Observability Best Practices
- ✅ Correlating metrics and logs
- ✅ Detecting anomalies and traffic patterns
- ✅ Using labels effectively for filtering
- ✅ Monitoring distributed systems

## 📝 License

This is a lab/educational project. Feel free to modify and use as needed.

---

**Happy Monitoring! 📊🚀**

*Built with Grafana, Prometheus, and Loki - The modern observability stack*
