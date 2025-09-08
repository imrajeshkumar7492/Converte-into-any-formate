#!/bin/bash

# Converte Pro Startup Script
# This script helps you start the Converte Pro application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within timeout"
    return 1
}

# Function to show help
show_help() {
    echo "Converte Pro Startup Script"
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  dev         Start development environment"
    echo "  prod        Start production environment"
    echo "  test        Run tests"
    echo "  clean       Clean up containers and volumes"
    echo "  logs        Show logs"
    echo "  status      Show service status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev      # Start development environment"
    echo "  $0 prod     # Start production environment"
    echo "  $0 test     # Run all tests"
    echo "  $0 clean    # Clean up everything"
}

# Function to start development environment
start_dev() {
    print_status "Starting Converte Pro development environment..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check if ports are available
    if port_in_use 3000; then
        print_warning "Port 3000 is already in use. Frontend might not start properly."
    fi
    
    if port_in_use 8000; then
        print_warning "Port 8000 is already in use. Backend might not start properly."
    fi
    
    # Create necessary directories
    mkdir -p backend/uploads backend/processed backend/temp backend/logs
    
    # Start services
    print_status "Starting services with Docker Compose..."
    docker-compose up -d --build
    
    # Wait for services to be ready
    print_status "Waiting for services to start..."
    sleep 10
    
    # Check service health
    if wait_for_service "http://localhost:8000/api/" "Backend API"; then
        print_success "Backend API is running at http://localhost:8000"
    fi
    
    if wait_for_service "http://localhost:3000" "Frontend"; then
        print_success "Frontend is running at http://localhost:3000"
    fi
    
    print_success "Development environment is ready!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "To view logs: $0 logs"
    echo "To stop: docker-compose down"
}

# Function to start production environment
start_prod() {
    print_status "Starting Converte Pro production environment..."
    
    # Check if production environment file exists
    if [ ! -f "docker-compose.prod.yml" ]; then
        print_error "Production configuration not found. Please create docker-compose.prod.yml"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "backend/.env" ]; then
        print_warning "No .env file found. Creating from template..."
        cp backend/.env.example backend/.env 2>/dev/null || {
            print_error "No .env.example found. Please create backend/.env with your configuration."
            exit 1
        }
    fi
    
    # Start production services
    print_status "Starting production services..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    print_success "Production environment started!"
    echo ""
    echo "🌐 Application: https://yourdomain.com"
    echo "📊 Monitoring: http://localhost:3001 (Grafana)"
    echo "📈 Metrics: http://localhost:9090 (Prometheus)"
}

# Function to run tests
run_tests() {
    print_status "Running Converte Pro tests..."
    
    # Check if backend test script exists
    if [ -f "backend/test_conversion.py" ]; then
        print_status "Running backend conversion tests..."
        cd backend
        python test_conversion.py
        cd ..
    else
        print_warning "Backend test script not found"
    fi
    
    # Run Docker Compose integration tests
    if [ -f ".github/workflows/docker-compose.yml" ]; then
        print_status "Running integration tests..."
        docker-compose -f docker-compose.yml up --abort-on-container-exit
    fi
    
    print_success "Tests completed!"
}

# Function to clean up
clean_up() {
    print_status "Cleaning up Converte Pro environment..."
    
    # Stop and remove containers
    docker-compose down -v 2>/dev/null || true
    docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
    
    # Remove images
    docker rmi converte-pro_backend converte-pro_frontend 2>/dev/null || true
    
    # Clean up volumes
    docker volume prune -f
    
    # Clean up temporary files
    rm -rf backend/uploads/* backend/processed/* backend/temp/* backend/logs/*
    
    print_success "Cleanup completed!"
}

# Function to show logs
show_logs() {
    print_status "Showing Converte Pro logs..."
    
    if [ "$1" = "backend" ]; then
        docker-compose logs -f backend
    elif [ "$1" = "frontend" ]; then
        docker-compose logs -f frontend
    elif [ "$1" = "worker" ]; then
        docker-compose logs -f worker
    else
        docker-compose logs -f
    fi
}

# Function to show status
show_status() {
    print_status "Converte Pro Service Status:"
    echo ""
    
    # Check Docker Compose services
    if docker-compose ps >/dev/null 2>&1; then
        docker-compose ps
    else
        print_warning "No Docker Compose services running"
    fi
    
    echo ""
    
    # Check service health
    if curl -s -f "http://localhost:8000/api/" >/dev/null 2>&1; then
        print_success "Backend API: ✅ Running"
    else
        print_error "Backend API: ❌ Not responding"
    fi
    
    if curl -s -f "http://localhost:3000" >/dev/null 2>&1; then
        print_success "Frontend: ✅ Running"
    else
        print_error "Frontend: ❌ Not responding"
    fi
}

# Main script logic
case "${1:-dev}" in
    "dev")
        start_dev
        ;;
    "prod")
        start_prod
        ;;
    "test")
        run_tests
        ;;
    "clean")
        clean_up
        ;;
    "logs")
        show_logs "$2"
        ;;
    "status")
        show_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown option: $1"
        echo ""
        show_help
        exit 1
        ;;
esac