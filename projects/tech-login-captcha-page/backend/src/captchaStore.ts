import crypto from 'node:crypto';
import Redis from 'ioredis';

export type CaptchaRecord = {
  captchaId: string;
  codeHash: string;
  expireAtMs: number;
  clientKeyHash?: string;
  ipPrefix?: string;
  remainAttempts: number;
};

export type CaptchaIssueResult = {
  captchaId: string;
  codePlain: string;
  expireInSec: number;
};

export type CaptchaVerifyResult =
  | { ok: true }
  | { ok: false; reason: 'NOT_FOUND_OR_USED' | 'EXPIRED' | 'BIND_MISMATCH' | 'CODE_MISMATCH'; remainAttempts?: number };

export interface CaptchaStore {
  issue(params: { ttlSec: number; remainAttempts: number; clientKey?: string; ip?: string }): Promise<CaptchaIssueResult>;
  verifyOnce(params: { captchaId: string; code: string; clientKey?: string; ip?: string }): Promise<CaptchaVerifyResult>;
}

function sha256(input: string) {
  return crypto.createHash('sha256').update(input).digest('hex');
}

function ipPrefix(ip?: string) {
  if (!ip) return undefined;
  // simple /24 prefix for IPv4; for IPv6 just hash full ip (less likely used in demo)
  const m = ip.match(/^(\d+\.\d+\.\d+)\.(\d+)$/);
  if (m) return `${m[1]}.0/24`;
  return sha256(ip).slice(0, 12);
}

function genCaptchaId() {
  return `cpt_${crypto.randomBytes(16).toString('hex')}`;
}

function genCode(len = 4) {
  const alphabet = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'; // avoid 0O1I
  let out = '';
  for (let i = 0; i < len; i++) out += alphabet[Math.floor(Math.random() * alphabet.length)];
  return out;
}

export class MemoryCaptchaStore implements CaptchaStore {
  private map = new Map<string, CaptchaRecord>();

  async issue(params: { ttlSec: number; remainAttempts: number; clientKey?: string; ip?: string }): Promise<CaptchaIssueResult> {
    const captchaId = genCaptchaId();
    const codePlain = genCode(4);
    const now = Date.now();
    const record: CaptchaRecord = {
      captchaId,
      codeHash: sha256(codePlain.toUpperCase()),
      expireAtMs: now + params.ttlSec * 1000,
      clientKeyHash: params.clientKey ? sha256(params.clientKey) : undefined,
      ipPrefix: ipPrefix(params.ip),
      remainAttempts: params.remainAttempts
    };
    this.map.set(captchaId, record);
    return { captchaId, codePlain, expireInSec: params.ttlSec };
  }

  async verifyOnce(params: { captchaId: string; code: string; clientKey?: string; ip?: string }): Promise<CaptchaVerifyResult> {
    const record = this.map.get(params.captchaId);
    if (!record) return { ok: false, reason: 'NOT_FOUND_OR_USED' };

    const now = Date.now();
    if (now > record.expireAtMs) {
      this.map.delete(params.captchaId);
      return { ok: false, reason: 'EXPIRED' };
    }

    // weak bind (clientKey is recommended; ip prefix optional)
    if (record.clientKeyHash && (!params.clientKey || sha256(params.clientKey) !== record.clientKeyHash)) {
      this.map.delete(params.captchaId); // one-time; treat bind mismatch as used
      return { ok: false, reason: 'BIND_MISMATCH' };
    }

    if (record.ipPrefix && ipPrefix(params.ip) !== record.ipPrefix) {
      this.map.delete(params.captchaId);
      return { ok: false, reason: 'BIND_MISMATCH' };
    }

    const codeOk = sha256(params.code.toUpperCase()) === record.codeHash;

    // one-time semantics: *any* verification attempt consumes the captchaId.
    // If you want multi-attempt, replace this with decrement & keep until 0.
    this.map.delete(params.captchaId);

    if (!codeOk) {
      return { ok: false, reason: 'CODE_MISMATCH', remainAttempts: Math.max(0, record.remainAttempts - 1) };
    }

    return { ok: true };
  }
}

export class RedisCaptchaStore implements CaptchaStore {
  constructor(private redis: Redis, private keyPrefix = 'captcha:') {}

  async issue(params: { ttlSec: number; remainAttempts: number; clientKey?: string; ip?: string }): Promise<CaptchaIssueResult> {
    const captchaId = genCaptchaId();
    const codePlain = genCode(4);
    const now = Date.now();
    const rec: CaptchaRecord = {
      captchaId,
      codeHash: sha256(codePlain.toUpperCase()),
      expireAtMs: now + params.ttlSec * 1000,
      clientKeyHash: params.clientKey ? sha256(params.clientKey) : undefined,
      ipPrefix: ipPrefix(params.ip),
      remainAttempts: params.remainAttempts
    };

    const key = this.keyPrefix + captchaId;
    await this.redis.set(key, JSON.stringify(rec), 'EX', params.ttlSec);
    return { captchaId, codePlain, expireInSec: params.ttlSec };
  }

  async verifyOnce(params: { captchaId: string; code: string; clientKey?: string; ip?: string }): Promise<CaptchaVerifyResult> {
    const key = this.keyPrefix + params.captchaId;
    const raw = await this.redis.get(key);
    if (!raw) return { ok: false, reason: 'NOT_FOUND_OR_USED' };

    // one-time: delete first to prevent replay/race
    await this.redis.del(key);

    const rec = JSON.parse(raw) as CaptchaRecord;
    const now = Date.now();
    if (now > rec.expireAtMs) return { ok: false, reason: 'EXPIRED' };

    if (rec.clientKeyHash && (!params.clientKey || sha256(params.clientKey) !== rec.clientKeyHash)) {
      return { ok: false, reason: 'BIND_MISMATCH' };
    }

    if (rec.ipPrefix && ipPrefix(params.ip) !== rec.ipPrefix) return { ok: false, reason: 'BIND_MISMATCH' };

    const ok = sha256(params.code.toUpperCase()) === rec.codeHash;
    if (!ok) return { ok: false, reason: 'CODE_MISMATCH', remainAttempts: Math.max(0, rec.remainAttempts - 1) };

    return { ok: true };
  }
}
