FROM node:20-alpine AS builder
WORKDIR /app

# Copy workspace files
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy frontend
COPY frontend/admin-dashboard/package.json frontend/admin-dashboard/
COPY frontend/admin-dashboard ./frontend/admin-dashboard

# Install pnpm
RUN npm install -g pnpm@10.28.1

# Install dependencies
RUN pnpm install --frozen-lockfile

# Build
WORKDIR /app/frontend/admin-dashboard
RUN pnpm build

FROM node:20-alpine
WORKDIR /app

# Copy built files
COPY --from=builder /app/frontend/admin-dashboard/.next ./.next
COPY --from=builder /app/frontend/admin-dashboard/public ./public
COPY --from=builder /app/frontend/admin-dashboard/package.json ./
COPY --from=builder /app/frontend/admin-dashboard/next.config.js ./
COPY --from=builder /app/node_modules ./node_modules

EXPOSE 3002
CMD ["npm", "start"]
