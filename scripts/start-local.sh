#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

DB_CONTAINER="looklive-db"
POSTGRES_PORT=5432
BACKEND_PORT=8000
FRONTEND_PORT=3000

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_success "Docker is running"
}

start_postgres() {
    if [ "$(docker ps -q -f name=$DB_CONTAINER)" ]; then
        log_warn "Database container '$DB_CONTAINER' already running"
        return 0
    fi

    if [ "$(docker ps -aq -f name=$DB_CONTAINER)" ]; then
        log_info "Starting existing container..."
        docker start $DB_CONTAINER
    else
        log_info "Starting PostgreSQL container..."
        docker run -d \
            --name $DB_CONTAINER \
            -p ${POSTGRES_PORT}:5432 \
            -e POSTGRES_USER=postgres \
            -e POSTGRES_PASSWORD=postgres \
            -e POSTGRES_DB=looklive \
            --health-cmd="pg_isready -U postgres -d looklive" \
            --health-interval=10s \
            --health-timeout=5s \
            --health-retries=5 \
            postgres:15-alpine
    fi

    log_success "PostgreSQL running on port $POSTGRES_PORT"
}

detect_terminal() {
    if command -v gnome-terminal &> /dev/null; then
        echo "gnome-terminal"
    elif command -v konsole &> /dev/null; then
        echo "konsole"
    elif command -v xfce4-terminal &> /dev/null; then
        echo "xfce4-terminal"
    elif command -v xterm &> /dev/null; then
        echo "xterm"
    else
        echo ""
    fi
}

start_backend() {
    log_info "Starting backend..."
    cd "$BACKEND_DIR"

    if [ ! -d ".venv" ]; then
        log_error "Virtual environment not found at $BACKEND_DIR/.venv"
        log_info "Creating virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -e .
    fi

    source .venv/bin/activate

    TERMINAL=$(detect_terminal)

    if [ -n "$TERMINAL" ]; then
        if [ "$TERMINAL" = "gnome-terminal" ]; then
            gnome-terminal -- bash -c "cd '$BACKEND_DIR' && source .venv/bin/activate && uvicorn main:app --reload --port $BACKEND_PORT; read"
        elif [ "$TERMINAL" = "konsole" ]; then
            konsole --hold -e "cd '$BACKEND_DIR' && source .venv/bin/activate && uvicorn main:app --reload --port $BACKEND_PORT"
        elif [ "$TERMINAL" = "xfce4-terminal" ]; then
            xfce4-terminal --hold -e "cd '$BACKEND_DIR' && source .venv/bin/activate && uvicorn main:app --reload --port $BACKEND_PORT"
        else
            xterm -hold -e "cd '$BACKEND_DIR' && source .venv/bin/activate && uvicorn main:app --reload --port $BACKEND_PORT" &
        fi
        log_success "Backend starting in new terminal on port $BACKEND_PORT"
    else
        log_warn "No terminal found, starting backend in background..."
        cd "$BACKEND_DIR"
        source .venv/bin/activate
        nohup uvicorn main:app --reload --port $BACKEND_PORT > /tmp/looklive-backend.log 2>&1 &
        echo $! > /tmp/looklive-backend.pid
        log_success "Backend started in background (PID: $(cat /tmp/looklive-backend.pid))"
    fi
}

start_frontend() {
    log_info "Starting frontend..."
    cd "$FRONTEND_DIR"

    if [ ! -d "node_modules" ]; then
        log_info "Installing frontend dependencies..."
        npm install
    fi

    TERMINAL=$(detect_terminal)

    if [ -n "$TERMINAL" ]; then
        if [ "$TERMINAL" = "gnome-terminal" ]; then
            gnome-terminal -- bash -c "cd '$FRONTEND_DIR' && npm run dev; read"
        elif [ "$TERMINAL" = "konsole" ]; then
            konsole --hold -e "cd '$FRONTEND_DIR' && npm run dev"
        elif [ "$TERMINAL" = "xfce4-terminal" ]; then
            xfce4-terminal --hold -e "cd '$FRONTEND_DIR' && npm run dev"
        else
            xterm -hold -e "cd '$FRONTEND_DIR' && npm run dev" &
        fi
        log_success "Frontend starting in new terminal on port $FRONTEND_PORT"
    else
        log_warn "No terminal found, starting frontend in background..."
        cd "$FRONTEND_DIR"
        nohup npm run dev > /tmp/looklive-frontend.log 2>&1 &
        echo $! > /tmp/looklive-frontend.pid
        log_success "Frontend started in background (PID: $(cat /tmp/looklive-frontend.pid))"
    fi
}

stop_services() {
    log_info "Stopping services..."

    if [ -f /tmp/looklive-backend.pid ]; then
        kill $(cat /tmp/looklive-backend.pid) 2>/dev/null || true
        rm /tmp/looklive-backend.pid
        log_info "Backend stopped"
    fi

    if [ -f /tmp/looklive-frontend.pid ]; then
        kill $(cat /tmp/looklive-frontend.pid) 2>/dev/null || true
        rm /tmp/looklive-frontend.pid
        log_info "Frontend stopped"
    fi

    if [ "$(docker ps -q -f name=$DB_CONTAINER)" ]; then
        docker stop $DB_CONTAINER 2>/dev/null || true
        log_info "Database stopped"
    fi

    log_success "All services stopped"
}

check_ports() {
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "Port $BACKEND_PORT is already in use (backend may be running)"
    fi
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_warn "Port $FRONTEND_PORT is already in use (frontend may be running)"
    fi
}

show_status() {
    echo ""
    echo "=== LookLive Status ==="
    echo ""

    if [ "$(docker ps -q -f name=$DB_CONTAINER)" ]; then
        log_success "PostgreSQL: Running on port $POSTGRES_PORT"
    else
        log_warn "PostgreSQL: Not running"
    fi

    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "Backend: Running on port $BACKEND_PORT"
    else
        log_warn "Backend: Not running"
    fi

    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "Frontend: Running on port $FRONTEND_PORT"
    else
        log_warn "Frontend: Not running"
    fi

    echo ""
    echo "URLs:"
    echo "  - Frontend: http://localhost:$FRONTEND_PORT"
    echo "  - Backend:  http://localhost:$BACKEND_PORT"
    echo "  - API Docs: http://localhost:$BACKEND_PORT/docs"
    echo "======================="
}

usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start all services (default)"
    echo "  stop      Stop all services"
    echo "  restart   Restart all services"
    echo "  status    Show service status"
    echo "  db        Start only PostgreSQL"
    echo ""
    echo "Examples:"
    echo "  $0         # Start all services"
    echo "  $0 status  # Check status"
    echo "  $0 stop    # Stop all services"
}

case "${1:-start}" in
    start)
        check_docker
        check_ports
        start_postgres
        start_backend
        start_frontend
        echo ""
        log_success "LookLive is starting..."
        show_status
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        check_docker
        start_postgres
        start_backend
        start_frontend
        show_status
        ;;
    status)
        show_status
        ;;
    db)
        check_docker
        start_postgres
        ;;
    *)
        usage
        exit 1
        ;;
esac