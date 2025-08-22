#!/bin/bash

# Production startup script for Pine2Py CryptoLab
set -e

echo "🚀 Starting Pine2Py CryptoLab in Production Mode"

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

# Check backend
if curl -f http://localhost:5001/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose logs backend
fi

# Check frontend
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend health check failed"
    docker-compose logs frontend
fi

echo ""
echo "🎉 Pine2Py CryptoLab is running!"
echo ""
echo "🌐 Frontend: http://localhost"
echo "🔧 Backend API: http://localhost:5001"
echo "📊 Market Data: http://localhost:5001/api/market/overview"
echo "⚡ Backtesting: http://localhost:5001/api/backtests/health"
echo ""
echo "📋 To view logs: docker-compose logs -f [service-name]"
echo "🛑 To stop: docker-compose down"
echo "🔄 To restart: docker-compose restart [service-name]"
echo ""
echo "📈 Happy trading strategy development!"