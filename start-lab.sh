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
    echo "   - Grafana:        http://localhost:3001 (admin/admin)"
    echo "   - Prometheus:     http://localhost:9090"
    echo "   - Loki:           http://localhost:3100"
    echo "   - Alloy UI:       http://localhost:12345"
    echo "   - Log Generator:  http://localhost:8001"
    echo "   - API Docs:       http://localhost:8001/docs"
    echo ""
    echo "📈 View logs:"
    echo "   docker-compose logs -f log-generator"
    echo ""
    echo "🛑 Stop the lab:"
    echo "   docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Error starting services. Check logs with:"
    echo "   docker-compose logs"
fi
