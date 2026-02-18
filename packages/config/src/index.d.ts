export interface ServiceEndpoint {
    host: string;
    port: number;
}
export declare function getServiceUrl(serviceName: string): string;
export declare const SERVICE_REGISTRY: Record<string, ServiceEndpoint>;
//# sourceMappingURL=index.d.ts.map