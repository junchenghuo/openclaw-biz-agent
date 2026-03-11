import { useEffect, useRef } from 'react';
import styles from './ParticleBackground.module.css';

type Dot = { x: number; y: number; vx: number; vy: number; r: number; a: number };

export default function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dots: Dot[] = [];
    const density = 32;

    const resize = () => {
      const dpr = Math.max(1, Math.min(2, window.devicePixelRatio || 1));
      canvas.width = Math.floor(window.innerWidth * dpr);
      canvas.height = Math.floor(window.innerHeight * dpr);
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

      dots.length = 0;
      for (let i = 0; i < density; i++) {
        dots.push({
          x: Math.random() * window.innerWidth,
          y: Math.random() * window.innerHeight,
          vx: (Math.random() - 0.5) * 0.25,
          vy: (Math.random() - 0.5) * 0.25,
          r: 0.8 + Math.random() * 1.8,
          a: 0.05 + Math.random() * 0.12
        });
      }
    };

    resize();
    window.addEventListener('resize', resize);

    let raf = 0;
    const tick = () => {
      raf = window.requestAnimationFrame(tick);
      ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);

      for (const d of dots) {
        d.x += d.vx;
        d.y += d.vy;
        if (d.x < -20) d.x = window.innerWidth + 20;
        if (d.x > window.innerWidth + 20) d.x = -20;
        if (d.y < -20) d.y = window.innerHeight + 20;
        if (d.y > window.innerHeight + 20) d.y = -20;

        ctx.beginPath();
        ctx.fillStyle = `rgba(94,231,255,${d.a})`;
        ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
        ctx.fill();
      }
    };

    tick();
    return () => {
      window.removeEventListener('resize', resize);
      window.cancelAnimationFrame(raf);
    };
  }, []);

  return <canvas ref={canvasRef} className={styles.canvas} aria-hidden="true" />;
}
