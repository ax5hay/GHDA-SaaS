export interface AuthenticatedUser {
    userId: string;
    tenantId: string;
    email: string;
    role: string;
}
export declare function verifyJWT(token: string): AuthenticatedUser | null;
export declare function generateJWT(user: AuthenticatedUser): string;
export declare function generateRefreshToken(user: AuthenticatedUser): string;
//# sourceMappingURL=index.d.ts.map