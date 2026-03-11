import { requestJson, shouldUseMock } from './client';
import type { CaptchaResponse, LoginRequest, LoginSuccess, ApiError } from './types';
import { mockGetCaptcha, mockLogin } from './mock';

export async function getCaptcha(): Promise<CaptchaResponse> {
  if (shouldUseMock()) return await mockGetCaptcha();
  const r = await requestJson<CaptchaResponse>('/captcha');
  if (r.ok) return r.data;
  throw { status: r.status, error: r.error } as { status: number; error: ApiError };
}

export async function login(req: LoginRequest): Promise<LoginSuccess> {
  if (shouldUseMock()) return await mockLogin(req);
  const r = await requestJson<LoginSuccess>('/login', {
    method: 'POST',
    body: JSON.stringify(req)
  });
  if (r.ok) return r.data;
  throw { status: r.status, error: r.error } as { status: number; error: ApiError };
}
