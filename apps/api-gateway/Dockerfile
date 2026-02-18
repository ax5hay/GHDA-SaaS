FROM node:22-slim AS builder
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@10.28.1

# Copy workspace files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig.base.json turbo.json ./

# Copy packages
COPY packages ./packages

# Copy api-gateway
COPY apps/api-gateway ./apps/api-gateway

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build packages and api-gateway
RUN pnpm run build --filter=@ghda-saas/config --filter=@ghda-saas/logging --filter=@ghda-saas/auth
RUN pnpm run build --filter=@ghda-saas/api-gateway

FROM node:22-slim
WORKDIR /app

# Copy node_modules and built files
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./
COPY --from=builder /app/pnpm-workspace.yaml ./
COPY --from=builder /app/packages ./packages
COPY --from=builder /app/apps/api-gateway/dist ./apps/api-gateway/dist
COPY --from=builder /app/apps/api-gateway/package.json ./apps/api-gateway/

WORKDIR /app/apps/api-gateway
EXPOSE 3000

CMD ["node", "dist/index.js"]
