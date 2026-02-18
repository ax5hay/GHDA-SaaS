#!/bin/bash
# Test all services

set -e

echo "🧪 Testing GHDA-SaaS Services"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=${3:-200}
    
    echo -n "Testing $name... "
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null || echo -e "\n000")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP $http_code)"
        if [ -n "$body" ]; then
            echo "   Response: $(echo "$body" | head -c 100)"
        fi
        return 0
    else
        echo -e "${RED}❌ FAILED${NC} (HTTP $http_code)"
        echo "   Expected: $expected_status"
        return 1
    fi
}

# Check infrastructure
echo "📦 Infrastructure Services"
echo "-------------------------"
test_endpoint "PostgreSQL" "http://localhost:5432" "000" || echo "   (PostgreSQL doesn't respond to HTTP, checking via Docker...)"
docker exec ghda-postgres pg_isready -U ghda_user -d ghda_saas >/dev/null 2>&1 && echo -e "PostgreSQL: ${GREEN}✅ OK${NC}" || echo -e "PostgreSQL: ${RED}❌ FAILED${NC}"

docker exec ghda-redis redis-cli ping >/dev/null 2>&1 && echo -e "Redis: ${GREEN}✅ OK${NC}" || echo -e "Redis: ${RED}❌ FAILED${NC}"

curl -s http://localhost:9000/minio/health/live >/dev/null 2>&1 && echo -e "MinIO: ${GREEN}✅ OK${NC}" || echo -e "MinIO: ${RED}❌ FAILED${NC}"
curl -s http://localhost:9090/-/healthy >/dev/null 2>&1 && echo -e "Prometheus: ${GREEN}✅ OK${NC}" || echo -e "Prometheus: ${RED}❌ FAILED${NC}"
curl -s http://localhost:3001/api/health >/dev/null 2>&1 && echo -e "Grafana: ${GREEN}✅ OK${NC}" || echo -e "Grafana: ${RED}❌ FAILED${NC}"

echo ""
echo "🚀 Application Services"
echo "----------------------"

# Test services
test_endpoint "API Gateway" "http://localhost:3000/health"
test_endpoint "Document Service" "http://localhost:8001/health"
test_endpoint "Report Service" "http://localhost:8002/health"
test_endpoint "Analytics Service" "http://localhost:8003/health"
test_endpoint "Processing Service" "http://localhost:8004/health"

echo ""
echo "🌐 Frontend"
echo "----------"
test_endpoint "Admin Dashboard" "http://localhost:3002" "200"

echo ""
echo "✅ Testing Complete!"
