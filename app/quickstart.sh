#!/bin/bash

# Text-to-SQL Agent Quick Start Script
# This script helps you get started with the application

set -e

echo "=================================="
echo "Text-to-SQL Agent - Quick Start"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo "Checking prerequisites..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker found${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose found${NC}"

# Check if .env file exists
echo ""
echo "Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo "Creating .env from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env created${NC}"
    echo ""
    echo -e "${YELLOW}⚠ IMPORTANT: Edit .env and add your API keys:${NC}"
    echo "  - OPENAI_API_KEY (for OpenAI)"
    echo "  - OR GEMINI_API_KEY (for Google Gemini)"
    echo ""
    echo "Then run this script again."
    exit 1
fi
echo -e "${GREEN}✓ .env file found${NC}"

# Check if API key is configured
if ! grep -q "^OPENAI_API_KEY=sk-" .env && ! grep -q "^GEMINI_API_KEY=" .env; then
    echo -e "${RED}✗ No valid API key found in .env${NC}"
    echo "Please add either OPENAI_API_KEY or GEMINI_API_KEY to .env"
    exit 1
fi
echo -e "${GREEN}✓ API key configured${NC}"

# Start services
echo ""
echo "Starting services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✓ PostgreSQL is running${NC}"
else
    echo -e "${RED}✗ PostgreSQL failed to start${NC}"
    docker-compose logs postgres
    exit 1
fi

if docker-compose ps | grep -q "app.*Up"; then
    echo -e "${GREEN}✓ Application is running${NC}"
else
    echo -e "${RED}✗ Application failed to start${NC}"
    docker-compose logs app
    exit 1
fi

# Show access URLs
echo ""
echo "=================================="
echo -e "${GREEN}✓ Services started successfully!${NC}"
echo "=================================="
echo ""
echo "Access the application:"
echo "  🎨 Streamlit UI: ${GREEN}http://localhost:8501${NC}"
echo "  📚 API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo "  💓 Health Check: ${GREEN}http://localhost:8000/health${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:      docker-compose logs -f app"
echo "  Stop services:  docker-compose down"
echo "  Rebuild:        docker-compose up --build"
echo ""
echo "First time?"
echo "  1. Open http://localhost:8501 in your browser"
echo "  2. Try a sample query like:"
echo '     "What are the top 5 customers by total order value?"'
echo ""
