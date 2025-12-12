#!/bin/bash
#
# RPGChat.AI - Quick Start Script
# Launches the application in either Development or Docker mode
#
# Usage:
#   ./start.sh           # Development mode (default)
#   ./start.sh --docker  # Full Docker deployment
#   ./start.sh -h        # Show help
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
MODE="dev"
while [[ $# -gt 0 ]]; do
    case $1 in
        --docker|-d)
            MODE="docker"
            shift
            ;;
        --help|-h)
            echo -e "${BLUE}🎭 RPGChat.AI - Quick Start Script${NC}"
            echo ""
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  (no args)     Development mode - runs backend/frontend locally with DB in Docker"
            echo "  --docker, -d  Docker mode - runs everything in Docker containers"
            echo "  --help, -h    Show this help message"
            echo ""
            echo "Development Mode (default):"
            echo "  - Database runs in Docker"
            echo "  - Backend runs locally with hot-reload (uv run fastapi dev)"
            echo "  - Frontend runs locally with hot-reload (npm run dev)"
            echo "  - Best for active development"
            echo ""
            echo "Docker Mode:"
            echo "  - All services run in Docker containers"
            echo "  - Production-like environment"
            echo "  - Best for testing deployment or demos"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}🎭 RPGChat.AI - Starting Application${NC}"
echo "============================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

#####################################
# DOCKER MODE
#####################################
if [ "$MODE" == "docker" ]; then
    echo -e "${CYAN}📦 Mode: Docker Deployment${NC}"
    echo ""
    
    # Build and start all containers
    echo -e "${YELLOW}🔨 Building and starting all services...${NC}"
    docker compose up --build -d
    
    # Wait for services to be healthy
    echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
    sleep 10
    
    # Run migrations
    echo -e "${YELLOW}🔄 Running database migrations...${NC}"
    docker compose exec -T backend alembic upgrade head 2>/dev/null || true
    
    # Restart backend to trigger auto-seeding (after fresh migrations)
    echo -e "${YELLOW}🔄 Restarting backend to apply seeds...${NC}"
    docker compose restart backend
    sleep 5
    
    # Check status
    echo ""
    docker compose ps
    
    # Display summary
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}🎉 RPGChat.AI is now running in Docker!${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo -e "  ${BLUE}Frontend:${NC}  http://localhost:5173"
    echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
    echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
    echo -e "  ${BLUE}Database:${NC}  localhost:5433"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  docker compose logs -f      # View logs"
    echo "  docker compose down         # Stop services"
    echo "  docker compose down -v      # Stop and reset database"
    echo ""
    exit 0
fi

#####################################
# DEVELOPMENT MODE (default)
#####################################
echo -e "${CYAN}📦 Mode: Development${NC}"
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed. Install it from: https://docs.astral.sh/uv/${NC}"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed. Install Node.js from: https://nodejs.org/${NC}"
    exit 1
fi

# Step 1: Start Database
echo -e "${YELLOW}📦 Step 1: Starting PostgreSQL database...${NC}"
docker compose up -d db
sleep 2

# Check if database is ready
echo -e "${YELLOW}   Waiting for database to be ready...${NC}"
until docker compose exec -T db pg_isready -U rpgchat > /dev/null 2>&1; do
    sleep 1
done
echo -e "${GREEN}   ✅ Database is ready${NC}"

# Step 2: Install backend dependencies (if needed)
echo -e "\n${YELLOW}📦 Step 2: Syncing backend dependencies...${NC}"
uv sync --quiet
echo -e "${GREEN}   ✅ Backend dependencies ready${NC}"

# Step 3: Run database migrations
echo -e "\n${YELLOW}🔄 Step 3: Running database migrations...${NC}"
cd back-end && uv run alembic upgrade head && cd ..
echo -e "${GREEN}   ✅ Migrations complete${NC}"

# Step 4: Install frontend dependencies (if needed)
echo -e "\n${YELLOW}📦 Step 4: Installing frontend dependencies...${NC}"
cd front-end && npm install --silent && cd ..
echo -e "${GREEN}   ✅ Frontend dependencies ready${NC}"

# Step 5: Start Backend (in background)
echo -e "\n${YELLOW}🚀 Step 5: Starting backend server...${NC}"
uv run fastapi dev back-end/app/main.py --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
sleep 3

# Check if backend started
if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Backend running at http://127.0.0.1:8000${NC}"
else
    echo -e "${YELLOW}   ⏳ Backend starting... (may take a few seconds)${NC}"
fi

# Step 6: Start Frontend (in background)
echo -e "\n${YELLOW}🎨 Step 6: Starting frontend server...${NC}"
cd front-end && npm run dev &
FRONTEND_PID=$!
cd ..
sleep 3
echo -e "${GREEN}   ✅ Frontend running at http://localhost:5173${NC}"

# Display summary
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}🎉 RPGChat.AI is now running!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  ${BLUE}Frontend:${NC}  http://localhost:5173"
echo -e "  ${BLUE}Backend:${NC}   http://127.0.0.1:8000"
echo -e "  ${BLUE}API Docs:${NC}  http://127.0.0.1:8000/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Handle shutdown
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ Services stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait
