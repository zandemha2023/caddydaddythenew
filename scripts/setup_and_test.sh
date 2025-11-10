#!/bin/bash
# Theo CAD - Setup and Test Script
# This script validates environment, dependencies, and runs tests

set -e

echo "=========================================="
echo "Theo CAD - Setup and Test"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo "ℹ $1"
}

# Change to project directory
cd "$(dirname "$0")/.."

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3.10+ required, found $PYTHON_VERSION"
    exit 1
fi
echo ""

# Step 2: Check if .env file exists
echo "Step 2: Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_info "Please edit .env file with your configuration (especially ANTHROPIC_API_KEY)"
    echo ""
fi

# Check for required environment variables
if [ -f ".env" ]; then
    source .env

    if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your-api-key-here" ]; then
        print_error "ANTHROPIC_API_KEY not set in .env file"
        print_info "Get your API key from: https://console.anthropic.com/"
        exit 1
    else
        print_success "ANTHROPIC_API_KEY found"
    fi

    if [ -z "$DATABASE_URL" ]; then
        print_warning "DATABASE_URL not set, using default"
    else
        print_success "DATABASE_URL configured"
    fi

    if [ -z "$REDIS_URL" ]; then
        print_warning "REDIS_URL not set, using default"
    else
        print_success "REDIS_URL configured"
    fi
fi
echo ""

# Step 3: Check dependencies
echo "Step 3: Checking dependencies..."
cd backend

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
fi

print_info "Activating virtual environment..."
source venv/bin/activate

print_info "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

print_success "Dependencies installed"
echo ""

# Step 4: Verify CadQuery installation
echo "Step 4: Verifying CadQuery installation..."
python3 -c "import cadquery as cq; print(f'CadQuery {cq.__version__} installed')" 2>&1 | grep -q "CadQuery" && \
    print_success "CadQuery verified" || \
    (print_error "CadQuery installation failed" && exit 1)
echo ""

# Step 5: Create output directories
echo "Step 5: Creating output directories..."
mkdir -p /tmp/theo-cad/uploads /tmp/theo-cad/outputs
print_success "Output directories created"
echo ""

# Step 6: Check database connection (optional)
echo "Step 6: Checking services..."
if command -v pg_isready &> /dev/null; then
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

    if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PORT" ]; then
        if pg_isready -h $DB_HOST -p $DB_PORT &> /dev/null; then
            print_success "PostgreSQL is accessible"
        else
            print_warning "PostgreSQL not accessible at $DB_HOST:$DB_PORT"
            print_info "You'll need PostgreSQL running for full functionality"
        fi
    fi
else
    print_warning "pg_isready not found, skipping PostgreSQL check"
fi

# Check Redis connection
if command -v redis-cli &> /dev/null; then
    REDIS_HOST=$(echo $REDIS_URL | sed -n 's!.*//\([^:]*\):.*!\1!p')
    REDIS_PORT=$(echo $REDIS_URL | sed -n 's!.*:\([0-9]*\)/.*!\1!p')

    if [ ! -z "$REDIS_HOST" ] && [ ! -z "$REDIS_PORT" ]; then
        if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping &> /dev/null; then
            print_success "Redis is accessible"
        else
            print_warning "Redis not accessible at $REDIS_HOST:$REDIS_PORT"
            print_info "You'll need Redis running for WebSocket streaming"
        fi
    fi
else
    print_warning "redis-cli not found, skipping Redis check"
fi
echo ""

# Step 7: Run basic import tests
echo "Step 7: Running import tests..."
python3 << EOF
import sys
try:
    from app.main import app
    print("✓ Main application imports successfully")

    from app.services.agents.requirements_agent_v2 import RequirementsAgentV2
    print("✓ Requirements Agent imports successfully")

    from app.services.agents.cad_agent_v2 import CADAgentV2
    print("✓ CAD Agent imports successfully")

    from app.services.agents.design_orchestrator import DesignOrchestrator
    print("✓ Design Orchestrator imports successfully")

    print("\nAll imports successful!")
    sys.exit(0)
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "All imports successful"
else
    print_error "Import tests failed"
    exit 1
fi
echo ""

# Step 8: Summary
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Start PostgreSQL (if not running):"
echo "   docker run -d -p 5432:5432 -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=theo_cad postgres:16"
echo ""
echo "2. Start Redis (if not running):"
echo "   docker run -d -p 6379:6379 redis:7-alpine"
echo ""
echo "3. Run database migrations:"
echo "   cd backend && alembic upgrade head"
echo ""
echo "4. Start the server:"
echo "   cd backend && uvicorn app.main:app --reload --port 8000"
echo ""
echo "5. Test the workflow:"
echo "   python scripts/test_design.py"
echo ""
echo "6. Run automated tests:"
echo "   cd backend && pytest tests/test_design_workflow.py -v"
echo ""
echo "=========================================="
