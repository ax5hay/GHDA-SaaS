import { FastifyInstance, FastifyRequest, FastifyReply } from "fastify";
import { getServiceUrl, SERVICE_REGISTRY } from "@ghda-saas/config";
import { verifyJWT } from "@ghda-saas/auth";

export async function proxyRoutes(app: FastifyInstance) {
  // Authentication middleware for protected routes
  app.addHook("onRequest", async (request: FastifyRequest, reply: FastifyReply) => {
    // Skip auth for health checks
    if (request.url.startsWith("/health")) {
      return;
    }

    const authHeader = request.headers.authorization;
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return reply.status(401).send({ error: "Unauthorized" });
    }

    const token = authHeader.substring(7);
    const user = verifyJWT(token);
    
    if (!user) {
      return reply.status(401).send({ error: "Invalid token" });
    }

    // Attach user to request
    (request as any).user = user;
  });

  // Proxy routes for each service
  for (const [prefix, serviceEndpoint] of Object.entries(SERVICE_REGISTRY)) {
    app.all(`/${prefix}/*`, async (request: FastifyRequest, reply: FastifyReply) => {
      const upstream = `http://${serviceEndpoint.host}:${serviceEndpoint.port}`;
      const path = (request.params as Record<string, string>)["*"];
      const url = `${upstream}/api/v1/${path ?? ""}`;
      const queryString = request.url.split("?")[1] || "";
      const fullUrl = queryString ? `${url}?${queryString}` : url;

      try {
        const headers: Record<string, string> = {
          "content-type": (request.headers["content-type"] as string) || "application/json",
        };

        // Forward auth headers
        if (request.headers.authorization) {
          headers.authorization = request.headers.authorization as string;
        }
        
        // Forward tenant ID
        if (request.headers["x-tenant-id"]) {
          headers["x-tenant-id"] = request.headers["x-tenant-id"] as string;
        } else if ((request as any).user) {
          headers["x-tenant-id"] = (request as any).user.tenantId;
        }

        // Forward request ID for tracing
        if (request.headers["x-request-id"]) {
          headers["x-request-id"] = request.headers["x-request-id"] as string;
        }

        const timeoutMs = 30000;
        const response = await fetch(fullUrl, {
          method: request.method,
          headers,
          body: request.method !== "GET" && request.method !== "HEAD"
            ? JSON.stringify(request.body ?? {})
            : undefined,
          signal: AbortSignal.timeout(timeoutMs),
        });

        const body = await response.text();
        reply.status(response.status).type("application/json").send(body);
      } catch (err) {
        request.log.error({ err, service: prefix, path }, "Upstream request failed");
        reply.status(502).send({
          error: "Bad Gateway",
          service: prefix,
          message: err instanceof Error ? err.message : "Unknown error",
        });
      }
    });
  }
}
