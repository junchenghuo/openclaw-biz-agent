import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type { ApiError } from '../api/types';
import { getCaptcha, login } from '../api';
import styles from './LoginCard.module.css';

type Props = {
  t: (key: any) => string;
};

type FieldErrors = Partial<Record<'username' | 'password' | 'captchaCode', string>>;

function mapError(t: Props['t'], code: string) {
  switch (code) {
    case 'PARAM_INVALID':
      return t('error_param_invalid');
    case 'AUTH_INVALID_CREDENTIALS':
      return t('error_invalid_credentials');
    case 'CAPTCHA_INVALID':
      return t('error_captcha_invalid');
    case 'CAPTCHA_EXPIRED':
      return t('error_captcha_expired');
    case 'CAPTCHA_REQUIRED':
      return t('error_required');
    case 'RATE_LIMITED':
      return t('error_rate_limited');
    case 'NETWORK_ERROR':
      return t('network_error');
    default:
      return t('error_server');
  }
}

export default function LoginCard({ t }: Props) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [captchaCode, setCaptchaCode] = useState('');
  const [rememberMe, setRememberMe] = useState(true);

  const [captchaId, setCaptchaId] = useState('');
  const [captchaImg, setCaptchaImg] = useState('');
  const [captchaLoading, setCaptchaLoading] = useState(false);
  const [submitLoading, setSubmitLoading] = useState(false);

  const [globalError, setGlobalError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [toast, setToast] = useState<string | null>(null);

  const lastFetchRef = useRef(0);

  const canSubmit = useMemo(() => {
    return username.trim() && password && captchaCode.trim() && captchaId && !submitLoading;
  }, [username, password, captchaCode, captchaId, submitLoading]);

  const fetchCaptcha = useCallback(async (reason?: 'init' | 'refresh' | 'auto') => {
    // 节流：避免连续点击导致 /captcha 被刷爆
    const now = Date.now();
    if (reason !== 'init' && now - lastFetchRef.current < 600) return;
    lastFetchRef.current = now;

    setCaptchaLoading(true);
    setGlobalError(null);
    try {
      const c = await getCaptcha();
      setCaptchaId(c.captchaId);
      setCaptchaImg(c.image);
      setCaptchaCode('');
      setFieldErrors((e) => ({ ...e, captchaCode: undefined }));
    } catch (e: any) {
      const err = (e?.error as ApiError) || { code: 'SERVER_ERROR' };
      setGlobalError(mapError(t, err.code));
    } finally {
      setCaptchaLoading(false);
    }
  }, [t]);

  useEffect(() => {
    fetchCaptcha('init');
  }, [fetchCaptcha]);

  const validate = () => {
    const fe: FieldErrors = {};
    if (!username.trim()) fe.username = t('error_required');
    if (!password) fe.password = t('error_required');
    if (!captchaCode.trim()) fe.captchaCode = t('error_required');
    setFieldErrors(fe);
    return Object.keys(fe).length === 0;
  };

  const onSubmit = async () => {
    setGlobalError(null);
    setToast(null);
    if (!validate()) {
      setGlobalError(t('error_required'));
      return;
    }

    setSubmitLoading(true);
    try {
      const r = await login({
        username: username.trim(),
        password,
        captchaId,
        captchaCode: captchaCode.trim(),
        rememberMe,
        redirect: '/'
      });
      // demo: 仅提示；真实项目里应保存 token / 跳转
      setToast(`${t('login_success')} · ${r.user?.name ?? ''}`.trim());
      setPassword('');
      await fetchCaptcha('auto');
    } catch (e: any) {
      const err = (e?.error as ApiError) || { code: 'SERVER_ERROR' };
      const msg = mapError(t, err.code);
      setGlobalError(msg);

      if (err.code === 'CAPTCHA_INVALID' || err.code === 'CAPTCHA_EXPIRED') {
        setFieldErrors((fe) => ({ ...fe, captchaCode: msg }));
      }
      if (err.code === 'AUTH_INVALID_CREDENTIALS') {
        setFieldErrors((fe) => ({ ...fe, password: msg }));
      }

      // 失败策略：401 的验证码相关/凭据错误 → 自动刷新验证码
      // 429 限流不要自动刷新，避免放大器
      const shouldAutoRefresh =
        err.code === 'CAPTCHA_INVALID' ||
        err.code === 'CAPTCHA_EXPIRED' ||
        err.code === 'AUTH_INVALID_CREDENTIALS' ||
        err.code === 'CAPTCHA_REQUIRED';

      if (shouldAutoRefresh && err.code !== 'RATE_LIMITED') {
        await fetchCaptcha('auto');
      }
    } finally {
      setSubmitLoading(false);
    }
  };

  return (
    <div className={styles.card} role="region" aria-label="login">
      <div className={styles.header}>
        <div className={styles.title}>{t('title')}</div>
        <div className={styles.subtitle}>{t('subtitle')}</div>
      </div>

      <form
        className={styles.form}
        onSubmit={(e) => {
          e.preventDefault();
          void onSubmit();
        }}
      >
        <label className={styles.field}>
          <span className={styles.label}>{t('username')}</span>
          <input
            className={styles.input}
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoComplete="username"
            inputMode="text"
            onBlur={() => {
              if (!username.trim()) setFieldErrors((fe) => ({ ...fe, username: t('error_required') }));
              else setFieldErrors((fe) => ({ ...fe, username: undefined }));
            }}
          />
          {fieldErrors.username ? <div className={styles.error}>{fieldErrors.username}</div> : null}
        </label>

        <label className={styles.field}>
          <span className={styles.label}>{t('password')}</span>
          <input
            className={styles.input}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            type="password"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                // allow enter submit
              }
            }}
            onBlur={() => {
              if (!password) setFieldErrors((fe) => ({ ...fe, password: t('error_required') }));
              else setFieldErrors((fe) => ({ ...fe, password: undefined }));
            }}
          />
          {fieldErrors.password ? <div className={styles.error}>{fieldErrors.password}</div> : null}
        </label>

        <div className={styles.field}>
          <span className={styles.label}>{t('captcha')}</span>
          <div className={styles.captchaRow}>
            <input
              className={styles.input}
              value={captchaCode}
              onChange={(e) => setCaptchaCode(e.target.value)}
              placeholder={t('captchaPlaceholder')}
              autoComplete="off"
              inputMode="text"
              onBlur={() => {
                if (!captchaCode.trim()) setFieldErrors((fe) => ({ ...fe, captchaCode: t('error_required') }));
                else setFieldErrors((fe) => ({ ...fe, captchaCode: undefined }));
              }}
            />
            <button
              type="button"
              className={styles.captchaBox}
              onClick={() => void fetchCaptcha('refresh')}
              disabled={captchaLoading}
              aria-label={t('refreshCaptcha')}
              title={t('refreshCaptcha')}
            >
              {captchaImg ? (
                <img className={styles.captchaImg} src={captchaImg} alt={t('captcha')} />
              ) : (
                <div className={styles.captchaSkeleton} />
              )}
              <span className={styles.captchaRefresh} aria-hidden="true">
                ↻
              </span>
            </button>
          </div>
          {fieldErrors.captchaCode ? <div className={styles.error}>{fieldErrors.captchaCode}</div> : null}
          <div className={styles.hint}>{t('captchaHint')}</div>
        </div>

        <label className={styles.remember}>
          <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} />
          <span>{t('rememberMe')}</span>
        </label>

        {globalError ? <div className={styles.globalError}>{globalError}</div> : null}
        {toast ? <div className={styles.toast}>{toast}</div> : null}

        <button className={styles.submit} type="submit" disabled={!canSubmit}>
          {submitLoading ? <span className={styles.spinner} aria-hidden="true" /> : null}
          {t('login')}
        </button>

        <div className={styles.demoHint}>
          Demo 账号：<code>admin</code> / <code>admin123</code>
        </div>
      </form>
    </div>
  );
}
