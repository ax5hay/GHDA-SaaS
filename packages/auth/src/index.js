import jwt from "jsonwebtoken";
export function verifyJWT(token) {
    try {
        const secret = process.env.JWT_SECRET || "your-secret-key-change-this-in-production";
        const decoded = jwt.verify(token, secret);
        return decoded;
    }
    catch {
        return null;
    }
}
export function generateJWT(user) {
    const secret = process.env.JWT_SECRET || "your-secret-key-change-this-in-production";
    const expiresInMinutes = process.env.ACCESS_TOKEN_EXPIRE_MINUTES
        ? parseInt(process.env.ACCESS_TOKEN_EXPIRE_MINUTES, 10)
        : 30;
    return jwt.sign(user, secret, { expiresIn: `${expiresInMinutes}m` });
}
export function generateRefreshToken(user) {
    const secret = process.env.JWT_SECRET || "your-secret-key-change-this-in-production";
    const expiresInDays = process.env.REFRESH_TOKEN_EXPIRE_DAYS
        ? parseInt(process.env.REFRESH_TOKEN_EXPIRE_DAYS, 10)
        : 7;
    return jwt.sign(user, secret, { expiresIn: `${expiresInDays}d` });
}
//# sourceMappingURL=index.js.map