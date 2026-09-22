import { useEffect, useState } from 'react';

interface DonutChartProps {
  data: { label: string; value: number; color: string }[];
  centerLabel?: string;
  centerValue?: string;
}

export function DonutChart({ data, centerLabel, centerValue }: DonutChartProps) {
  const total = data.reduce((sum, d) => sum + d.value, 0);
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = requestAnimationFrame(() => setAnimated(true));
    return () => cancelAnimationFrame(t);
  }, []);

  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  let offsetAccumulator = 0;

  const segments = data.map((d) => {
    const fraction = d.value / total;
    const dashLength = fraction * circumference;
    const segment = {
      color: d.color,
      dashLength,
      gap: circumference - dashLength,
      offset: offsetAccumulator,
      label: d.label,
      value: d.value,
      pct: Math.round(fraction * 100),
    };
    offsetAccumulator += dashLength;
    return segment;
  });

  return (
    <div className="flex flex-col items-center gap-5 sm:flex-row sm:justify-center sm:gap-6">
      {/* Donut */}
      <div className="relative shrink-0">
        <svg width="180" height="180" viewBox="0 0 180 180" className="-rotate-90">
          {/* Background track */}
          <circle
            cx="90"
            cy="90"
            r={radius}
            fill="none"
            stroke="#eef2f8"
            strokeWidth="18"
          />
          {segments.map((s, i) => (
            <circle
              key={s.label}
              cx="90"
              cy="90"
              r={radius}
              fill="none"
              stroke={s.color}
              strokeWidth="18"
              strokeLinecap="round"
              strokeDasharray={`${animated ? s.dashLength : 0} ${s.gap}`}
              strokeDashoffset={-s.offset}
              style={{
                transition: 'stroke-dasharray 0.9s cubic-bezier(0.22, 1, 0.36, 1)',
                transitionDelay: `${i * 120}ms`,
              }}
            />
          ))}
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="font-display text-2xl font-800 text-navy-900">
            {centerValue ?? total}
          </span>
          <span className="text-[11px] font-600 text-navy-400">{centerLabel ?? 'Total'}</span>
        </div>
      </div>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-x-5 gap-y-2.5 sm:grid-cols-1">
        {segments.map((s) => (
          <div key={s.label} className="flex items-center gap-2.5">
            <span
              className="h-3 w-3 shrink-0 rounded-full"
              style={{ backgroundColor: s.color }}
            />
            <span className="text-[12px] font-600 text-navy-600">{s.label}</span>
            <span className="ml-auto text-[12px] font-700 text-navy-900">{s.value}</span>
            <span className="text-[11px] font-500 text-navy-400">({s.pct}%)</span>
          </div>
        ))}
      </div>
    </div>
  );
}
