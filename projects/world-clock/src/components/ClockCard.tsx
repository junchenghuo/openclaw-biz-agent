import React, { useState, useEffect } from 'react';
import { ClockFace } from './ClockFace';
import { CountryConfig } from '../types';

interface ClockCardProps {
  config: CountryConfig;
}

export const ClockCard: React.FC<ClockCardProps> = ({ config }) => {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
    }, 100);

    return () => clearInterval(interval);
  }, []);

  const getLocalTime = (timezone: string): Date => {
    return new Date(new Date().toLocaleString('en-US', { timeZone: timezone }));
  };

  const localTime = getLocalTime(config.timezone);
  const hours = localTime.getHours().toString().padStart(2, '0');
  const minutes = localTime.getMinutes().toString().padStart(2, '0');
  const seconds = localTime.getSeconds().toString().padStart(2, '0');

  const formatOffset = (timezone: string): string => {
    try {
      const now = new Date();
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: timezone,
        timeZoneName: 'shortOffset',
      });
      const parts = formatter.formatToParts(now);
      const offsetPart = parts.find(p => p.type === 'timeZoneName');
      return offsetPart?.value || '';
    } catch {
      return '';
    }
  };

  return (
    <div
      className="clock-card"
      style={{
        background: 'linear-gradient(145deg, #1a1a2e 0%, #16213e 100%)',
        borderRadius: '20px',
        padding: '20px',
        boxShadow: `0 10px 40px rgba(0,0,0,0.4), 0 0 20px ${config.primaryColor}20`,
        border: `1px solid ${config.primaryColor}40`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '12px',
        transition: 'transform 0.3s ease, box-shadow 0.3s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-5px)';
        e.currentTarget.style.boxShadow = `0 15px 50px rgba(0,0,0,0.5), 0 0 30px ${config.primaryColor}30`;
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = `0 10px 40px rgba(0,0,0,0.4), 0 0 20px ${config.primaryColor}20`;
      }}
    >
      <div style={{ position: 'relative' }}>
        <ClockFace
          country={config.country}
          city={config.city}
          timezone={config.timezone}
          time={localTime}
          primaryColor={config.primaryColor}
          secondaryColor={config.secondaryColor}
          decoration={config.decoration}
        />
      </div>
      
      <div style={{ textAlign: 'center' }}>
        <h3
          style={{
            color: config.primaryColor,
            margin: 0,
            fontSize: '18px',
            fontWeight: 600,
            textShadow: `0 0 10px ${config.primaryColor}80`,
          }}
        >
          {config.city}
        </h3>
        <p
          style={{
            color: config.secondaryColor,
            margin: '4px 0 0',
            fontSize: '12px',
            opacity: 0.8,
          }}
        >
          {config.country}
        </p>
      </div>

      <div
        style={{
          fontFamily: 'monospace',
          fontSize: '24px',
          color: '#fff',
          letterSpacing: '2px',
        }}
      >
        <span style={{ color: config.primaryColor }}>{hours}</span>
        <span>:</span>
        <span style={{ color: config.secondaryColor }}>{minutes}</span>
        <span>:</span>
        <span style={{ color: '#ff6b6b' }}>{seconds}</span>
      </div>

      <div
        style={{
          fontSize: '11px',
          color: '#888',
          padding: '4px 12px',
          background: 'rgba(0,0,0,0.3)',
          borderRadius: '10px',
        }}
      >
        {formatOffset(config.timezone)}
      </div>
    </div>
  );
};