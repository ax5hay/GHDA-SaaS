import { FastifyInstance } from "fastify";
import { getServiceUrl, SERVICE_REGISTRY } from "@ghda-saas/config";

export async function healthRoutes(app: FastifyInstance) {
  app.get("/health", async () => {
    return { service: "api-gateway", status: "healthy" };
  });

  app.get("/health/services", async () => {
    const services = Object.keys(SERVICE_REGISTRY);
    const health: any = { gateway: "healthy", services: {} };

    for (const [serviceName, endpoint] of Object.entries(SERVICE_REGISTRY)) {
      try {
        const url = `http://${endpoint.host}:${endpoint.port}`;
        const startTime = Date.now();
        const response = await fetch(`${url}/health`, { 
          signal: AbortSignal.timeout(3000) 
        });
        const latencyMs = Date.now() - startTime;
        
        health.services[serviceName] = {
          status: response.ok ? "healthy" : "unhealthy",
          latencyMs,
        };
      } catch (err) {
        health.services[serviceName] = { 
          status: "unhealthy", 
          latencyMs: 0,
          error: err instanceof Error ? err.message : "Unknown error"
        };
      }
    }

    return health;
  });
}
