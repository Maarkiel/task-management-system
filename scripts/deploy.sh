#!/bin/bash

# Task Manager Deployment Script
# This script handles the deployment of the Task Manager application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
ENV_FILE=".env"
BACKUP_DIR="backups"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file ($COMPOSE_FILE) not found."
        exit 1
    fi
    
    log_success "All requirements met."
}

setup_environment() {
    log_info "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f ".env.example" ]; then
            log_info "Creating .env file from .env.example..."
            cp .env.example .env
            log_warning "Please edit .env file with your configuration before running again."
            exit 1
        else
            log_error ".env file not found and no .env.example available."
            exit 1
        fi
    fi
    
    log_success "Environment setup complete."
}

backup_data() {
    log_info "Creating backup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Backup database if it exists
    if docker volume ls | grep -q "taskmanager_backend_data"; then
        BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
        docker run --rm -v taskmanager_backend_data:/data -v "$(pwd)/$BACKUP_DIR":/backup alpine tar czf "/backup/$(basename $BACKUP_FILE)" -C /data .
        log_success "Backup created: $BACKUP_FILE"
    else
        log_info "No existing data to backup."
    fi
}

build_images() {
    log_info "Building Docker images..."
    
    if command -v docker-compose &> /dev/null; then
        docker-compose build --no-cache
    else
        docker compose build --no-cache
    fi
    
    log_success "Images built successfully."
}

deploy_application() {
    log_info "Deploying application..."
    
    # Stop existing containers
    if command -v docker-compose &> /dev/null; then
        docker-compose down
        docker-compose up -d
    else
        docker compose down
        docker compose up -d
    fi
    
    log_success "Application deployed successfully."
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for backend health check
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:5000/api/health &> /dev/null; then
            log_success "Backend is ready."
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Backend failed to start within expected time."
            exit 1
        fi
        
        log_info "Waiting for backend... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    # Wait for frontend
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:3000 &> /dev/null; then
            log_success "Frontend is ready."
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Frontend failed to start within expected time."
            exit 1
        fi
        
        log_info "Waiting for frontend... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
}

show_status() {
    log_info "Application status:"
    
    if command -v docker-compose &> /dev/null; then
        docker-compose ps
    else
        docker compose ps
    fi
    
    echo ""
    log_success "Application is running!"
    log_info "Frontend: http://localhost:3000"
    log_info "Backend API: http://localhost:5000/api"
    log_info "API Documentation: http://localhost:5000/api/docs"
}

cleanup() {
    log_info "Cleaning up unused Docker resources..."
    docker system prune -f
    log_success "Cleanup complete."
}

# Main deployment process
main() {
    log_info "Starting Task Manager deployment..."
    
    check_requirements
    setup_environment
    
    # Create backup if not in CI/CD environment
    if [ -z "$CI" ]; then
        backup_data
    fi
    
    build_images
    deploy_application
    wait_for_services
    show_status
    
    if [ -z "$CI" ]; then
        cleanup
    fi
    
    log_success "Deployment completed successfully!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping application..."
        if command -v docker-compose &> /dev/null; then
            docker-compose down
        else
            docker compose down
        fi
        log_success "Application stopped."
        ;;
    "restart")
        log_info "Restarting application..."
        if command -v docker-compose &> /dev/null; then
            docker-compose restart
        else
            docker compose restart
        fi
        log_success "Application restarted."
        ;;
    "logs")
        if command -v docker-compose &> /dev/null; then
            docker-compose logs -f
        else
            docker compose logs -f
        fi
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_data
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|stop|restart|logs|status|backup|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application (default)"
        echo "  stop     - Stop the application"
        echo "  restart  - Restart the application"
        echo "  logs     - Show application logs"
        echo "  status   - Show application status"
        echo "  backup   - Create a backup of application data"
        echo "  cleanup  - Clean up unused Docker resources"
        exit 1
        ;;
esac

