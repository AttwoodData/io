# RAG Agent Factory - Phase 1

A simple, modular Flask application that provides a Q&A interface with local Ollama models.

## Quick Start

### Prerequisites
- Docker installed and running
- Ollama service running (localhost:11434)
- Ollama model downloaded (e.g., `ollama pull llama3.2:3b`)

### Development Workflow

```bash
# Quick deployment (build + run)
./dev.sh deploy

# Individual steps
./dev.sh build    # Build Docker image
./dev.sh run      # Run container
./dev.sh logs     # View logs
./dev.sh stop     # Stop container
./dev.sh clean    # Remove everything

# Check status
./dev.sh status
```

### Manual Docker Commands

```bash
# Build image
docker build -t rag-agent-factory .

# Run container
docker run -d -p 5001:5000 --name rag-dev-container rag-agent-factory

# View logs
docker logs -f rag-dev-container
```

## Architecture

```
rag-agent-factory/
├── app.py                    # Main Flask application
├── config/settings.py        # Configuration management
├── llm/ollama_client.py      # Ollama integration
├── utils/error_handlers.py   # Error handling utilities
├── templates/                # HTML templates (Metropolis font)
├── static/                   # CSS and JavaScript
└── dev.sh                   # Development workflow script
```

## Features

- ✅ Simple question → answer interface
- ✅ Local Ollama integration (FERPA compliant)
- ✅ Clean, modular code structure
- ✅ Responsive web interface with Metropolis font
- ✅ Docker containerization
- ✅ Health monitoring
- ✅ Error handling and logging

## Phase 1 Goals

- [x] Basic Ollama integration
- [x] Docker deployment
- [x] Clean web interface
- [x] Modular code structure
- [ ] External domain deployment

## Next Steps (Phase 2)

- Document processing pipeline development
- Multi-format file support (PDF, images, etc.)
- RAG capabilities with vector storage
- Conversation memory

## Configuration

Environment variables can be set for customization:

- `OLLAMA_HOST`: Ollama service host (default: localhost)
- `OLLAMA_PORT`: Ollama service port (default: 11434)
- `OLLAMA_MODEL`: Model to use (default: llama3.2:3b)
- `FLASK_DEBUG`: Enable debug mode (default: False)

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama service
ollama serve

# Pull a model if none available
ollama pull llama3.2:3b
```

### Docker Issues
```bash
# Check Docker status
docker info

# View container logs
./dev.sh logs

# Restart everything
./dev.sh clean
./dev.sh deploy
```

### Port Conflicts
```bash
# Use different port
docker run -d -p 5002:5000 --name rag-dev-container rag-agent-factory
```

## Development Principles

This project follows these core principles:

1. **Simplicity over complexity** - Prefer readable, verbose code over clever solutions
2. **Modular design** - Easy component swapping and upgrades  
3. **Educational value** - Code should be self-documenting and learning-focused
4. **Iterative development** - Build incrementally with testing at each step

## License

Open source - built for educational and development purposes.
