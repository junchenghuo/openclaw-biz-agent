import type { ApiError, CaptchaResponse, LoginRequest, LoginSuccess } from './types';

type CaptchaStoreItem = {
  code: string;
  expiresAt: number;
};

const store = new Map<string, CaptchaStoreItem>();

function now() {
  return Date.now();
}

function randomCode(len: number) {
  const chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';
  let out = '';
  for (let i = 0; i < len; i++) out += chars[Math.floor(Math.random() * chars.length)];
  return out;
}

function drawCaptchaImage(code: string, w = 120, h = 44) {
  const canvas = document.createElement('canvas');
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;

  // background
  const g = ctx.createLinearGradient(0, 0, w, h);
  g.addColorStop(0, 'rgba(255,255,255,0.12)');
  g.addColorStop(1, 'rgba(94,231,255,0.08)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);

  // noise lines
  for (let i = 0; i < 5; i++) {
    ctx.strokeStyle = `rgba(255,255,255,${0.15 + Math.random() * 0.15})`;
    ctx.beginPath();
    ctx.moveTo(Math.random() * w, Math.random() * h);
    ctx.lineTo(Math.random() * w, Math.random() * h);
    ctx.stroke();
  }

  // text
  ctx.save();
  ctx.font = '700 22px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto';
  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.textBaseline = 'middle';
  const spacing = w / (code.length + 1);
  for (let i = 0; i < code.length; i++) {
    const ch = code[i];
    const x = spacing * (i + 1);
    const y = h / 2;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((Math.random() - 0.5) * 0.35);
    ctx.fillText(ch, -7, 0);
    ctx.restore();
  }
  ctx.restore();

  // dots
  for (let i = 0; i < 24; i++) {
    ctx.fillStyle = `rgba(34,211,238,${0.15 + Math.random() * 0.2})`;
    ctx.beginPath();
    ctx.arc(Math.random() * w, Math.random() * h, Math.random() * 1.6 + 0.4, 0, Math.PI * 2);
    ctx.fill();
  }

  return canvas.toDataURL('image/png');
}

export async function mockGetCaptcha(): Promise<CaptchaResponse> {
  const captchaId = `cpt_${crypto.randomUUID()}`;
  const codeLength = 4;
  const code = randomCode(codeLength);
  const expireIn = 120;
  const image = drawCaptchaImage(code);
  store.set(captchaId, { code: code.toLowerCase(), expiresAt: now() + expireIn * 1000 });

  return {
    captchaId,
    imageType: 'png',
    image,
    expireIn,
    codeLength,
    caseSensitive: false
  };
}

function error(code: ApiError['code'], message?: string): ApiError {
  return { code, message: message || code };
}

export async function mockLogin(req: LoginRequest): Promise<LoginSuccess> {
  // Rate limit / lockout can be extended later
  if (!req.username || !req.password) {
    throw { status: 400, error: error('PARAM_INVALID') };
  }
  if (!req.captchaId || !req.captchaCode) {
    throw { status: 401, error: error('CAPTCHA_REQUIRED') };
  }

  const item = store.get(req.captchaId);
  // one-time credential: remove on any attempt
  store.delete(req.captchaId);

  if (!item) {
    throw { status: 401, error: error('CAPTCHA_EXPIRED') };
  }
  if (now() > item.expiresAt) {
    throw { status: 401, error: error('CAPTCHA_EXPIRED') };
  }

  const code = (req.captchaCode || '').toLowerCase().trim();
  if (code !== item.code) {
    throw { status: 401, error: error('CAPTCHA_INVALID') };
  }

  // demo credential
  if (!(req.username === 'admin' && req.password === 'admin123')) {
    throw { status: 401, error: error('AUTH_INVALID_CREDENTIALS') };
  }

  return {
    token: `mock_${crypto.randomUUID()}`,
    tokenType: 'Bearer',
    expireIn: 7200,
    user: { id: 'u_1', name: '管理员' }
  };
}
