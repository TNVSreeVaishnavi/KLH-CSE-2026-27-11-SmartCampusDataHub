import {
  GraduationCap,
  Users,
  BookOpen,
  CalendarDays,
  Bus,
  Building2,
} from 'lucide-react';

const CAMPUS_IMAGE =
  'https://images.pexels.com/photos/16666017/pexels-photo-16666017.jpeg?auto=compress&cs=tinysrgb&w=1600';

const FEATURES = [
  { label: 'Students', icon: Users },
  { label: 'Academics', icon: BookOpen },
  { label: 'Events', icon: CalendarDays },
  { label: 'Transportation', icon: Bus },
  { label: 'Facilities', icon: Building2 },
] as const;

export function BrandPanel() {
  return (
    <div className="relative h-full w-full overflow-hidden rounded-r-[inherit]">
      {/* Background photo */}
      <img
        src={CAMPUS_IMAGE}
        alt="Aerial view of a university campus"
        className="absolute inset-0 h-full w-full object-cover"
      />

      {/* Dark navy overlay for readability */}
      <div className="absolute inset-0 bg-gradient-to-br from-navy-950/85 via-navy-900/75 to-navy-800/65" />
      <div className="absolute inset-0 bg-gradient-to-t from-navy-950/70 via-transparent to-navy-950/40" />

      {/* Subtle decorative grid */}
      <div className="absolute inset-0 opacity-[0.06] bg-grid" />

      {/* Content layer */}
      <div className="relative flex h-full flex-col justify-between p-7 sm:p-10 lg:p-12">
        {/* Top — brand lockup */}
        <div className="flex items-center gap-3 animate-fade-in">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-royal-500/90 shadow-glow backdrop-blur-sm">
            <GraduationCap className="h-6 w-6 text-white" strokeWidth={2.2} />
          </div>
          <div className="leading-tight">
            <p className="font-display text-base font-700 tracking-tight text-white sm:text-lg">
              Smart Campus
            </p>
            <p className="font-display text-base font-700 tracking-tight text-royal-200 sm:text-lg">
              Data Hub
            </p>
          </div>
        </div>

        {/* Center — welcome block */}
        <div className="max-w-md animate-fade-in-up">
          <p className="mb-3 text-[11px] font-600 uppercase tracking-[0.35em] text-royal-200/80">
            Welcome to
          </p>
          <h1 className="font-display text-4xl font-800 leading-[1.05] tracking-tight text-white sm:text-5xl">
            Smart Campus
            <br />
            <span className="bg-gradient-to-r from-royal-300 to-royal-500 bg-clip-text text-transparent">
              Data Hub
            </span>
          </h1>
          <p className="mt-5 max-w-sm text-balance text-sm leading-relaxed text-navy-100/80 sm:text-base">
            A unified data platform for a smarter, more connected campus.
          </p>

          {/* Feature cards */}
          <div className="mt-8 grid grid-cols-2 gap-2.5 sm:grid-cols-3 sm:gap-3">
            {FEATURES.map(({ label, icon: Icon }, index) => (
              <div
                key={label}
                style={{ animationDelay: `${0.15 + index * 0.08}s` }}
                className="group flex items-center gap-2.5 rounded-xl border border-white/10 bg-white/[0.06] px-3 py-2.5 backdrop-blur-md transition-all duration-300 hover:-translate-y-0.5 hover:border-royal-400/40 hover:bg-white/[0.12] animate-fade-in-up"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-royal-500/20 text-royal-200 transition-colors duration-300 group-hover:bg-royal-500/30 group-hover:text-white">
                  <Icon className="h-4 w-4" strokeWidth={2} />
                </span>
                <span className="text-[13px] font-600 text-white/90">{label}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom — tagline */}
        <div className="max-w-xs animate-fade-in-up" style={{ animationDelay: '0.6s' }}>
          <div className="h-px w-12 bg-gradient-to-r from-royal-400 to-transparent" />
          <p className="mt-4 text-balance text-sm font-500 leading-relaxed text-navy-100/70">
            Transforming campus data
            <br />
            into brighter opportunities.
          </p>
        </div>
      </div>
    </div>
  );
}
