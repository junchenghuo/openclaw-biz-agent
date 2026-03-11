export type Locale = 'zh-CN' | 'en-US';

export type I18nKey =
  | 'title'
  | 'subtitle'
  | 'username'
  | 'password'
  | 'captcha'
  | 'captchaPlaceholder'
  | 'login'
  | 'refreshCaptcha'
  | 'captchaHint'
  | 'rememberMe'
  | 'error_required'
  | 'error_param_invalid'
  | 'error_invalid_credentials'
  | 'error_captcha_invalid'
  | 'error_captcha_expired'
  | 'error_rate_limited'
  | 'error_server'
  | 'network_error'
  | 'login_success';

const dict: Record<Locale, Record<I18nKey, string>> = {
  'zh-CN': {
    title: '欢迎登录',
    subtitle: '请输入账号、密码与验证码',
    username: '账号',
    password: '密码',
    captcha: '验证码',
    captchaPlaceholder: '请输入验证码',
    login: '登录',
    refreshCaptcha: '换一张',
    captchaHint: '看不清？点击验证码更换',
    rememberMe: '记住我',

    error_required: '请填写完整信息',
    error_param_invalid: '请检查输入内容',
    error_invalid_credentials: '账号或密码错误',
    error_captcha_invalid: '验证码错误，请重试',
    error_captcha_expired: '验证码已过期，请重新获取',
    error_rate_limited: '操作过于频繁，请稍后再试',
    error_server: '服务开小差了，请稍后再试',
    network_error: '网络异常，请检查连接',
    login_success: '登录成功'
  },
  'en-US': {
    title: 'Welcome back',
    subtitle: 'Sign in with your credentials',
    username: 'Username',
    password: 'Password',
    captcha: 'Captcha',
    captchaPlaceholder: 'Enter captcha',
    login: 'Sign in',
    refreshCaptcha: 'Refresh',
    captchaHint: "Can't read it? Click to refresh",
    rememberMe: 'Remember me',

    error_required: 'Please complete the form',
    error_param_invalid: 'Please check your input',
    error_invalid_credentials: 'Invalid username or password',
    error_captcha_invalid: 'Captcha is incorrect',
    error_captcha_expired: 'Captcha expired, please refresh',
    error_rate_limited: 'Too many requests, try again later',
    error_server: 'Server error, please try again later',
    network_error: 'Network error',
    login_success: 'Signed in'
  }
};

export function createI18n(locale: Locale) {
  const table = dict[locale] ?? dict['zh-CN'];
  return (key: I18nKey) => table[key] ?? key;
}
