import type { ApiError } from './types';

export type ApiResult<T> =
  | { ok: true; data: T }
  | { ok: false; status: number; error: ApiError };

const API_BASE = import.meta.env.VITE_API_BASE || '';
const USE_MOCK = (import.meta.env.VITE_USE_MOCK || 'true').toLowerCase() === 'true';

export function getClientKey(): string {
  const key = 'tech_login_client_key_v1';
  let v = localStorage.getItem(key);
  if (!v) {
    v = `ck_${crypto.randomUUID()}`;
    localStorage.setItem(key, v);
  }
  return v;
}

export async function requestJson<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  const url = API_BASE ? `${API_BASE}${path}` : path;
  try {
    const resp = await fetch(url, {
      ...init,
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'X-Client-Key': getClientKey(),
        ...(init?.headers || {})
      }
    });

    const isJson = resp.headers.get('content-type')?.includes('application/json');
    if (resp.ok) {
      const data = (isJson ? await resp.json() : (await resp.text())) as T;
      return { ok: true, data };
    }

    const error = (isJson ? await resp.json() : { code: 'SERVER_ERROR', message: await resp.text() }) as ApiError;
    return { ok: false, status: resp.status, error };
  } catch {
    return { ok: false, status: 0, error: { code: 'NETWORK_ERROR', message: 'network error' } };
  }
}

export function shouldUseMock() {
  return USE_MOCK;
}
