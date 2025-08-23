#!/bin/bash

# Epic 7 Production startup script for PineOpt
set -e

echo "🚀 Starting PineOpt Epic 7 in Production Mode"
echo "📋 Features: Testing, Documentation, Performance, Monitoring"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Docker Compose is not installed. Please install it first."
    exit 1
fi

# Set up environment
if [ ! -f .env ]; then
    echo "📝 Creating production environment file..."
    cp .env.production .env
    echo "⚠️ Please edit .env file with your production settings before running again"
    exit 1
fi

# Create necessary directories
mkdir -p database outputs/logs uploads/strategies monitoring

# Build and start services
echo "🔨 Building Docker images..."
docker-compose build --no-cache

echo "📦 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check Epic 7 backend
if curl -f http://localhost:5007/api/health > /dev/null 2>&1; then
    echo "✅ Epic 7 Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend
fi

# Check frontend
if curl -f http://localhost:3000/health > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    docker-compose logs frontend
fi

# Check monitoring system
if curl -f http://localhost:5007/api/v1/monitoring/summary > /dev/null 2>&1; then
    echo "✅ Monitoring system is active"
else
    echo "⚠️ Monitoring system may need attention"
fi

echo ""
echo "🎉 PineOpt Epic 7 is running!"
echo ""
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:5007/api"
echo "📊 Market Data: http://localhost:5007/api/v1/market/overview"
echo "⚡ Backtesting: http://localhost:5007/api/v1/backtests"
echo "📈 Monitoring: http://localhost:5007/api/v1/monitoring/summary"
echo "📚 Documentation: http://localhost:5007/docs/"
echo ""
echo "📋 To view logs: docker-compose logs -f [service-name]"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart [service-name]"
echo ""
echo "🚀 Epic 7 Features Active:"
echo "  ✅ Comprehensive Testing Suite"
echo "  ✅ Interactive API Documentation"  
echo "  ✅ Performance Optimization & Caching"
echo "  ✅ Advanced Monitoring & Metrics"
echo ""
echo "📈 Happy trading strategy development with Epic 7!"