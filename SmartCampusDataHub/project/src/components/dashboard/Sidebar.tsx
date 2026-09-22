import { GraduationCap, X, Dot } from 'lucide-react';
import { NAV_ITEMS } from '@/data/navigation';
import type { HealthResponse, PipelineResponse } from '@/services/api';

interface SidebarProps {
  activeId: string;
  onNavigate: (id: string) => void;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  health: HealthResponse | null;
  pipeline: PipelineResponse | null;
}

export function Sidebar({ activeId, onNavigate, mobileOpen, onCloseMobile, health, pipeline }: SidebarProps) {
  const lastExecution = pipeline?.summary.last_execution;
  const systemStatus = [
    { label: 'Database', value: health?.database === 'connected' ? 'Connected' : 'Unavailable' },
    { label: 'Records', value: health ? `${health.records.students ?? 0} students` : 'Loading...' },
    { label: 'Pipeline', value: lastExecution?.status ?? 'Loading...' },
    { label: 'Last Pipeline Run', value: lastExecution?.start_time?.slice(0, 10) ?? 'Loading...' },
    { label: 'Version', value: health?.version ?? 'Loading...' },
  ];
  const isOperational = health?.database === 'connected' && lastExecution?.status === 'SUCCESS';

  return (
    <>
      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-30 bg-navy-950/60 backdrop-blur-sm lg:hidden animate-fade-in"
          onClick={onCloseMobile}
        />
      )}

      <aside
        className={`fixed z-40 flex h-full w-[264px] shrink-0 flex-col bg-navy-900 transition-transform duration-300 lg:static lg:translate-x-0 ${
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Subtle texture */}
        <div className="pointer-events-none absolute inset-0 opacity-[0.04] bg-grid" />

        {/* Header / brand */}
        <div className="relative flex items-center justify-between px-5 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-royal-500 to-royal-700 shadow-card">
              <GraduationCap className="h-5 w-5 text-white" strokeWidth={2.2} />
            </div>
            <div className="leading-tight">
              <p className="font-display text-sm font-700 tracking-tight text-white">Smart Campus</p>
              <p className="font-display text-sm font-700 tracking-tight text-royal-300">Data Hub</p>
            </div>
          </div>
          <button
            onClick={onCloseMobile}
            className="rounded-lg p-1.5 text-navy-300 transition-colors hover:bg-white/10 hover:text-white lg:hidden"
            aria-label="Close menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="relative flex-1 overflow-y-auto px-3 py-2">
          <p className="px-3 pb-2 pt-3 text-[10px] font-700 uppercase tracking-[0.2em] text-navy-400">
            Navigation
          </p>
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const active = item.id === activeId;
              const Icon = item.icon;
              return (
                <li key={item.id}>
                  <button
                    onClick={() => onNavigate(item.id)}
                    className={`group flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-600 transition-all duration-200 ${
                      active
                        ? 'bg-royal-500 text-white shadow-[0_0_20px_-2px_rgba(50,115,252,0.5)] hover:bg-royal-500'
                        : 'text-navy-200 hover:bg-white/[0.07] hover:text-white'
                    }`}
                  >
                    <Icon
                      className={`h-[18px] w-[18px] shrink-0 transition-colors ${
                        active ? 'text-white' : 'text-navy-300 group-hover:text-royal-300'
                      }`}
                      strokeWidth={2}
                    />
                    <span className="truncate">{item.label}</span>
                    {active && <Dot className="ml-auto h-5 w-5 text-white/60" />}
                  </button>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* System status */}
        <div className="relative px-4 pb-5 pt-3">
          <div className="rounded-2xl border border-white/[0.08] bg-white/[0.04] p-4">
            <div className="flex items-center justify-between">
              <p className="text-[10px] font-700 uppercase tracking-[0.18em] text-navy-400">
                System Status
              </p>
                <span className={`flex items-center gap-1.5 text-[11px] font-600 ${isOperational ? 'text-green-400' : 'text-amber-400'}`}>
                <span className="relative flex h-2 w-2">
                  <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-60 ${isOperational ? 'bg-green-400' : 'bg-amber-400'}`} />
                  <span className={`relative inline-flex h-2 w-2 rounded-full ${isOperational ? 'bg-green-400' : 'bg-amber-400'}`} />
                </span>
                {isOperational ? 'Operational' : 'Attention'}
              </span>
            </div>
            <div className="mt-3 space-y-2">
              {systemStatus.map((s) => (
                <div key={s.label} className="flex items-center justify-between text-[12px]">
                  <span className="text-navy-300">{s.label}</span>
                  <span className="font-600 text-navy-100">{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
