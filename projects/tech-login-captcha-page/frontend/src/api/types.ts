export type CaptchaResponse = {
  captchaId: string;
  imageType: 'png' | 'jpeg' | string;
  image: string; // data url
  expireIn: number;
  codeLength: number;
  caseSensitive: boolean;
};

export type LoginRequest = {
  username: string;
  password: string;
  captchaId: string;
  captchaCode: string;
  rememberMe?: boolean;
  redirect?: string;
};

export type LoginSuccess = {
  token: string;
  tokenType: 'Bearer' | string;
  expireIn: number;
  refreshToken?: string;
  user?: {
    id: string;
    name: string;
  };
};

export type ApiError = {
  code:
    | 'PARAM_INVALID'
    | 'AUTH_INVALID_CREDENTIALS'
    | 'CAPTCHA_INVALID'
    | 'CAPTCHA_EXPIRED'
    | 'CAPTCHA_REQUIRED'
    | 'ACCOUNT_LOCKED'
    | 'RATE_LIMITED'
    | 'SERVER_ERROR'
    | string;
  message?: string;
  requestId?: string;
  details?: {
    remainAttempts?: number;
    captchaRefresh?: boolean;
  };
};
