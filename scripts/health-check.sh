#!/bin/bash

# Health check script for the Loan Onboarding API
set -e

# Configuration
API_URL=${API_URL:-"http://localhost:8000"}
TIMEOUT=${TIMEOUT:-30}
RETRY_COUNT=${RETRY_COUNT:-3}
RETRY_DELAY=${RETRY_DELAY:-5}

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[HEALTH CHECK]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check API health
check_api_health() {
    local url="$1/health"
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" --max-time "$TIMEOUT" 2>/dev/null || echo "HTTPSTATUS:000")
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed -E 's/HTTPSTATUS:[0-9]*$//')
    
    if [ "$http_code" = "200" ]; then
        print_status "API health check passed ✓"
        echo "Response: $body"
        return 0
    else
        print_error "API health check failed (HTTP $http_code)"
        return 1
    fi
}

# Function to check database connectivity
check_database() {
    local url="$1/api/v1/health/database"
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" --max-time "$TIMEOUT" 2>/dev/null || echo "HTTPSTATUS:000")
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        print_status "Database connectivity check passed ✓"
        return 0
    else
        print_warning "Database connectivity check failed (HTTP $http_code)"
        return 1
    fi
}

# Function to check external services
check_external_services() {
    local url="$1/api/v1/health/external"
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" --max-time "$TIMEOUT" 2>/dev/null || echo "HTTPSTATUS:000")
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        print_status "External services check passed ✓"
        return 0
    else
        print_warning "External services check failed (HTTP $http_code)"
        return 1
    fi
}

# Function to check metrics endpoint
check_metrics() {
    local url="$1/metrics"
    local response
    local http_code
    
    response=$(curl -s -w "HTTPSTATUS:%{http_code}" "$url" --max-time "$TIMEOUT" 2>/dev/null || echo "HTTPSTATUS:000")
    http_code=$(echo "$response" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        print_status "Metrics endpoint accessible ✓"
        return 0
    else
        print_warning "Metrics endpoint not accessible (HTTP $http_code)"
        return 1
    fi
}

# Main health check function
run_health_check() {
    local api_url="$1"
    local attempt=1
    local max_attempts="$RETRY_COUNT"
    
    print_status "Starting health check for $api_url"
    print_status "Timeout: ${TIMEOUT}s, Retries: $max_attempts"
    
    while [ $attempt -le $max_attempts ]; do
        print_status "Attempt $attempt/$max_attempts"
        
        # Basic health check
        if check_api_health "$api_url"; then
            # Additional checks
            check_database "$api_url"
            check_external_services "$api_url"
            check_metrics "$api_url"
            
            print_status "Overall health check completed ✓"
            return 0
        else
            if [ $attempt -lt $max_attempts ]; then
                print_warning "Retrying in ${RETRY_DELAY} seconds..."
                sleep "$RETRY_DELAY"
            fi
        fi
        
        ((attempt++))
    done
    
    print_error "Health check failed after $max_attempts attempts"
    return 1
}

# Function to check container health
check_container_health() {
    print_status "Checking Docker container health..."
    
    # Check if containers are running
    if docker-compose ps | grep -q "Up (healthy)"; then
        print_status "Containers are healthy ✓"
    elif docker-compose ps | grep -q "Up"; then
        print_warning "Containers are running but health status unknown"
    else
        print_error "Some containers are not running"
        docker-compose ps
        return 1
    fi
}

# Function to show comprehensive status
show_comprehensive_status() {
    print_status "=== Comprehensive Health Status ==="
    
    # Container status
    check_container_health
    
    # API health
    run_health_check "$API_URL"
    
    # Resource usage
    print_status "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Handle script arguments
case "$1" in
    "api")
        run_health_check "$API_URL"
        ;;
    "containers")
        check_container_health
        ;;
    "full")
        show_comprehensive_status
        ;;
    *)
        echo "Usage: $0 {api|containers|full}"
        echo ""
        echo "Commands:"
        echo "  api        - Check API health endpoints"
        echo "  containers - Check Docker container health"
        echo "  full       - Run comprehensive health check"
        echo ""
        echo "Environment variables:"
        echo "  API_URL      - API base URL (default: http://localhost:8000)"
        echo "  TIMEOUT      - Request timeout in seconds (default: 30)"
        echo "  RETRY_COUNT  - Number of retry attempts (default: 3)"
        echo "  RETRY_DELAY  - Delay between retries in seconds (default: 5)"
        exit 1
        ;;
esac
