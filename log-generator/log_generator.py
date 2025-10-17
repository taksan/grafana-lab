"""
Log generation module - handles all log generation logic
"""
import time
import json
import random
from datetime import datetime
from faker import Faker

fake = Faker()

# Prometheus metrics will be imported from api.py when needed
# This avoids circular imports
_metrics_module = None


class LogGeneratorConfig:
    """Configuration for log generator."""
    def __init__(self):
        self.min_interval = 0.2
        self.max_interval = 1.5
        self.ddos_active = False
        self.ddos_end_time = 0
        self.ddos_region = None


def get_region_geocode_data():
    """Return IP ranges with geocoding information organized by region."""
    return {
        "Europe": {
            "ranges": [
                ("2.16.0.0", "2.31.255.255"),
                ("5.0.0.0", "5.255.255.255"),
                ("31.0.0.0", "31.255.255.255"),
                ("37.0.0.0", "37.255.255.255"),
                ("46.0.0.0", "46.255.255.255"),
                ("62.0.0.0", "62.255.255.255"),
                ("78.0.0.0", "78.255.255.255"),
                ("80.0.0.0", "80.255.255.255"),
                ("82.0.0.0", "82.255.255.255"),
                ("88.0.0.0", "88.255.255.255"),
            ],
            "countries": [
                {"name": "United Kingdom", "code": "GB", "cities": [
                    {"name": "London", "lat": 51.5074, "lon": -0.1278},
                    {"name": "Manchester", "lat": 53.4808, "lon": -2.2426},
                    {"name": "Birmingham", "lat": 52.4862, "lon": -1.8904},
                ]},
                {"name": "Germany", "code": "DE", "cities": [
                    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
                    {"name": "Munich", "lat": 48.1351, "lon": 11.5820},
                    {"name": "Frankfurt", "lat": 50.1109, "lon": 8.6821},
                ]},
                {"name": "France", "code": "FR", "cities": [
                    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
                    {"name": "Lyon", "lat": 45.7640, "lon": 4.8357},
                    {"name": "Marseille", "lat": 43.2965, "lon": 5.3698},
                ]},
            ]
        },
        "Asia": {
            "ranges": [
                ("1.0.0.0", "1.255.255.255"),
                ("14.0.0.0", "14.255.255.255"),
                ("27.0.0.0", "27.255.255.255"),
                ("36.0.0.0", "36.255.255.255"),
                ("42.0.0.0", "42.255.255.255"),
                ("58.0.0.0", "58.255.255.255"),
                ("103.0.0.0", "103.255.255.255"),
                ("110.0.0.0", "110.255.255.255"),
                ("116.0.0.0", "116.255.255.255"),
                ("125.0.0.0", "125.255.255.255"),
            ],
            "countries": [
                {"name": "Japan", "code": "JP", "cities": [
                    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
                    {"name": "Osaka", "lat": 34.6937, "lon": 135.5023},
                    {"name": "Kyoto", "lat": 35.0116, "lon": 135.7681},
                ]},
                {"name": "China", "code": "CN", "cities": [
                    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
                    {"name": "Shanghai", "lat": 31.2304, "lon": 121.4737},
                    {"name": "Shenzhen", "lat": 22.5431, "lon": 114.0579},
                ]},
                {"name": "India", "code": "IN", "cities": [
                    {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
                    {"name": "Delhi", "lat": 28.7041, "lon": 77.1025},
                    {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946},
                ]},
            ]
        },
        "South America": {
            "ranges": [
                ("177.0.0.0", "177.255.255.255"),
                ("179.0.0.0", "179.255.255.255"),
                ("181.0.0.0", "181.255.255.255"),
                ("186.0.0.0", "186.255.255.255"),
                ("189.0.0.0", "189.255.255.255"),
                ("190.0.0.0", "190.255.255.255"),
                ("191.0.0.0", "191.255.255.255"),
                ("200.0.0.0", "200.255.255.255"),
                ("201.0.0.0", "201.255.255.255"),
                ("187.0.0.0", "187.255.255.255"),
            ],
            "countries": [
                {"name": "Brazil", "code": "BR", "cities": [
                    {"name": "São Paulo", "lat": -23.5505, "lon": -46.6333},
                    {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729},
                    {"name": "Brasília", "lat": -15.8267, "lon": -47.9218},
                ]},
                {"name": "Argentina", "code": "AR", "cities": [
                    {"name": "Buenos Aires", "lat": -34.6037, "lon": -58.3816},
                    {"name": "Córdoba", "lat": -31.4201, "lon": -64.1888},
                    {"name": "Rosario", "lat": -32.9442, "lon": -60.6505},
                ]},
                {"name": "Colombia", "code": "CO", "cities": [
                    {"name": "Bogotá", "lat": 4.7110, "lon": -74.0721},
                    {"name": "Medellín", "lat": 6.2476, "lon": -75.5658},
                    {"name": "Cali", "lat": 3.4516, "lon": -76.5320},
                ]},
            ]
        },
        "Africa": {
            "ranges": [
                ("41.0.0.0", "41.255.255.255"),
                ("102.0.0.0", "102.255.255.255"),
                ("105.0.0.0", "105.255.255.255"),
                ("154.0.0.0", "154.255.255.255"),
                ("196.0.0.0", "196.255.255.255"),
                ("197.0.0.0", "197.255.255.255"),
                ("129.0.0.0", "129.255.255.255"),
                ("155.0.0.0", "155.255.255.255"),
                ("160.0.0.0", "160.255.255.255"),
                ("169.0.0.0", "169.255.255.255"),
            ],
            "countries": [
                {"name": "South Africa", "code": "ZA", "cities": [
                    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473},
                    {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241},
                    {"name": "Durban", "lat": -29.8587, "lon": 31.0218},
                ]},
                {"name": "Nigeria", "code": "NG", "cities": [
                    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792},
                    {"name": "Abuja", "lat": 9.0765, "lon": 7.3986},
                    {"name": "Kano", "lat": 12.0022, "lon": 8.5920},
                ]},
                {"name": "Egypt", "code": "EG", "cities": [
                    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
                    {"name": "Alexandria", "lat": 31.2001, "lon": 29.9187},
                    {"name": "Giza", "lat": 30.0131, "lon": 31.2089},
                ]},
            ]
        },
        "Australia": {
            "ranges": [
                ("1.128.0.0", "1.159.255.255"),
                ("27.32.0.0", "27.47.255.255"),
                ("49.0.0.0", "49.255.255.255"),
                ("101.0.0.0", "101.255.255.255"),
                ("203.0.0.0", "203.255.255.255"),
            ],
            "countries": [
                {"name": "Australia", "code": "AU", "cities": [
                    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
                    {"name": "Melbourne", "lat": -37.8136, "lon": 144.9631},
                    {"name": "Brisbane", "lat": -27.4698, "lon": 153.0251},
                ]},
            ]
        },
        "North America": {
            "ranges": [
                ("8.0.0.0", "8.255.255.255"),
                ("12.0.0.0", "12.255.255.255"),
                ("24.0.0.0", "24.255.255.255"),
                ("50.0.0.0", "50.255.255.255"),
                ("66.0.0.0", "66.255.255.255"),
            ],
            "countries": [
                {"name": "United States", "code": "US", "cities": [
                    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
                    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
                    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298},
                    {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
                ]},
                {"name": "Canada", "code": "CA", "cities": [
                    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832},
                    {"name": "Vancouver", "lat": 49.2827, "lon": -123.1207},
                    {"name": "Montreal", "lat": 45.5017, "lon": -73.5673},
                ]},
            ]
        },
    }


def get_region_ip_ranges():
    """Return IP ranges organized by region (legacy format)."""
    geocode_data = get_region_geocode_data()
    return {region: data["ranges"] for region, data in geocode_data.items()}


def generate_distributed_ip_with_geocode():
    """Generate IP addresses with geocoding information."""
    geocode_data = get_region_geocode_data()
    
    # Select a random region
    region = random.choice(list(geocode_data.keys()))
    region_data = geocode_data[region]
    
    # Select a random IP range from that region
    ip_ranges = region_data["ranges"]
    start_ip, end_ip = random.choice(ip_ranges)
    
    # Generate IP
    start_parts = [int(x) for x in start_ip.split('.')]
    end_parts = [int(x) for x in end_ip.split('.')]
    
    ip_parts = []
    for i in range(4):
        if i < 3:
            ip_parts.append(random.randint(start_parts[i], end_parts[i]))
        else:
            ip_parts.append(random.randint(1, 254))
    
    ip = '.'.join(map(str, ip_parts))
    
    # Select a random country and city from that region
    country = random.choice(region_data["countries"])
    city = random.choice(country["cities"])
    
    geocode = {
        "location": {
            "lat": city["lat"],
            "lon": city["lon"]
        },
        "country_iso_code": country["code"],
        "country_name": country["name"],
        "city_name": city["name"]
    }
    
    return ip, geocode


def generate_distributed_ip():
    """Generate IP addresses from various countries for better geographic distribution (legacy)."""
    ip, _ = generate_distributed_ip_with_geocode()
    return ip


def _generate_distributed_ip_legacy():
    """Legacy IP generation without geocode."""
    # IP ranges organized by region with equal representation
    ip_ranges = [
        # Europe (10 ranges)
        ("2.16.0.0", "2.31.255.255"),
        ("5.0.0.0", "5.255.255.255"),
        ("31.0.0.0", "31.255.255.255"),
        ("37.0.0.0", "37.255.255.255"),
        ("46.0.0.0", "46.255.255.255"),
        ("62.0.0.0", "62.255.255.255"),
        ("78.0.0.0", "78.255.255.255"),
        ("80.0.0.0", "80.255.255.255"),
        ("82.0.0.0", "82.255.255.255"),
        ("88.0.0.0", "88.255.255.255"),
        
        # Asia (10 ranges)
        ("1.0.0.0", "1.255.255.255"),
        ("14.0.0.0", "14.255.255.255"),
        ("27.0.0.0", "27.255.255.255"),
        ("36.0.0.0", "36.255.255.255"),
        ("42.0.0.0", "42.255.255.255"),
        ("58.0.0.0", "58.255.255.255"),
        ("103.0.0.0", "103.255.255.255"),
        ("110.0.0.0", "110.255.255.255"),
        ("116.0.0.0", "116.255.255.255"),
        ("125.0.0.0", "125.255.255.255"),
        
        # South America (10 ranges)
        ("177.0.0.0", "177.255.255.255"),
        ("179.0.0.0", "179.255.255.255"),
        ("181.0.0.0", "181.255.255.255"),
        ("186.0.0.0", "186.255.255.255"),
        ("189.0.0.0", "189.255.255.255"),
        ("190.0.0.0", "190.255.255.255"),
        ("191.0.0.0", "191.255.255.255"),
        ("200.0.0.0", "200.255.255.255"),
        ("201.0.0.0", "201.255.255.255"),
        ("187.0.0.0", "187.255.255.255"),
        
        # Africa (10 ranges)
        ("41.0.0.0", "41.255.255.255"),
        ("102.0.0.0", "102.255.255.255"),
        ("105.0.0.0", "105.255.255.255"),
        ("154.0.0.0", "154.255.255.255"),
        ("196.0.0.0", "196.255.255.255"),
        ("197.0.0.0", "197.255.255.255"),
        ("129.0.0.0", "129.255.255.255"),
        ("155.0.0.0", "155.255.255.255"),
        ("160.0.0.0", "160.255.255.255"),
        ("169.0.0.0", "169.255.255.255"),
        
        # Australia/Oceania (5 ranges)
        ("1.128.0.0", "1.159.255.255"),
        ("27.32.0.0", "27.47.255.255"),
        ("49.0.0.0", "49.255.255.255"),
        ("101.0.0.0", "101.255.255.255"),
        ("203.0.0.0", "203.255.255.255"),
        
        # North America - US (5 ranges, reduced)
        ("8.0.0.0", "8.255.255.255"),
        ("12.0.0.0", "12.255.255.255"),
        ("24.0.0.0", "24.255.255.255"),
        ("50.0.0.0", "50.255.255.255"),
        ("66.0.0.0", "66.255.255.255"),
    ]
    
    # Select a random IP range
    start_ip, end_ip = random.choice(ip_ranges)
    
    # Convert IP to integer
    start_parts = [int(x) for x in start_ip.split('.')]
    end_parts = [int(x) for x in end_ip.split('.')]
    
    # Generate random IP within the range
    ip_parts = []
    for i in range(4):
        if i < 3:
            ip_parts.append(random.randint(start_parts[i], end_parts[i]))
        else:
            ip_parts.append(random.randint(1, 254))
    
    return '.'.join(map(str, ip_parts))


def generate_ip_from_region_with_geocode(region_name):
    """Generate IP from a specific region with geocode information."""
    geocode_data = get_region_geocode_data()
    if region_name not in geocode_data:
        region_name = random.choice(list(geocode_data.keys()))
    
    region_data = geocode_data[region_name]
    ip_ranges = region_data["ranges"]
    start_ip, end_ip = random.choice(ip_ranges)
    
    start_parts = [int(x) for x in start_ip.split('.')]
    end_parts = [int(x) for x in end_ip.split('.')]
    
    ip_parts = []
    for i in range(4):
        if i < 3:
            ip_parts.append(random.randint(start_parts[i], end_parts[i]))
        else:
            ip_parts.append(random.randint(1, 254))
    
    ip = '.'.join(map(str, ip_parts))
    
    # Select a random country and city from that region
    country = random.choice(region_data["countries"])
    city = random.choice(country["cities"])
    
    geocode = {
        "location": {
            "lat": city["lat"],
            "lon": city["lon"]
        },
        "country_iso_code": country["code"],
        "country_name": country["name"],
        "city_name": city["name"]
    }
    
    return ip, geocode


def generate_ip_from_region(region_name):
    """Generate IP from a specific region (legacy)."""
    ip, _ = generate_ip_from_region_with_geocode(region_name)
    return ip


def generate_log_entry(override_ip=None, override_geocode=None):
    """Generates a single, structured log entry with geocoding information."""
    
    # Simulate different HTTP methods
    method = random.choice(["GET", "POST", "PUT", "DELETE", "PATCH"])
    
    # Simulate common status codes, with a higher probability for 2xx and 4xx
    status_code = random.choices(
        [200, 201, 204, 301, 400, 401, 403, 404, 500, 503], 
        weights=[15, 5, 2, 3, 5, 3, 2, 10, 4, 1], 
        k=1
    )[0]
    
    # Generate a fake URL path
    uri = fake.uri_path()
    
    # Add product or user context to some URLs
    if random.random() < 0.3:
        uri = f"/products/{fake.word()}/{random.randint(1000, 9999)}"
    elif random.random() < 0.2:
        uri = f"/users/{fake.user_name()}/profile"
    
    # Generate IP and geocode data
    if override_ip:
        client_ip = override_ip
        geocode = override_geocode if override_geocode else None
    else:
        client_ip, geocode = generate_distributed_ip_with_geocode()
        
    log_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "INFO" if status_code < 400 else ("ERROR" if status_code >= 500 else "WARN"),
        "client_ip": client_ip,
        "user_id": f"user_{random.randint(1, 100)}",
        "http": {
            "request": {
                "method": method,
                "referrer": fake.uri()
            },
            "response": {
                "status_code": status_code,
                "bytes": random.randint(50, 50000)
            },
            "url": uri,
            "version": "1.1"
        },
        "user_agent": {
            "original": fake.user_agent()
        },
        "message": f'{method} {uri} - {status_code}'
    }
    
    # Add geocode information if available
    if geocode:
        log_data["geocode"] = geocode
    
    return log_data


def run_log_generator(config: LogGeneratorConfig, metrics=None):
    """Main log generation loop."""
    print("Log generator started", flush=True)
    while True:
        # Check if DDoS simulation is active
        if config.ddos_active and time.time() < config.ddos_end_time:
            # Generate DDoS traffic - many requests from same region
            ddos_ip, ddos_geocode = generate_ip_from_region_with_geocode(config.ddos_region)
            burst_count = random.randint(50, 100)
            for _ in range(burst_count):
                log_entry = generate_log_entry(override_ip=ddos_ip, override_geocode=ddos_geocode)
                print(json.dumps(log_entry), flush=True)
                
                # Track metrics if available
                if metrics:
                    metrics['logs_generated_total'].inc()
                    status_code = str(log_entry['http']['response']['status_code'])
                    method = log_entry['http']['request']['method']
                    metrics['http_requests_total'].labels(method=method, status_code=status_code).inc()
                    
                    # Track geographic metrics
                    if 'geocode' in log_entry:
                        geo = log_entry['geocode']
                        metrics['http_requests_by_location'].labels(
                            country=geo['country_name'],
                            city=geo['city_name'],
                            latitude=str(geo['location']['lat']),
                            longitude=str(geo['location']['lon'])
                        ).inc()
            
            time.sleep(0.1)  # Short burst interval during DDoS
        elif config.ddos_active and time.time() >= config.ddos_end_time:
            # DDoS simulation ended
            config.ddos_active = False
            config.ddos_region = None
            if metrics:
                metrics['ddos_active_gauge'].set(0)
            print(f"DDoS simulation ended", flush=True)
        else:
            # Normal traffic generation
            log_entry = generate_log_entry()
            print(json.dumps(log_entry), flush=True)
            
            # Track metrics if available
            if metrics:
                metrics['logs_generated_total'].inc()
                status_code = str(log_entry['http']['response']['status_code'])
                method = log_entry['http']['request']['method']
                metrics['http_requests_total'].labels(method=method, status_code=status_code).inc()
                
                # Track geographic metrics
                if 'geocode' in log_entry:
                    geo = log_entry['geocode']
                    metrics['http_requests_by_location'].labels(
                        country=geo['country_name'],
                        city=geo['city_name'],
                        latitude=str(geo['location']['lat']),
                        longitude=str(geo['location']['lon'])
                    ).inc()
            
            time.sleep(random.uniform(config.min_interval, config.max_interval))
