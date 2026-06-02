#!/bin/bash

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ ${1}${NC}"
}

# Parse arguments
TEST_MODE=false
COMPOSE_ARGS=""

for arg in "$@"; do
    if [ "$arg" = "--test" ]; then
        TEST_MODE=true
    else
        COMPOSE_ARGS="$COMPOSE_ARGS $arg"
    fi
done

if [ "$TEST_MODE" = true ]; then
    print_header "🧪 TEST MODE - SQLite + Default Admin"
    print_info "Database: Local SQLite (finalisthub_test.db)"
    print_info "Admin Account: username=admin, password=admin"
    print_info "Client: http://localhost:5173"
    print_info "Server: http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
    echo ""
    docker compose --env-file .env.test up $COMPOSE_ARGS
else
    print_header "🚀 PRODUCTION MODE - SQLiteCloud"
    print_info "Database: SQLiteCloud"
    print_info "Client: http://localhost:5173"
    print_info "Server: http://localhost:8000"
    print_info "API Docs: http://localhost:8000/docs"
    echo ""
    docker compose up $COMPOSE_ARGS
fi

