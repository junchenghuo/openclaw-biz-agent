import crypto from 'node:crypto';
import jwt from 'jsonwebtoken';

export type UserInfo = { id: string; name: string };

export async function verifyUsernamePassword(params: { username: string; password: string }) {
  // Demo stub:
  // - Integrate with existing user directory / password hash verification here.
  // - DO NOT log password.
  const demoUser = process.env.DEMO_USER ?? 'zhangsan';
  const demoPass = process.env.DEMO_PASS ?? '123456';

  if (params.username === demoUser && params.password === demoPass) {
    const user: UserInfo = { id: 'u_demo_1', name: '张三' };
    return { ok: true as const, user };
  }

  return { ok: false as const };
}

export function issueJwt(params: { userId: string; ttlSec: number }) {
  const secret = process.env.JWT_SECRET ?? crypto.randomBytes(32).toString('hex');
  // NOTE: for production, JWT_SECRET must be stable and stored securely.
  return jwt.sign({ sub: params.userId }, secret, { expiresIn: params.ttlSec });
}
