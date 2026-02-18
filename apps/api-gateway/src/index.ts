import Fastify from "fastify";
import cors from "@fastify/cors";
import helmet from "@fastify/helmet";
import rateLimit from "@fastify/rate-limit";
import websocket from "@fastify/websocket";
import { healthRoutes } from "./routes/health.js";
import { proxyRoutes } from "./routes/proxy.js";
import { requestLogger } from "./middleware/request-logger.js";
import { logger } from "@ghda-saas/logging";

const PORT = parseInt(process.env.API_GATEWAY_PORT || "3000", 10);
const HOST = process.env.API_GATEWAY_HOST || "0.0.0.0";

async function main() {
  const app = Fastify({
    logger: {
      level: process.env.LOG_LEVEL || "info",
    },
    requestIdHeader: "x-request-id",
    genReqId: () => crypto.randomUUID(),
  });

  // Security & middleware
  await app.register(helmet, { global: true });
  await app.register(cors, {
    origin: process.env.CORS_ORIGIN || "*",
    credentials: true,
  });
  await app.register(rateLimit, {
    max: parseInt(process.env.RATE_LIMIT_MAX || "200", 10),
    timeWindow: process.env.RATE_LIMIT_WINDOW || "1 minute",
  });
  await app.register(websocket);

  // Request logging
  requestLogger(app);

  // Routes
  await app.register(healthRoutes, { prefix: "/" });
  await app.register(proxyRoutes, { prefix: "/api/v1" });

  // Graceful shutdown
  const signals: NodeJS.Signals[] = ["SIGINT", "SIGTERM"];
  for (const signal of signals) {
    process.on(signal, async () => {
      app.log.info(`Received ${signal}, shutting down gracefully`);
      await app.close();
      process.exit(0);
    });
  }

  await app.listen({ port: PORT, host: HOST });
  app.log.info(`API Gateway started on ${HOST}:${PORT}`);
}

main().catch((err) => {
  console.error("Fatal startup error:", err);
  process.exit(1);
});
