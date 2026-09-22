import { useEffect, useState } from 'react';
import {
  Users,
  GraduationCap,
  Bus,
  Building2,
  CalendarDays,
  CalendarCheck,
  TrendingUp,
  TrendingDown,
  Minus,
  Calendar,
  RefreshCw,
  Lightbulb,
  CheckCircle2,
  ArrowUpRight,
} from 'lucide-react';
import { BarChart } from '@/components/dashboard/charts/BarChart';
import { DonutChart } from '@/components/dashboard/charts/DonutChart';
import { campusApi, type OverviewResponse, type PipelineResponse } from '@/services/api';
import type { KpiMetric } from '@/data/overviewData';

const ACCENT_GRADIENTS: Record<string, string> = {
  royal: 'from-royal-500 to-royal-700 text-white shadow-[0_8px_20px_-6px_rgba(50,115,252,0.4)]',
  green: 'from-emerald-500 to-emerald-700 text-white shadow-[0_8px_20px_-6px_rgba(16,185,129,0.4)]',
  navy: 'from-navy-600 to-navy-800 text-white shadow-[0_8px_20px_-6px_rgba(39,65,122,0.4)]',
  amber: 'from-amber-500 to-amber-600 text-white shadow-[0_8px_20px_-6px_rgba(245,158,11,0.4)]',
  teal: 'from-teal-500 to-teal-700 text-white shadow-[0_8px_20px_-6px_rgba(20,184,166,0.4)]',
  violet: 'from-violet-500 to-violet-700 text-white shadow-[0_8px_20px_-6px_rgba(139,92,246,0.4)]',
};

const INSIGHT_ACCENTS: Record<string, string> = {
  royal: 'bg-royal-50 text-royal-600',
  green: 'bg-green-50 text-green-600',
  amber: 'bg-amber-50 text-amber-600',
  navy: 'bg-navy-50 text-navy-600',
};

const STATUS_STYLES: Record<string, string> = {
  Upcoming: 'bg-royal-50 text-royal-700',
  Completed: 'bg-green-50 text-green-700',
  Ongoing: 'bg-amber-50 text-amber-700',
};

const STATUS_DOT: Record<string, string> = {
  Upcoming: 'bg-royal-500',
  Completed: 'bg-green-500',
  Ongoing: 'bg-amber-500',
};

const ATTENDANCE_COLORS: Record<string, string> = {
  Present: '#1d54f0',
  Absent: '#ef4444',
  Late: '#f59e0b',
  Excused: '#94a3b8',
};

const SERVICE_NAMES = ['INGESTION', 'CLEANING', 'VALIDATION', 'TRANSFORMATION', 'DATABASE_LOAD', 'ANALYTICS'];

export function OverviewPage({ userName }: { userName: string }) {
  const [refreshing, setRefreshing] = useState(false);
  const [lastRefresh, setLastRefresh] = useState('Just now');
  const [overview, setOverview] = useState<OverviewResponse | null>(null);
  const [pipeline, setPipeline] = useState<PipelineResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    setError(null);
    try {
      const [overviewData, pipelineData] = await Promise.all([
        campusApi.getOverview(),
        campusApi.getPipeline(),
      ]);
      setOverview(overviewData);
      setPipeline(pipelineData);
      setLastRefresh('Just now');
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load dashboard data.');
    }
  };

  useEffect(() => {
    void loadDashboard();
  }, []);

  const handleRefresh = async () => {
    if (refreshing) return;
    setRefreshing(true);
    await loadDashboard();
    setRefreshing(false);
  };

  // Live-update the "last refresh" label
  useEffect(() => {
    if (refreshing) return;
    const timer = setInterval(() => {
      setLastRefresh((prev) => (prev === 'Just now' ? '1 min ago' : prev));
    }, 60000);
    return () => clearInterval(timer);
  }, [refreshing]);

  if (error && !overview) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-navy-100 bg-white p-8 text-center shadow-card">
        <p className="font-display text-xl font-700 text-navy-900">Unable to load campus data</p>
        <p className="mt-2 max-w-md text-sm text-navy-400">{error}</p>
        <button
          onClick={() => void loadDashboard()}
          className="mt-5 flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 transition-all hover:border-royal-300 hover:text-royal-600"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      </div>
    );
  }

  if (!overview) {
    return <div className="flex min-h-[400px] items-center justify-center text-sm text-navy-400">Loading campus data...</div>;
  }

  const { kpis } = overview;
  const latestExecution = pipeline?.summary.last_execution ?? overview.pipeline.last_execution;
  const latestStatus = latestExecution?.status === 'SUCCESS' ? 'Operational' : latestExecution?.status ?? 'Unknown';
  const kpiItems: KpiMetric[] = [
    { label: 'Total Students', value: `${kpis.total_students}`, change: 'Current total', trend: 'flat' as const, icon: Users, accent: 'royal' },
    { label: 'Average Attendance', value: `${kpis.average_attendance.toFixed(1)}%`, change: 'Current average', trend: 'flat' as const, icon: CalendarCheck, accent: 'green' },
    { label: 'Academic Performance', value: `${kpis.average_gpa.toFixed(2)} GPA`, change: 'Current average', trend: 'flat' as const, icon: GraduationCap, accent: 'navy' },
    { label: 'Total Events', value: `${kpis.total_events}`, change: 'Current total', trend: 'flat' as const, icon: CalendarDays, accent: 'amber' },
    { label: 'Transportation Usage', value: `${kpis.transportation_vehicles}`, change: 'Vehicles tracked', trend: 'flat' as const, icon: Bus, accent: 'teal' },
    { label: 'Facilities Active', value: `${kpis.active_facilities}`, change: 'Operational facilities', trend: 'flat' as const, icon: Building2, accent: 'violet' },
  ];
  const attendanceSegments = overview.attendance_by_status.map((segment) => ({
    label: segment.status,
    value: segment.count,
    color: ATTENDANCE_COLORS[segment.status] ?? '#64748b',
  }));
  const recentEvents = overview.recent_events.map((event) => ({
    event: event.name,
    type: event.event_type ?? 'General',
    date: event.date,
    participants: event.capacity ?? 0,
    status: event.date > new Date().toISOString().slice(0, 10) ? 'Upcoming' : 'Completed',
  }));
  const topDepartment = [...overview.students_by_department].sort((a, b) => b.count - a.count)[0];
  const operationalServices = SERVICE_NAMES.map((stageName) => {
    const stage = pipeline?.stages.find((item) => item.stage_name === stageName);
    return {
      name: stageName.replace('_', ' '),
      status: stage?.status === 'SUCCESS' ? 'Operational' : stage?.status ?? latestStatus,
      latency: stage?.duration_seconds != null ? `${stage.duration_seconds.toFixed(2)}s` : 'n/a',
      uptime: stage?.status === 'SUCCESS' ? 'OK' : 'Check',
    };
  });
  const insights = [
    { title: 'Attendance coverage', description: `${kpis.average_attendance.toFixed(1)}% average attendance across tracked records.`, metric: `${kpis.average_attendance.toFixed(1)}%`, icon: CalendarCheck, accent: 'green' },
    { title: 'Largest department', description: topDepartment ? `${topDepartment.department} has the highest student count.` : 'No department data is available.', metric: `${topDepartment?.count ?? 0}`, icon: Users, accent: 'royal' },
    { title: 'Facilities online', description: `${kpis.active_facilities} facilities are currently operational.`, metric: `${kpis.active_facilities}`, icon: Building2, accent: 'amber' },
    { title: 'Pipeline health', description: `${overview.pipeline.success_rate}% execution success rate across recorded runs.`, metric: `${overview.pipeline.success_rate}%`, icon: GraduationCap, accent: 'navy' },
  ];

  return (
    <div className="space-y-5">
      {/* Page header with controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-[13px] font-600 text-royal-600">Welcome back, {userName}!</p>
          <h1 className="mt-1 font-display text-2xl font-800 tracking-tight text-navy-900 sm:text-[28px]">
            Campus Executive Overview
          </h1>
          <p className="mt-1.5 text-sm text-navy-400">
            Real-time insights and analytics from Smart Campus Data Hub
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          {/* Date selector */}
          <div className="relative">
            <Calendar className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
            <select
              defaultValue="today"
              className="cursor-pointer appearance-none rounded-xl border border-navy-200 bg-white py-2.5 pl-9 pr-9 text-[13px] font-600 text-navy-700 transition-all hover:border-navy-300 focus:border-royal-500 focus:outline-none focus:ring-4 focus:ring-royal-500/10"
            >
              <option value="today">Today</option>
              <option value="week">This Week</option>
              <option value="month">This Month</option>
              <option value="quarter">This Quarter</option>
            </select>
            <svg
              className="pointer-events-none absolute right-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-navy-400"
              viewBox="0 0 12 12"
              fill="none"
            >
              <path d="M3 5l3 3 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>

          {/* Refresh */}
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 transition-all hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Refresh</span>
          </button>
        </div>
      </div>

      {/* KPI row */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-6">
        {kpiItems.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              style={{ animationDelay: `${i * 0.06}s` }}
              className="group rounded-2xl border border-navy-100 bg-white p-4 shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-container animate-fade-in-up sm:p-5"
            >
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${ACCENT_GRADIENTS[kpi.accent]}`}
              >
                <Icon className="h-5 w-5" strokeWidth={2.2} />
              </div>
              <p className="mt-3.5 text-[12px] font-600 text-navy-400 sm:text-[13px]">{kpi.label}</p>
              <p className="font-display text-2xl font-800 tracking-tight text-navy-900 sm:text-[28px]">
                {kpi.value}
              </p>
              <div className="mt-1 flex items-center gap-1">
                {kpi.trend === 'up' && <TrendingUp className="h-3 w-3 text-green-500" />}
                {kpi.trend === 'down' && <TrendingDown className="h-3 w-3 text-red-500" />}
                {kpi.trend === 'flat' && <Minus className="h-3 w-3 text-navy-400" />}
                <span
                  className={`text-[11px] font-600 ${
                    kpi.trend === 'up'
                      ? 'text-green-600'
                      : kpi.trend === 'down'
                        ? 'text-red-600'
                        : 'text-navy-400'
                  }`}
                >
                  {kpi.change}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-5">
        {/* Bar chart — Students by Department */}
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6 lg:col-span-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
                Students by Department
              </h3>
              <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
                Enrollment distribution across faculties
              </p>
            </div>
            <span className="rounded-full bg-navy-50 px-3 py-1 text-[12px] font-700 text-navy-600">
              {kpis.total_students} total
            </span>
          </div>
          <div className="relative mt-6 h-[240px]">
            <BarChart
              data={overview.students_by_department.map((d) => ({
                label: d.department,
                value: d.count,
              }))}
            />
          </div>
        </div>

        {/* Donut chart — Attendance Status */}
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6 lg:col-span-2">
          <div>
            <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
              Attendance Status
            </h3>
            <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
              Today's student attendance breakdown
            </p>
          </div>
          <div className="mt-6 flex items-center justify-center">
            <DonutChart
              data={attendanceSegments.map((s) => ({
                label: s.label,
                value: s.value,
                color: s.color,
              }))}
              centerLabel="Present"
              centerValue={`${kpis.average_attendance.toFixed(1)}%`}
            />
          </div>
        </div>
      </div>

      {/* Recent events table */}
      <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
              Recent Campus Events
            </h3>
            <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
              Latest scheduled and completed activities
            </p>
          </div>
          <button className="flex items-center gap-1 text-[13px] font-600 text-royal-600 transition-colors hover:text-royal-700">
            View all
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Table */}
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[560px]">
            <thead>
              <tr className="border-b border-navy-100 text-left text-[11px] font-700 uppercase tracking-wider text-navy-400">
                <th className="pb-3 pr-4 font-700">Event</th>
                <th className="pb-3 pr-4 font-700">Type</th>
                <th className="pb-3 pr-4 font-700">Date</th>
                <th className="pb-3 pr-4 font-700">Participants</th>
                <th className="pb-3 font-700">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-50">
              {recentEvents.length > 0 ? recentEvents.map((e) => (
                <tr key={e.event} className="group transition-colors hover:bg-navy-50/40">
                  <td className="py-3.5 pr-4 text-[13px] font-700 text-navy-900">{e.event}</td>
                  <td className="py-3.5 pr-4 text-[13px] font-500 text-navy-500">{e.type}</td>
                  <td className="py-3.5 pr-4 text-[13px] font-500 text-navy-500">{e.date}</td>
                  <td className="py-3.5 pr-4">
                    <span className="text-[13px] font-700 text-navy-900">{e.participants}</span>
                    <span className="ml-1 text-[12px] text-navy-400">capacity</span>
                  </td>
                  <td className="py-3.5">
                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-700 ${STATUS_STYLES[e.status]}`}
                    >
                      <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[e.status]}`} />
                      {e.status}
                    </span>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="py-8 text-center text-sm text-navy-400">No campus events available.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Key insights */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-amber-500" />
          <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">Key Insights</h3>
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {insights.map((insight, i) => {
            const Icon = insight.icon;
            return (
              <div
                key={insight.title}
                style={{ animationDelay: `${i * 0.08}s` }}
                className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-container animate-fade-in-up"
              >
                <div className="flex items-center justify-between">
                  <span
                    className={`flex h-9 w-9 items-center justify-center rounded-xl ${INSIGHT_ACCENTS[insight.accent]}`}
                  >
                    <Icon className="h-[18px] w-[18px]" strokeWidth={2.2} />
                  </span>
                  <span className="font-display text-xl font-800 text-navy-900">{insight.metric}</span>
                </div>
                <p className="mt-3 text-[13px] font-700 text-navy-800">{insight.title}</p>
                <p className="mt-1.5 text-[12px] leading-relaxed text-navy-400">
                  {insight.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Real-time system status */}
      <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
              Real-time System Status
            </h3>
            <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
              Data pipeline service health · Last refresh: {lastRefresh}
            </p>
          </div>
          <span className="flex items-center gap-2 rounded-full bg-green-50 px-3.5 py-2 text-[12px] font-700 text-green-600">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500" />
            </span>
            {latestStatus === 'Operational' ? 'All Systems Operational' : 'System Attention Required'}
          </span>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {operationalServices.map((svc, i) => (
            <div
              key={svc.name}
              style={{ animationDelay: `${i * 0.05}s` }}
              className="flex items-center gap-3.5 rounded-xl border border-navy-100 bg-navy-50/30 p-3.5 transition-all hover:border-green-200 hover:bg-green-50/30 animate-fade-in-up"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-green-100">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-[13px] font-700 text-navy-900">{svc.name}</p>
                <p className="text-[11px] font-500 text-navy-400">
                  {svc.status} · {svc.latency} latency
                </p>
              </div>
              <span className="shrink-0 text-[11px] font-700 text-green-600">{svc.uptime}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
