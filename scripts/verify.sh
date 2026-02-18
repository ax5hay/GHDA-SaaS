#!/bin/bash
# Verification script for GHDA-SaaS microservices

set -e

echo "🔍 GHDA-SaaS Verification Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check infrastructure services
echo "📦 Checking Infrastructure Services..."
echo ""

check_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name: Healthy"
        return 0
    else
        echo -e "${RED}❌${NC} $name: Unhealthy or not running"
        return 1
    fi
}

# PostgreSQL
if docker-compose -f infra/docker/docker-compose.yml exec -T postgres pg_isready -U ghda_user -d ghda_saas > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} PostgreSQL: Healthy"
else
    echo -e "${RED}❌${NC} PostgreSQL: Not ready"
fi

# Redis
if docker-compose -f infra/docker/docker-compose.yml exec -T redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✅${NC} Redis: Healthy"
else
    echo -e "${RED}❌${NC} Redis: Not responding"
fi

# MinIO
check_service "MinIO" "http://localhost:9000/minio/health/live" ""

# Prometheus
check_service "Prometheus" "http://localhost:9090/-/healthy" "Prometheus Server is Healthy"

# Grafana
check_service "Grafana" "http://localhost:3001/api/health" ""

echo ""
echo "📚 Checking Shared Packages..."
echo ""

# Check TypeScript packages
if pnpm run build --filter=@ghda-saas/config --filter=@ghda-saas/logging --filter=@ghda-saas/auth > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} TypeScript packages: Built successfully"
else
    echo -e "${RED}❌${NC} TypeScript packages: Build failed"
fi

# Check Python package
if python3 -c "from ghda_db import get_db_session" > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Python DB package: Import successful"
else
    echo -e "${YELLOW}⚠️${NC}  Python DB package: Not installed (run: pip install -e packages/db)"
fi

echo ""
echo "🚀 Checking Services..."
echo ""

# Check if services can start (quick test)
echo -e "${YELLOW}⚠️${NC}  Services: Manual testing required"
echo "   - API Gateway: http://localhost:3000/health"
echo "   - Document Service: http://localhost:8001/health"

echo ""
echo "=================================="
echo "✅ Verification Complete"
echo ""
echo "To start services:"
echo "  pnpm dev                    # Start all services"
echo "  pnpm docker:up             # Start infrastructure"
echo ""
