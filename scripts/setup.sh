#!/bin/bash
# Setup script for GHDA-SaaS

set -e

echo "🚀 GHDA-SaaS Setup Script"
echo "=========================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."
command -v pnpm >/dev/null 2>&1 || { echo "❌ pnpm not found. Install with: npm install -g pnpm"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ docker not found"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ python3 not found"; exit 1; }
echo "✅ All prerequisites met"
echo ""

# Install Node dependencies
echo "📦 Installing Node dependencies..."
pnpm install
echo "✅ Node dependencies installed"
echo ""

# Build shared packages
echo "🔨 Building shared packages..."
pnpm run build --filter=@ghda-saas/config --filter=@ghda-saas/logging --filter=@ghda-saas/auth
echo "✅ Shared packages built"
echo ""

# Install Python database package
echo "🐍 Installing Python database package..."
cd packages/db
python3 -m pip install -e . --quiet || echo "⚠️  Python package installation needs manual setup"
cd ../..
echo "✅ Python setup complete"
echo ""

# Start infrastructure
echo "🐳 Starting infrastructure services..."
docker-compose -f infra/docker/docker-compose.yml up -d postgres redis minio prometheus grafana
echo "⏳ Waiting for services to be ready..."
sleep 10
echo "✅ Infrastructure services started"
echo ""

# Verify infrastructure
echo "🔍 Verifying infrastructure..."
docker-compose -f infra/docker/docker-compose.yml ps
echo ""

echo "✅ Setup Complete!"
echo ""
echo "Next steps:"
echo "  1. Start services: pnpm dev"
echo "  2. Check health: curl http://localhost:3000/health"
echo "  3. Access Grafana: http://localhost:3001 (admin/admin)"
echo "  4. Access Prometheus: http://localhost:9090"
echo ""
