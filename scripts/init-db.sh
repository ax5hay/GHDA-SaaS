#!/bin/bash
# Initialize PostgreSQL database

set -e

echo "🗄️  Initializing PostgreSQL database..."

docker-compose -f infra/docker/docker-compose.yml exec -T postgres psql -U ghda_user -d postgres <<EOF
-- Create database if not exists
SELECT 'CREATE DATABASE ghda_saas'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'ghda_saas')\gexec

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ghda_saas TO ghda_user;
EOF

echo "✅ Database initialized"
