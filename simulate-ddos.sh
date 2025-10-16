#!/bin/bash

# Default values
DURATION=60
REGION=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--duration)
            DURATION="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -d, --duration SECONDS    Duration of DDoS simulation (default: 60)"
            echo "  -r, --region REGION       Region to simulate from (optional)"
            echo "  -h, --help                Show this help message"
            echo ""
            echo "Available regions:"
            echo "  - Europe"
            echo "  - Asia"
            echo "  - South America"
            echo "  - Africa"
            echo "  - Australia"
            echo "  - North America"
            echo ""
            echo "Examples:"
            echo "  $0 -d 120                    # 2-minute DDoS from random region"
            echo "  $0 -d 60 -r Asia             # 1-minute DDoS from Asia"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "🔥 Simulating DDoS attack..."
echo "   Duration: ${DURATION} seconds"
if [ -n "$REGION" ]; then
    echo "   Region: $REGION"
    PAYLOAD="{\"duration_seconds\": $DURATION, \"region\": \"$REGION\"}"
else
    echo "   Region: Random"
    PAYLOAD="{\"duration_seconds\": $DURATION}"
fi
echo ""

# Send request
RESPONSE=$(curl -s -X POST http://localhost:8001/simulate_ddos \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Check if successful
if echo "$RESPONSE" | grep -q "success"; then
    SELECTED_REGION=$(echo "$RESPONSE" | grep -o '"region":"[^"]*"' | cut -d'"' -f4)
    echo "✅ DDoS simulation started from $SELECTED_REGION"
    echo ""
    echo "📊 Monitor the attack in Grafana: http://localhost:3001"
    echo "📈 Watch metrics in Prometheus: http://localhost:9090"
else
    echo "❌ Failed to start DDoS simulation"
    echo "Response: $RESPONSE"
fi
