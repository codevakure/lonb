#!/bin/bash

# Production deployment script for Loan Onboarding API
set -e

echo "🚀 Starting production deployment..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
VERSION=${VERSION:-latest}
COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from .env.example..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_warning "Please update .env file with your configuration before proceeding."
            exit 1
        else
            print_error ".env.example file not found. Cannot create .env file."
            exit 1
        fi
    fi
    
    print_status "Prerequisites check completed ✓"
}

# Function to validate environment variables
validate_environment() {
    print_status "Validating environment configuration..."
    
    # Source the .env file
    set -a
    source .env
    set +a
    
    # Check required environment variables
    REQUIRED_VARS=(
        "AWS_DEFAULT_REGION"
        "S3_BUCKET_NAME"
        "DYNAMODB_TABLE_NAME"
        "SECRET_KEY"
    )
    
    for var in "${REQUIRED_VARS[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set in .env file"
            exit 1
        fi
    done
    
    print_status "Environment validation completed ✓"
}

# Function to run tests
run_tests() {
    print_status "Running tests..."
    
    # Build test image
    docker build -t loan-api-test -f Dockerfile.test . || {
        print_error "Failed to build test image"
        exit 1
    }
    
    # Run tests
    docker run --rm \
        -v "$(pwd)":/app \
        -e ENV=test \
        loan-api-test \
        pytest tests/ -v --cov=. --cov-report=term-missing --cov-fail-under=85 || {
        print_error "Tests failed"
        exit 1
    }
    
    print_status "Tests completed successfully ✓"
}

# Function to build and deploy
deploy() {
    print_status "Building and deploying application..."
    
    # Build images
    docker-compose -f $COMPOSE_FILE build --build-arg VERSION=$VERSION || {
        print_error "Failed to build images"
        exit 1
    }
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose -f $COMPOSE_FILE down
    
    # Start services
    print_status "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d || {
        print_error "Failed to start services"
        exit 1
    }
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Health check
    if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_error "Health check failed"
        docker-compose -f $COMPOSE_FILE logs
        exit 1
    fi
    
    print_status "Deployment completed successfully ✓"
}

# Function to show service status
show_status() {
    print_status "Service Status:"
    docker-compose -f $COMPOSE_FILE ps
    
    print_status "Service Logs (last 20 lines):"
    docker-compose -f $COMPOSE_FILE logs --tail=20
}

# Function to cleanup
cleanup() {
    print_status "Cleaning up unused Docker resources..."
    docker system prune -f
    docker image prune -f
}

# Main execution
main() {
    print_status "Loan Onboarding API - Production Deployment"
    print_status "Environment: $ENVIRONMENT"
    print_status "Version: $VERSION"
    
    check_prerequisites
    validate_environment
    
    # Run tests only if not skipped
    if [ "$SKIP_TESTS" != "true" ]; then
        run_tests
    else
        print_warning "Skipping tests (SKIP_TESTS=true)"
    fi
    
    deploy
    show_status
    cleanup
    
    print_status "🎉 Deployment completed successfully!"
    print_status "API is available at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Health Check: http://localhost:8000/health"
}

# Handle script arguments
case "$1" in
    "deploy")
        main
        ;;
    "status")
        show_status
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose -f $COMPOSE_FILE down
        ;;
    "logs")
        docker-compose -f $COMPOSE_FILE logs -f
        ;;
    "cleanup")
        cleanup
        ;;
    *)
        echo "Usage: $0 {deploy|status|stop|logs|cleanup}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Run full deployment (tests + build + deploy)"
        echo "  status   - Show service status and logs"
        echo "  stop     - Stop all services"
        echo "  logs     - Follow service logs"
        echo "  cleanup  - Clean up unused Docker resources"
        echo ""
        echo "Environment variables:"
        echo "  ENVIRONMENT - Deployment environment (default: production)"
        echo "  VERSION     - Application version (default: latest)"
        echo "  SKIP_TESTS  - Skip tests (default: false)"
        exit 1
        ;;
esac
