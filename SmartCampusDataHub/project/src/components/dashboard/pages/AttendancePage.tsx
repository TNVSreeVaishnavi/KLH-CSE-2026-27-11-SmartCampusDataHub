import { useEffect, useState } from 'react';
import {
  CalendarCheck,
  CheckCircle2,
  XCircle,
  Clock,
  FileText,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertTriangle,
  ArrowUpRight,
  RefreshCw,
} from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';
import { DonutChart } from '@/components/dashboard/charts/DonutChart';
import { HorizontalBarChart } from '@/components/dashboard/charts/HorizontalBarChart';
import { campusApi, type AttendanceResponse } from '@/services/api';
import type { KpiMetric } from '@/data/overviewData';

const ACCENT_GRADIENTS: Record<string, string> = {
  royal: 'from-royal-500 to-royal-700 text-white shadow-[0_8px_20px_-6px_rgba(50,115,252,0.4)]',
  green: 'from-emerald-500 to-emerald-700 text-white shadow-[0_8px_20px_-6px_rgba(16,185,129,0.4)]',
  navy: 'from-navy-600 to-navy-800 text-white shadow-[0_8px_20px_-6px_rgba(39,65,122,0.4)]',
  amber: 'from-amber-500 to-amber-600 text-white shadow-[0_8px_20px_-6px_rgba(245,158,11,0.4)]',
  teal: 'from-teal-500 to-teal-700 text-white shadow-[0_8px_20px_-6px_rgba(20,184,166,0.4)]',
  violet: 'from-violet-500 to-violet-700 text-white shadow-[0_8px_20px_-6px_rgba(139,92,246,0.4)]',
};

function attendanceColor(pct: number) {
  if (pct < 75) return { bar: 'bg-red-500', text: 'text-red-600', bg: 'bg-red-50' };
  if (pct < 85) return { bar: 'bg-amber-500', text: 'text-amber-600', bg: 'bg-amber-50' };
  return { bar: 'bg-green-500', text: 'text-green-600', bg: 'bg-green-50' };
}

export function AttendancePage() {
  const [attendance, setAttendance] = useState<AttendanceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadAttendance = async () => {
    setLoading(true);
    setError(null);
    try {
      setAttendance(await campusApi.getAttendance());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load attendance data.');
    } finally {
      setLoading(false);
    }
  };

  const refreshAttendance = async () => {
    setRefreshing(true);
    await loadAttendance();
    setRefreshing(false);
  };

  useEffect(() => {
    void loadAttendance();
  }, []);

  if (loading && !attendance) {
    return <div className="flex min-h-[400px] items-center justify-center text-sm text-navy-400">Loading attendance data...</div>;
  }

  if (error && !attendance) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-navy-100 bg-white p-8 text-center shadow-card">
        <p className="font-display text-xl font-700 text-navy-900">Unable to load attendance data</p>
        <p className="mt-2 max-w-md text-sm text-navy-400">{error}</p>
        <button onClick={() => void loadAttendance()} className="mt-5 rounded-xl border border-navy-200 px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600">Retry</button>
      </div>
    );
  }

  if (!attendance || attendance.statistics.total_students === 0) {
    return <div className="space-y-5"><div className="flex items-end justify-between gap-4"><PageHeader title="Attendance Analytics" subtitle="Track and monitor student attendance patterns across departments" /><button onClick={() => void refreshAttendance()} disabled={refreshing} className="flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div><div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-dashed border-navy-200 bg-white p-8 text-center shadow-card"><CalendarCheck className="h-10 w-10 text-navy-300" /><p className="mt-4 font-display text-xl font-700 text-navy-900">No attendance data available</p><p className="mt-2 text-sm text-navy-400">Gold Parquet has not produced attendance records yet.</p></div></div>;
  }

  const statusTotals = Object.fromEntries(attendance.by_status.map((item) => [item.status.toLowerCase(), item.count]));
  const attendanceKpis: KpiMetric[] = [
    { label: 'Average Attendance', value: `${attendance.statistics.avg_attendance.toFixed(1)}%`, change: 'Current average', trend: 'flat' as const, icon: CalendarCheck, accent: 'green' },
    { label: 'Present', value: `${statusTotals.present ?? 0}`, change: 'Recorded sessions', trend: 'flat' as const, icon: CheckCircle2, accent: 'royal' },
    { label: 'Absent', value: `${statusTotals.absent ?? 0}`, change: 'Recorded sessions', trend: 'flat' as const, icon: XCircle, accent: 'amber' },
    { label: 'Late', value: `${statusTotals.late ?? 0}`, change: 'Recorded sessions', trend: 'flat' as const, icon: Clock, accent: 'navy' },
    { label: 'Excused', value: `${statusTotals.excused ?? 0}`, change: 'Recorded sessions', trend: 'flat' as const, icon: FileText, accent: 'teal' },
  ];
  const attendanceSegments = attendance.by_status.map((item) => ({
    label: item.status.charAt(0).toUpperCase() + item.status.slice(1).toLowerCase(),
    value: item.count,
    color: item.status.toLowerCase() === 'present' ? '#1d54f0' : item.status.toLowerCase() === 'absent' ? '#ef4444' : item.status.toLowerCase() === 'late' ? '#f59e0b' : '#94a3b8',
  }));

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4"><PageHeader title="Attendance Analytics" subtitle="Track and monitor student attendance patterns across departments" /><button onClick={() => void refreshAttendance()} disabled={refreshing} aria-label="Refresh attendance data" className="flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div>

      {/* KPI cards */}
      <div className="grid grid-cols-2 gap-3 sm:gap-4 xl:grid-cols-5">
        {attendanceKpis.map((kpi, i) => {
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
              centerValue={`${attendance.statistics.avg_attendance.toFixed(1)}%`}
            />
          </div>
        </div>

        {/* Horizontal bar chart — Attendance by Department */}
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6 lg:col-span-3">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
                Attendance by Department
              </h3>
              <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
                Average attendance rate across faculties
              </p>
            </div>
            <span className="rounded-full bg-green-50 px-3 py-1 text-[12px] font-700 text-green-600">
              Avg {attendance.statistics.avg_attendance.toFixed(1)}%
            </span>
          </div>
          <div className="mt-6">
            <HorizontalBarChart
              data={attendance.by_department.map((d) => ({
                label: d.department,
                value: d.avg_attendance,
                suffix: '%',
              }))}
              maxValue={100}
            />
          </div>
        </div>
      </div>

      {/* Low attendance table */}
      <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-2.5">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
              <AlertTriangle className="h-5 w-5" />
            </span>
            <div>
              <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
                Low Attendance Students
              </h3>
              <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
                Students below 85% attendance threshold
              </p>
            </div>
          </div>
          <button className="flex items-center gap-1 self-start text-[13px] font-600 text-royal-600 transition-colors hover:text-royal-700 sm:self-auto">
            View full report
            <ArrowUpRight className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Table */}
        <div className="mt-5 overflow-x-auto">
          <table className="w-full min-w-[640px]">
            <thead>
              <tr className="border-b border-navy-100 text-left text-[11px] font-700 uppercase tracking-wider text-navy-400">
                <th className="pb-3 pr-4">Student</th>
                <th className="pb-3 pr-4">Department</th>
                <th className="pb-3 pr-4">Year</th>
                <th className="pb-3 pr-4">Attendance</th>
                <th className="pb-3 pr-4">Missed / Total</th>
                <th className="pb-3">Trend</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-50">
              {attendance.low_attendance.records.length > 0 ? attendance.low_attendance.records.map((s) => {
                const colors = attendanceColor(s.avg_attendance);
                return (
                  <tr key={s.student_id} className="group transition-colors hover:bg-navy-50/40">
                    <td className="py-3.5 pr-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${colors.bg} text-[11px] font-700 ${colors.text}`}
                        >
                          {s.name
                            .split(' ')
                            .map((n) => n[0])
                            .join('')
                            .slice(0, 2)
                            .toUpperCase()}
                        </div>
                        <div>
                          <p className="text-[13px] font-700 text-navy-900">{s.name}</p>
                          <p className="font-mono text-[11px] text-navy-400">{s.student_id}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3.5 pr-4 text-[13px] font-500 text-navy-600">
                      {s.department ?? '--'}
                    </td>
                    <td className="py-3.5 pr-4 text-[13px] font-500 text-navy-600">--</td>
                    <td className="py-3.5 pr-4">
                      <div className="flex items-center gap-2.5">
                        <div className="h-2 w-20 overflow-hidden rounded-full bg-navy-100">
                          <div
                            className={`h-full rounded-full ${colors.bar} transition-all duration-700`}
                            style={{ width: `${s.avg_attendance}%` }}
                          />
                        </div>
                        <span className={`text-[13px] font-700 ${colors.text}`}>
                          {s.avg_attendance}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3.5 pr-4 text-[13px] font-600 text-navy-600">
                      <span className="font-700 text-navy-900">{s.missed_sessions ?? '--'}</span>
                      <span className="text-navy-400"> / {s.sessions_tracked ?? '--'}</span>
                    </td>
                    <td className="py-3.5">
                      <span className="inline-flex items-center gap-1 text-[12px] font-700 text-navy-500">
                        <Minus className="h-3.5 w-3.5" />
                        Current average
                      </span>
                    </td>
                  </tr>
                )}
              ) : (
                <tr><td colSpan={6} className="py-10 text-center text-sm font-600 text-navy-400">No students are below the attendance threshold.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
