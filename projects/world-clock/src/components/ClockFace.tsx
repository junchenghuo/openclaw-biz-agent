import React, { useRef, useEffect } from 'react';

interface ClockFaceProps {
  country: string;
  city: string
  timezone: string;
  time: Date;
  primaryColor: string;
  secondaryColor: string;
  decoration?: string;
}

export const ClockFace: React.FC<ClockFaceProps> = ({
  country,
  city,
  timezone,
  time,
  primaryColor,
  secondaryColor,
  decoration,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const size = 200;
    const centerX = size / 2;
    const centerY = size / 2;
    const radius = 90;

    // Clear canvas
    ctx.clearRect(0, 0, size, size);

    // Draw clock face background
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, radius);
    gradient.addColorStop(0, '#1a1a2e');
    gradient.addColorStop(1, '#0f0f1a');
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw outer ring with glow
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 3;
    ctx.shadowColor = primaryColor;
    ctx.shadowBlur = 15;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Draw hour markers
    for (let i = 0; i < 12; i++) {
      const angle = (i * 30 - 90) * (Math.PI / 180);
      const x1 = centerX + Math.cos(angle) * (radius - 15);
      const y1 = centerY + Math.sin(angle) * (radius - 15);
      const x2 = centerX + Math.cos(angle) * (radius - 8);
      const y2 = centerY + Math.sin(angle) * (radius - 8);
      
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.strokeStyle = secondaryColor;
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Draw decoration based on country
    if (decoration) {
      ctx.font = '24px serif';
      ctx.textAlign = 'center';
      ctx.fillStyle = secondaryColor;
      ctx.globalAlpha = 0.3;
      ctx.fillText(decoration, centerX, centerY - 20);
      ctx.globalAlpha = 1;
    }

    // Calculate time
    const hours = time.getHours();
    const minutes = time.getMinutes();
    const seconds = time.getSeconds();
    const ms = time.getMilliseconds();

    // Draw hour hand
    const hourAngle = ((hours % 12) + minutes / 60) * 30 - 90;
    const hourRad = hourAngle * (Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(
      centerX + Math.cos(hourRad) * 45,
      centerY + Math.sin(hourRad) * 45
    );
    ctx.strokeStyle = primaryColor;
    ctx.lineWidth = 4;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Draw minute hand
    const minuteAngle = (minutes + seconds / 60) * 6 - 90;
    const minuteRad = minuteAngle * (Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(
      centerX + Math.cos(minuteRad) * 65,
      centerY + Math.sin(minuteRad) * 65
    );
    ctx.strokeStyle = secondaryColor;
    ctx.lineWidth = 3;
    ctx.lineCap = 'round';
    ctx.stroke();

    // Draw second hand with smooth animation
    const secondAngle = (seconds + ms / 1000) * 6 - 90;
    const secondRad = secondAngle * (Math.PI / 180);
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.lineTo(
      centerX + Math.cos(secondRad) * 70,
      centerY + Math.sin(secondRad) * 70
    );
    ctx.strokeStyle = '#ff6b6b';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Draw center dot
    ctx.beginPath();
    ctx.arc(centerX, centerY, 4, 0, Math.PI * 2);
    ctx.fillStyle = primaryColor;
    ctx.fill();

  }, [time, primaryColor, secondaryColor, decoration]);

  return (
    <canvas
      ref={canvasRef}
      width={200}
      height={200}
      style={{ display: 'block' }}
    />
  );
};