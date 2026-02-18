import { FastifyInstance } from "fastify";

export function requestLogger(app: FastifyInstance) {
  app.addHook("onRequest", async (request) => {
    request.log.info({
      method: request.method,
      url: request.url,
      ip: request.ip,
    }, "incoming request");
  });

  app.addHook("onResponse", async (request, reply) => {
    const responseTime = reply.elapsedTime || 0;
    request.log.info({
      method: request.method,
      url: request.url,
      statusCode: reply.statusCode,
      responseTime: `${responseTime.toFixed(2)}ms`,
    }, "request completed");
  });
}
