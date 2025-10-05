#!/bin/bash

# Claude Chat Project Structure Creator
# Run this from ~/io directory
# Creates all folders and empty files for the project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Claude Chat - Project Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if we're in the right directory
if [[ "$PWD" != *"/io" ]]; then
    echo -e "${YELLOW}⚠️  Warning: You should run this from ~/io directory${NC}"
    echo -e "Current directory: $PWD"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 1
    fi
fi

# Project directory name
PROJECT_DIR="claude-chat"

echo -e "${BLUE}📁 Creating project structure...${NC}"
echo ""

# Check if directory already exists
if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory '$PROJECT_DIR' already exists!${NC}"
    read -p "Do you want to remove it and start fresh? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$PROJECT_DIR"
        echo -e "${GREEN}✓${NC} Removed existing directory"
    else
        echo -e "${RED}✗${NC} Cancelled. Exiting..."
        exit 1
    fi
fi

# Create main project directory
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"
echo -e "${GREEN}✓${NC} Created main directory: $PROJECT_DIR"

# Create subdirectories
echo ""
echo -e "${BLUE}📂 Creating subdirectories...${NC}"

mkdir -p templates
echo -e "${GREEN}✓${NC} Created: templates/"

mkdir -p static/css
echo -e "${GREEN}✓${NC} Created: static/css/"

mkdir -p static/js
echo -e "${GREEN}✓${NC} Created: static/js/"

mkdir -p logs
echo -e "${GREEN}✓${NC} Created: logs/"

# Create empty files in root directory
echo ""
echo -e "${BLUE}📄 Creating root-level files...${NC}"

touch app.py
echo -e "${GREEN}✓${NC} Created: app.py"

touch wsgi.py
echo -e "${GREEN}✓${NC} Created: wsgi.py"

touch requirements.txt
echo -e "${GREEN}✓${NC} Created: requirements.txt"

touch Dockerfile
echo -e "${GREEN}✓${NC} Created: Dockerfile"

touch docker-compose.yml
echo -e "${GREEN}✓${NC} Created: docker-compose.yml"

touch .dockerignore
echo -e "${GREEN}✓${NC} Created: .dockerignore"

touch .gitignore
echo -e "${GREEN}✓${NC} Created: .gitignore"

touch .env.example
echo -e "${GREEN}✓${NC} Created: .env.example"

touch quick-deploy.sh
chmod +x quick-deploy.sh
echo -e "${GREEN}✓${NC} Created: quick-deploy.sh (executable)"

touch README.md
echo -e "${GREEN}✓${NC} Created: README.md"

# Create template files
echo ""
echo -e "${BLUE}🎨 Creating template files...${NC}"

touch templates/index.html
echo -e "${GREEN}✓${NC} Created: templates/index.html"

# Create static files
echo ""
echo -e "${BLUE}🎨 Creating static files...${NC}"

touch static/css/main.css
echo -e "${GREEN}✓${NC} Created: static/css/main.css"

touch static/js/chat.js
echo -e "${GREEN}✓${NC} Created: static/js/chat.js"

# Create a .gitkeep for logs directory
touch logs/.gitkeep
echo -e "${GREEN}✓${NC} Created: logs/.gitkeep"

# Create helpful file markers
echo ""
echo -e "${BLUE}📝 Creating file markers...${NC}"

# Add comments to empty files to indicate what goes in them
cat > app.py << 'EOF'
# Flask Application - Main Entry Point
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: app.py"

cat > wsgi.py << 'EOF'
# WSGI Entry Point
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: wsgi.py"

cat > requirements.txt << 'EOF'
# Python Dependencies
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: requirements.txt"

cat > Dockerfile << 'EOF'
# Docker Container Definition
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: Dockerfile"

cat > docker-compose.yml << 'EOF'
# Docker Compose Configuration
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: docker-compose.yml"

cat > .dockerignore << 'EOF'
# Docker Build Ignore List
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: .dockerignore"

cat > .gitignore << 'EOF'
# Git Ignore List - CRITICAL FOR SECURITY
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: .gitignore"

cat > .env.example << 'EOF'
# Environment Variables Template
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: .env.example"

cat > quick-deploy.sh << 'EOF'
#!/bin/bash
# Deployment Script
# Copy content from "ALL PROJECT FILES" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: quick-deploy.sh"

cat > templates/index.html << 'EOF'
<!-- Chat Interface HTML Template -->
<!-- Copy content from "ALL PROJECT FILES" artifact -->
EOF
echo -e "${GREEN}✓${NC} Added marker to: templates/index.html"

cat > static/css/main.css << 'EOF'
/* Main Stylesheet */
/* Copy content from "static/css/main.css - Complete Stylesheet" artifact */
EOF
echo -e "${GREEN}✓${NC} Added marker to: static/css/main.css"

cat > static/js/chat.js << 'EOF'
// Chat JavaScript
// Copy content from "static/js/chat.js - Complete JavaScript" artifact
EOF
echo -e "${GREEN}✓${NC} Added marker to: static/js/chat.js"

cat > README.md << 'EOF'
# Claude Chat Application

A secure, conversational interface to Claude API with context preservation.

## Setup Status

Project structure created. Next steps:

1. Copy content from artifacts into each file
2. Create .env file with API keys
3. Run deployment script

See conversation history for complete file contents.
EOF
echo -e "${GREEN}✓${NC} Added marker to: README.md"

# Summary
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Project Structure Created!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "📁 Location: $(pwd)"
echo ""
echo -e "${BLUE}📋 Files Created:${NC}"
echo ""
ls -1
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo "1️⃣  You are now in: claude-chat/"
echo ""
echo "2️⃣  Copy file contents from conversation:"
echo "   nano app.py           # Copy from 'ALL PROJECT FILES' artifact"
echo "   nano wsgi.py          # Copy from 'ALL PROJECT FILES' artifact"
echo "   nano requirements.txt # Copy from 'ALL PROJECT FILES' artifact"
echo "   ... and so on for each file"
echo ""
echo "3️⃣  Create .env file:"
echo "   nano .env"
echo "   Add: ANTHROPIC_API_KEY=sk-ant-api03-your-key"
echo "   Add: SECRET_KEY=<generate-with-python>"
echo ""
echo "4️⃣  Deploy:"
echo "   ./quick-deploy.sh"
echo ""
echo -e "${GREEN}✅ Ready to populate files!${NC}"
echo ""