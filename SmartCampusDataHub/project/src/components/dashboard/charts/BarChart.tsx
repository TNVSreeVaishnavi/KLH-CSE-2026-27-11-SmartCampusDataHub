import { useEffect, useState } from 'react';

interface BarChartProps {
  data: { label: string; value: number }[];
  maxValue?: number;
}

export function BarChart({ data, maxValue }: BarChartProps) {
  const max = maxValue ?? Math.ceil(Math.max(...data.map((d) => d.value)) * 1.15);
  const [animated, setAnimated] = useState(false);

  useEffect(() => {
    const t = requestAnimationFrame(() => setAnimated(true));
    return () => cancelAnimationFrame(t);
  }, []);

  return (
    <div className="flex h-full flex-col">
      {/* Bars */}
      <div className="flex flex-1 items-end gap-2 sm:gap-3 lg:gap-4">
        {data.map((d, i) => {
          const heightPct = (d.value / max) * 100;
          return (
            <div
              key={d.label}
              className="group flex flex-1 flex-col items-center justify-end"
              style={{ height: '100%' }}
            >
              {/* Value tooltip on hover */}
              <div className="mb-1.5 opacity-0 transition-opacity duration-200 group-hover:opacity-100">
                <span className="rounded-md bg-navy-900 px-2 py-0.5 text-[11px] font-700 text-white shadow-card">
                  {d.value}
                </span>
              </div>

              {/* Bar */}
              <div className="relative w-full max-w-[44px] overflow-hidden rounded-t-lg bg-navy-100">
                <div
                  className="w-full rounded-t-lg bg-gradient-to-t from-royal-700 to-royal-400 transition-all duration-700 ease-out"
                  style={{
                    height: animated ? `${heightPct}%` : '0%',
                    transitionDelay: `${i * 80}ms`,
                  }}
                />
                {/* Top highlight */}
                <div
                  className="absolute left-0 right-0 top-0 h-0.5 bg-royal-300 transition-all duration-700 ease-out"
                  style={{
                    bottom: animated ? `${heightPct}%` : '0%',
                    transitionDelay: `${i * 80}ms`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Labels */}
      <div className="mt-2.5 flex gap-2 sm:gap-3 lg:gap-4">
        {data.map((d) => (
          <div
            key={d.label}
            className="flex-1 text-center text-[10px] font-600 leading-tight text-navy-400 sm:text-[11px]"
          >
            {d.label}
          </div>
        ))}
      </div>

      {/* Y-axis reference lines */}
      <div className="pointer-events-none absolute inset-0 flex flex-col justify-between py-0">
        {[0, 0.25, 0.5, 0.75, 1].map((p) => (
          <div key={p} className="h-px w-full bg-navy-100/60" />
        ))}
      </div>
    </div>
  );
}
