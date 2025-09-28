#!/bin/bash

# RAG Agent Factory - Development Script
# Quick development workflow automation

echo "🚀 RAG Agent Factory - Development Workflow"
echo "==========================================="

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
}

# Function to check if Ollama is running
check_ollama() {
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "⚠️  Ollama service not detected on localhost:11434"
        echo "   Make sure Ollama is running: ollama serve"
        echo "   Or update OLLAMA_HOST in config if running elsewhere"
    else
        echo "✅ Ollama service detected"
    fi
}

# Main development workflow
case "${1:-build}" in
    "build")
        echo "🔨 Building Docker image..."
        check_docker
        docker build -t rag-agent-factory .
        ;;
    "run")
        echo "🏃 Starting development container..."
        check_docker
        check_ollama
        docker rm -f rag-dev-container 2>/dev/null || true
        docker run -d -p 5001:5000 --name rag-dev-container --restart unless-stopped rag-agent-factory
        echo "✅ Container started at http://localhost:5001"
        echo "📊 View logs: ./dev.sh logs"
        ;;
    "deploy")
        echo "🚀 Full deployment (build + run)..."
        check_docker
        check_ollama
        docker rm -f rag-dev-container 2>/dev/null || true
        docker build -t rag-agent-factory .
        docker run -d -p 5001:5000 --name rag-dev-container --restart unless-stopped rag-agent-factory
        echo "✅ Deployment complete at http://localhost:5001"
        sleep 2
        echo "📋 Testing health endpoint..."
        curl -s http://localhost:5001/health | python3 -m json.tool || echo "Health check failed"
        ;;
    "logs")
        echo "📋 Viewing container logs..."
        docker logs -f rag-dev-container
        ;;
    "stop")
        echo "🛑 Stopping development container..."
        docker rm -f rag-dev-container
        echo "✅ Container stopped"
        ;;
    "status")
        echo "📊 Container status:"
        docker ps | grep rag-dev-container || echo "Container not running"
        echo ""
        echo "🏥 Health check:"
        curl -s http://localhost:5001/health | python3 -m json.tool 2>/dev/null || echo "Health check failed"
        ;;
    "clean")
        echo "🧹 Cleaning up..."
        docker rm -f rag-dev-container 2>/dev/null || true
        docker rmi rag-agent-factory 2>/dev/null || true
        echo "✅ Cleanup complete"
        ;;
    "help")
        echo "📖 Available commands:"
        echo "  ./dev.sh build   - Build Docker image"
        echo "  ./dev.sh run     - Run container (requires build first)"
        echo "  ./dev.sh deploy  - Build and run (one command)"
        echo "  ./dev.sh logs    - View container logs"
        echo "  ./dev.sh stop    - Stop container"
        echo "  ./dev.sh status  - Check container and health status"
        echo "  ./dev.sh clean   - Remove container and image"
        echo "  ./dev.sh help    - Show this help"
        ;;
    *)
        echo "❓ Unknown command: $1"
        echo "📖 Run './dev.sh help' for available commands"
        exit 1
        ;;
esac
