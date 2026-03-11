export type ApiErrorCode =
  | 'PARAM_INVALID'
  | 'CAPTCHA_REQUIRED'
  | 'CAPTCHA_INVALID'
  | 'CAPTCHA_EXPIRED'
  | 'AUTH_INVALID_CREDENTIALS'
  | 'ACCOUNT_LOCKED'
  | 'RATE_LIMITED'
  | 'SERVER_ERROR';

export class ApiError extends Error {
  public readonly httpStatus: number;
  public readonly code: ApiErrorCode;
  public readonly details?: Record<string, unknown>;

  constructor(params: { httpStatus: number; code: ApiErrorCode; message: string; details?: Record<string, unknown> }) {
    super(params.message);
    this.httpStatus = params.httpStatus;
    this.code = params.code;
    this.details = params.details;
  }
}

export function badRequest(message: string, details?: Record<string, unknown>) {
  return new ApiError({ httpStatus: 400, code: 'PARAM_INVALID', message, details });
}

export function rateLimited(message = 'rate limited', details?: Record<string, unknown>) {
  return new ApiError({ httpStatus: 429, code: 'RATE_LIMITED', message, details });
}
