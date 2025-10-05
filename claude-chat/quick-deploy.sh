#!/bin/bash
# Deployment Script
#!/bin/bash

# Claude Chat - Quick Deployment Script for Debian

set -e

echo "🚀 Claude Chat - Debian Nginx Deployment"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Check we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "docker-compose.yml not found. Run from project directory."
    exit 1
fi

echo ""
echo "📋 Pre-Deployment Checks"
echo "========================"

# Check Docker
if command -v docker &> /dev/null; then
    print_status "Docker installed: $(docker --version)"
else
    print_error "Docker not installed!"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    print_status "Docker Compose installed: $(docker-compose --version)"
else
    print_error "Docker Compose not installed!"
    exit 1
fi

# Check .env file
if [ -f ".env" ]; then
    if grep -q "your_api_key_here" .env; then
        print_error ".env has placeholder API key!"
        exit 1
    else
        print_status ".env configured"
    fi
else
    print_error ".env file missing!"
    exit 1
fi

# Check port 5002
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 5002 in use"
else
    print_status "Port 5002 available"
fi

echo ""
echo "🐳 Docker Deployment"
echo "===================="

# Build and deploy
print_info "Building Docker image..."
docker-compose build

print_info "Starting container..."
docker-compose up -d

sleep 5

# Check status
if docker ps | grep -q claude-chat; then
    print_status "Container running"
else
    print_error "Container not running!"
    docker-compose logs
    exit 1
fi

# Test health
print_info "Testing health endpoint..."
if curl -sf http://localhost:5002/health > /dev/null; then
    print_status "Health check passed"
else
    print_warning "Health check failed"
fi

echo ""
print_status "Setup complete!"
echo ""
echo "🔗 URLs:"
echo "   Internal: http://localhost:5002"
echo "   After Nginx: https://claude.attwoodanalytics.com"