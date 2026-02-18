export interface ServiceEndpoint {
  host: string;
  port: number;
}

export function getServiceUrl(serviceName: string): string {
  const hostEnv = `${serviceName.toUpperCase().replace("-", "_")}_HOST`;
  const portEnv = `${serviceName.toUpperCase().replace("-", "_")}_PORT`;
  
  const host = process.env[hostEnv] || "localhost";
  const port = process.env[portEnv] || "8000";
  
  return `http://${host}:${port}`;
}

export const SERVICE_REGISTRY: Record<string, ServiceEndpoint> = {
  "document-service": {
    host: process.env.DOCUMENT_SERVICE_HOST || "document-service",
    port: parseInt(process.env.DOCUMENT_SERVICE_PORT || "8001", 10),
  },
  "report-service": {
    host: process.env.REPORT_SERVICE_HOST || "report-service",
    port: parseInt(process.env.REPORT_SERVICE_PORT || "8002", 10),
  },
  "analytics-service": {
    host: process.env.ANALYTICS_SERVICE_HOST || "analytics-service",
    port: parseInt(process.env.ANALYTICS_SERVICE_PORT || "8003", 10),
  },
  "processing-service": {
    host: process.env.PROCESSING_SERVICE_HOST || "processing-service",
    port: parseInt(process.env.PROCESSING_SERVICE_PORT || "8004", 10),
  },
};
