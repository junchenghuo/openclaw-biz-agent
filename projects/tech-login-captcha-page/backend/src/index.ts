import Fastify from 'fastify';
import cookie from '@fastify/cookie';
import rateLimit from '@fastify/rate-limit';
import svgCaptcha from 'svg-captcha';
import Redis from 'ioredis';

import { ApiError, badRequest } from './errors.js';
import { MemoryCaptchaStore, RedisCaptchaStore } from './captchaStore.js';
import { issueJwt, verifyUsernamePassword } from './auth.js';

const app = Fastify({
  logger: {
    level: process.env.LOG_LEVEL ?? 'info'
  }
});

await app.register(cookie);

// Basic rate-limit (can be moved to gateway; this is service-level baseline)
await app.register(rateLimit, {
  global: false,
  keyGenerator: (req) => {
    const ip = req.ip;
    const clientKey = (req.headers['x-client-key'] as string | undefined) ?? '';
    return `${ip}|${clientKey}`;
  },
  errorResponseBuilder: (_req, context) => {
    return {
      code: 'RATE_LIMITED',
      message: 'rate limited',
      requestId: context.requestId
    };
  }
});

function requestIdOf(req: any) {
  return req.id;
}

function getClientKey(req: any) {
  const v = req.headers['x-client-key'];
  return typeof v === 'string' && v.trim() ? v.trim() : undefined;
}

function auditLog(event: string, fields: Record<string, unknown>) {
  // Keep it structured; avoid password/captchaCode plaintext.
  app.log.info({ event, ...fields });
}

const ttlSec = Number(process.env.CAPTCHA_TTL_SEC ?? 120);
const remainAttempts = Number(process.env.CAPTCHA_ATTEMPTS ?? 1);

const redisUrl = process.env.REDIS_URL;
const captchaStore = redisUrl
  ? new RedisCaptchaStore(new Redis(redisUrl), process.env.REDIS_CAPTCHA_PREFIX ?? 'captcha:')
  : new MemoryCaptchaStore();

app.get(
  '/captcha',
  {
    config: { rateLimit: { max: 60, timeWindow: '1 minute' } }
  },
  async (req, reply) => {
    reply.header('Cache-Control', 'no-store');

    const clientKey = getClientKey(req);

    const issue = await captchaStore.issue({ ttlSec, remainAttempts, clientKey, ip: req.ip });

    // Render svg image. (Store only hash; never store plaintext.)
    const svg = svgCaptcha(
      Object.assign(svgCaptcha.create({
        size: 4,
        ignoreChars: '0oO1iIlL',
        noise: 2,
        width: Number((req.query as any)?.w ?? 120),
        height: Number((req.query as any)?.h ?? 44)
      }), { text: issue.codePlain })
    ).data;

    auditLog('captcha_issued', {
      requestId: requestIdOf(req),
      ip: req.ip,
      clientKeyPresent: Boolean(clientKey),
      captchaId: issue.captchaId,
      expireIn: issue.expireInSec
    });

    return {
      captchaId: issue.captchaId,
      imageType: 'svg',
      image: `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`,
      expireIn: issue.expireInSec,
      codeLength: 4,
      caseSensitive: false
    };
  }
);

app.post(
  '/login',
  {
    config: { rateLimit: { max: 10, timeWindow: '1 minute' } }
  },
  async (req, reply) => {
    const body = req.body as any;

    const username = typeof body?.username === 'string' ? body.username.trim() : '';
    const password = typeof body?.password === 'string' ? body.password : '';
    const captchaId = typeof body?.captchaId === 'string' ? body.captchaId : '';
    const captchaCode = typeof body?.captchaCode === 'string' ? body.captchaCode.trim() : '';

    if (!username || !password) throw badRequest('username/password required');

    if (!captchaId || !captchaCode) {
      throw new ApiError({ httpStatus: 401, code: 'CAPTCHA_REQUIRED', message: 'captcha required', details: { captchaRefresh: true } });
    }

    const clientKey = getClientKey(req);

    // 1) verify captcha first (and consume it regardless of result)
    const captchaRes = await captchaStore.verifyOnce({ captchaId, code: captchaCode, clientKey, ip: req.ip });
    if (!captchaRes.ok) {
      const code =
        captchaRes.reason === 'EXPIRED'
          ? 'CAPTCHA_EXPIRED'
          : captchaRes.reason === 'CODE_MISMATCH'
            ? 'CAPTCHA_INVALID'
            : 'CAPTCHA_INVALID';

      auditLog('login_failed', {
        requestId: requestIdOf(req),
        ip: req.ip,
        username,
        result: 'fail',
        failCode: code
      });

      throw new ApiError({
        httpStatus: 401,
        code,
        message: code === 'CAPTCHA_EXPIRED' ? 'captcha expired' : 'captcha invalid',
        details: { remainAttempts: captchaRes.remainAttempts, captchaRefresh: true }
      });
    }

    // 2) verify credentials
    const authRes = await verifyUsernamePassword({ username, password });
    if (!authRes.ok) {
      auditLog('login_failed', {
        requestId: requestIdOf(req),
        ip: req.ip,
        username,
        result: 'fail',
        failCode: 'AUTH_INVALID_CREDENTIALS'
      });

      throw new ApiError({
        httpStatus: 401,
        code: 'AUTH_INVALID_CREDENTIALS',
        message: 'invalid credentials',
        details: { captchaRefresh: true }
      });
    }

    // 3) issue session (default: JWT bearer in JSON body)
    const sessionMode = process.env.SESSION_MODE ?? 'jwt'; // jwt|cookie
    const tokenTtlSec = Number(process.env.TOKEN_TTL_SEC ?? 7200);

    const token = issueJwt({ userId: authRes.user.id, ttlSec: tokenTtlSec });

    if (sessionMode === 'cookie') {
      reply.setCookie('sid', token, {
        path: '/',
        httpOnly: true,
        secure: true,
        sameSite: 'lax'
      });
    }

    auditLog('login_success', {
      requestId: requestIdOf(req),
      ip: req.ip,
      username,
      userId: authRes.user.id
    });

    return {
      token: sessionMode === 'jwt' ? token : undefined,
      tokenType: sessionMode === 'jwt' ? 'Bearer' : undefined,
      expireIn: tokenTtlSec,
      user: authRes.user
    };
  }
);

app.setErrorHandler((err, req, reply) => {
  const requestId = requestIdOf(req);

  if (err instanceof ApiError) {
    reply.status(err.httpStatus).send({
      code: err.code,
      message: err.message,
      requestId,
      details: err.details
    });
    return;
  }

  req.log.error({ err }, 'unhandled_error');
  reply.status(500).send({ code: 'SERVER_ERROR', message: 'server error', requestId });
});

const port = Number(process.env.PORT ?? 3000);
const host = process.env.HOST ?? '0.0.0.0';

app.listen({ port, host }).catch((e) => {
  app.log.error(e);
  process.exit(1);
});
