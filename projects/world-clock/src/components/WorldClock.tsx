import React from 'react';
import { ClockCard } from './ClockCard';
import { CountryConfig } from '../types';

const CLOCKS: CountryConfig[] = [
  {
    id: 'cn',
    country: '中国',
    city: '上海',
    timezone: 'Asia/Shanghai',
    primaryColor: '#E74C3C',
    secondaryColor: '#F39C12',
    decoration: '☁',
  },
  {
    id: 'jp',
    country: '日本',
    city: '东京',
    timezone: 'Asia/Tokyo',
    primaryColor: '#FF69B4',
    secondaryColor: '#FFB6C1',
    decoration: '🌸',
  },
  {
    id: 'kr',
    country: '韩国',
    city: '首尔',
    timezone: 'Asia/Seoul',
    primaryColor: '#3498DB',
    secondaryColor: '#2980B9',
    decoration: '☯',
  },
  {
    id: 'fr',
    country: '法国',
    city: '巴黎',
    timezone: 'Europe/Paris',
    primaryColor: '#9B59B6',
    secondaryColor: '#8E44AD',
    decoration: '🗼',
  },
  {
    id: 'gb',
    country: '英国',
    city: '伦敦',
    timezone: 'Europe/London',
    primaryColor: '#27AE60',
    secondaryColor: '#1E8449',
    decoration: '🕰',
  },
  {
    id: 'us-ny',
    country: '美国',
    city: '纽约',
    timezone: 'America/New_York',
    primaryColor: '#2980B9',
    secondaryColor: '#1A5276',
    decoration: '🗽',
  },
  {
    id: 'us-la',
    country: '美国',
    city: '洛杉矶',
    timezone: 'America/Los_Angeles',
    primaryColor: '#F1C40F',
    secondaryColor: '#D4AC0D',
    decoration: '⭐',
  },
  {
    id: 'au',
    country: '澳大利亚',
    city: '悉尼',
    timezone: 'Australia/Sydney',
    primaryColor: '#E67E22',
    secondaryColor: '#CA6F1E',
    decoration: '🦘',
  },
];

export const WorldClock: React.FC = () => {
  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0f0f2a 100%)',
        padding: '40px 20px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background effects */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `
            radial-gradient(circle at 20% 80%, rgba(120, 0, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(0, 200, 255, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(255, 100, 100, 0.05) 0%, transparent 70%)
          `,
          pointerEvents: 'none',
        }}
      />

      <div style={{ position: 'relative', zIndex: 1, maxWidth: '1200px', margin: '0 auto' }}>
        <header style={{ textAlign: 'center', marginBottom: '50px' }}>
          <h1
            style={{
              fontSize: 'clamp(32px, 5vw, 48px)',
              fontWeight: 700,
              color: '#fff',
              margin: 0,
              textShadow: `
                0 0 20px rgba(255,255,255,0.3),
                0 0 40px rgba(100,100,255,0.2)
              `,
              letterSpacing: '4px',
            }}
          >
            🌍 WORLD CLOCK
          </h1>
          <p
            style={{
              color: '#888',
              margin: '12px 0 0',
              fontSize: '16px',
              letterSpacing: '2px',
            }}
          >
            全球实时时钟 · 八个时区
          </p>
        </header>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '30px',
            justifyItems: 'center',
          }}
        >
          {CLOCKS.map((config) => (
            <ClockCard key={config.id} config={config} />
          ))}
        </div>

        <footer
          style={{
            textAlign: 'center',
            marginTop: '60px',
            color: '#555',
            fontSize: '14px',
          }}
        >
          <p>实时更新 · 每秒刷新 · 精确到毫秒</p>
        </footer>
      </div>
    </div>
  );
};

export default WorldClock;