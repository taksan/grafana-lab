#!/bin/bash

echo "🚀 Starting Grafana + Prometheus Lab..."
echo ""

# Start services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Lab is ready!"
    echo ""
    echo "📊 Access the services:"
    echo "   - Grafana:            http://localhost:3001 (admin/admin)"
    echo "   - Prometheus:         http://localhost:9090"
    echo "   - Loki:               http://localhost:3100"
    echo "   - Promtail:           http://localhost:9080"
    echo "   - Traffic Generator:  http://localhost:9001"
    echo "   - API Docs:           http://localhost:9001/docs"
    echo "   - User Database:      http://localhost:9500"
    echo "   - Server Assignment:  http://localhost:9600"
    echo ""
    echo "📈 View logs:"
    echo "   docker-compose logs -f traffic-generator"
    echo ""
    echo "🛑 Stop the lab:"
    echo "   docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Error starting services. Check logs with:"
    echo "   docker-compose logs"
fi
