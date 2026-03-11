import { useMemo } from 'react';
import LoginCard from './components/LoginCard';
import ParticleBackground from './components/ParticleBackground';
import { createI18n, type Locale } from './utils/i18n';
import styles from './styles/app.module.css';

export default function App() {
  // 预留 i18n：后续可改为从路由/用户偏好读取
  const locale: Locale = 'zh-CN';
  const t = useMemo(() => createI18n(locale), [locale]);

  return (
    <div className={styles.page}>
      <ParticleBackground />
      <div className={styles.center}>
        <LoginCard t={t} />
        <div className={styles.footer}>© {new Date().getFullYear()} Tech Login Demo</div>
      </div>
    </div>
  );
}
