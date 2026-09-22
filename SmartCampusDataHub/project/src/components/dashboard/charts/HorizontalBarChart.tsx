interface HorizontalBarChartProps {
  data: { label: string; value: number; suffix?: string }[];
  maxValue?: number;
}

export function HorizontalBarChart({ data, maxValue = 100 }: HorizontalBarChartProps) {
  const max = maxValue ?? Math.ceil(Math.max(...data.map((d) => d.value)) * 1.1);

  return (
    <div className="space-y-3.5">
      {data.map((d, i) => {
        const widthPct = (d.value / max) * 100;
        return (
          <div key={d.label} className="group">
            <div className="mb-1.5 flex items-center justify-between">
              <span className="text-[12px] font-600 text-navy-600 sm:text-[13px]">{d.label}</span>
              <span className="text-[13px] font-700 text-navy-900">
                {d.value}
                {d.suffix ?? ''}
              </span>
            </div>
            <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-navy-100">
              <div
                className="h-full rounded-full bg-gradient-to-r from-royal-600 to-royal-400 transition-all duration-700 ease-out group-hover:from-royal-700 group-hover:to-royal-500"
                style={{
                  width: `${widthPct}%`,
                  transitionDelay: `${i * 80}ms`,
                }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}
