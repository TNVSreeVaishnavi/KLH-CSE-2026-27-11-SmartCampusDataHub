import { useEffect, useMemo, useState } from 'react';
import {
  Users,
  Building2,
  GraduationCap,
  Search,
  TrendingUp,
  TrendingDown,
  Minus,
  SlidersHorizontal,
  Download,
  RefreshCw,
} from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';
import { BarChart } from '@/components/dashboard/charts/BarChart';
import { campusApi, type StudentRecord } from '@/services/api';
import type { KpiMetric } from '@/data/overviewData';

const ACCENT_GRADIENTS: Record<string, string> = {
  royal: 'from-royal-500 to-royal-700 text-white shadow-[0_8px_20px_-6px_rgba(50,115,252,0.4)]',
  green: 'from-emerald-500 to-emerald-700 text-white shadow-[0_8px_20px_-6px_rgba(16,185,129,0.4)]',
  navy: 'from-navy-600 to-navy-800 text-white shadow-[0_8px_20px_-6px_rgba(39,65,122,0.4)]',
  amber: 'from-amber-500 to-amber-600 text-white shadow-[0_8px_20px_-6px_rgba(245,158,11,0.4)]',
  teal: 'from-teal-500 to-teal-700 text-white shadow-[0_8px_20px_-6px_rgba(20,184,166,0.4)]',
  violet: 'from-violet-500 to-violet-700 text-white shadow-[0_8px_20px_-6px_rgba(139,92,246,0.4)]',
};

const STATUS_STYLES: Record<string, string> = {
  Active: 'bg-green-50 text-green-700',
  'On Leave': 'bg-amber-50 text-amber-700',
  Graduated: 'bg-navy-50 text-navy-600',
  Inactive: 'bg-amber-50 text-amber-700',
};

const AVATAR_COLORS = [
  'from-royal-500 to-royal-700',
  'from-emerald-500 to-emerald-700',
  'from-navy-600 to-navy-800',
  'from-amber-500 to-amber-600',
  'from-teal-500 to-teal-700',
  'from-violet-500 to-violet-700',
];

function displayStatus(status: string) {
  return status.charAt(0).toUpperCase() + status.slice(1).toLowerCase();
}

function getInitials(name: string) {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
}

export function StudentsPage() {
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState('all');
  const [yearFilter, setYearFilter] = useState('all');
  const [students, setStudents] = useState<StudentRecord[]>([]);
  const [allStudents, setAllStudents] = useState<StudentRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadStudents = async (department = deptFilter, year = yearFilter) => {
    setLoading(true);
    setError(null);
    try {
      const response = await campusApi.getStudents({
        department: department === 'all' ? undefined : department,
        year: year === 'all' ? undefined : Number(year.replace('Year ', '')),
      });
      setStudents(response.records);
      if (department === 'all' && year === 'all') setAllStudents(response.records);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load student data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadStudents('all', 'all');
  }, []);

  useEffect(() => {
    if (allStudents.length === 0) return;
    void loadStudents();
  }, [deptFilter, yearFilter]);

  const filtered = useMemo(() => {
    return students.filter((s) => {
      const matchesSearch =
        !search ||
        s.name.toLowerCase().includes(search.toLowerCase()) ||
        s.email.toLowerCase().includes(search.toLowerCase()) ||
        s.student_id.toLowerCase().includes(search.toLowerCase());
      return matchesSearch;
    });
  }, [search, students]);

  const departments = [...new Set(allStudents.map((student) => student.department))].sort();
  const years = [...new Set(allStudents.map((student) => student.year))].sort();
  const studentsByDepartment = departments.map((department) => ({
    department,
    students: allStudents.filter((student) => student.department === department).length,
  }));
  const studentsByYear = years.map((year) => ({
    year,
    students: allStudents.filter((student) => student.year === year).length,
  }));
  const studentKpis: KpiMetric[] = [
    { label: 'Total Students', value: `${allStudents.length}`, change: 'Current total', trend: 'flat' as const, icon: Users, accent: 'royal' },
    { label: 'Departments', value: `${departments.length}`, change: 'Current total', trend: 'flat' as const, icon: Building2, accent: 'navy' },
    { label: 'Year Groups', value: `${years.length}`, change: 'Current total', trend: 'flat' as const, icon: GraduationCap, accent: 'teal' },
  ];

  const hasFilters = search || deptFilter !== 'all' || yearFilter !== 'all';

  const clearFilters = () => {
    setSearch('');
    setDeptFilter('all');
    setYearFilter('all');
  };

  const refreshStudents = async () => {
    setRefreshing(true);
    await loadStudents('all', 'all');
    setRefreshing(false);
  };

  if (loading && allStudents.length === 0) {
    return <div className="flex min-h-[400px] items-center justify-center text-sm text-navy-400">Loading student data...</div>;
  }

  if (error && allStudents.length === 0) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-navy-100 bg-white p-8 text-center shadow-card">
        <p className="font-display text-xl font-700 text-navy-900">Unable to load student data</p>
        <p className="mt-2 max-w-md text-sm text-navy-400">{error}</p>
        <button onClick={() => void loadStudents('all', 'all')} className="mt-5 rounded-xl border border-navy-200 px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600">Retry</button>
      </div>
    );
  }

  if (allStudents.length === 0) {
    return <div className="space-y-5"><div className="flex items-end justify-between gap-4"><PageHeader title="Student Directory" subtitle="Enrollment, demographics, and academic records across all departments" /><button onClick={() => void refreshStudents()} disabled={refreshing} className="flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div><div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-dashed border-navy-200 bg-white p-8 text-center shadow-card"><Users className="h-10 w-10 text-navy-300" /><p className="mt-4 font-display text-xl font-700 text-navy-900">No student data available</p><p className="mt-2 text-sm text-navy-400">Gold Parquet has not produced student records yet.</p></div></div>;
  }

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4"><PageHeader title="Student Directory" subtitle="Enrollment, demographics, and academic records across all departments" /><button onClick={() => void refreshStudents()} disabled={refreshing} aria-label="Refresh student data" className="flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {studentKpis.map((kpi, i) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              style={{ animationDelay: `${i * 0.08}s` }}
              className="group rounded-2xl border border-navy-100 bg-white p-5 shadow-card transition-all duration-300 hover:-translate-y-0.5 hover:shadow-container animate-fade-in-up"
            >
              <div className="flex items-start justify-between">
                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${ACCENT_GRADIENTS[kpi.accent]}`}
                >
                  <Icon className="h-5 w-5" strokeWidth={2.2} />
                </div>
                {kpi.trend === 'up' && (
                  <span className="flex items-center gap-0.5 rounded-full bg-green-50 px-2 py-1 text-[11px] font-700 text-green-600">
                    <TrendingUp className="h-3 w-3" />
                    {kpi.change}
                  </span>
                )}
                {kpi.trend === 'down' && (
                  <span className="flex items-center gap-0.5 rounded-full bg-red-50 px-2 py-1 text-[11px] font-700 text-red-600">
                    <TrendingDown className="h-3 w-3" />
                    {kpi.change}
                  </span>
                )}
                {kpi.trend === 'flat' && (
                  <span className="flex items-center gap-0.5 rounded-full bg-navy-50 px-2 py-1 text-[11px] font-700 text-navy-500">
                    <Minus className="h-3 w-3" />
                    {kpi.change}
                  </span>
                )}
              </div>
              <p className="mt-4 text-[13px] font-600 text-navy-400">{kpi.label}</p>
              <p className="font-display text-3xl font-800 tracking-tight text-navy-900">{kpi.value}</p>
            </div>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
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
              {allStudents.length} total
            </span>
          </div>
          <div className="relative mt-6 h-[220px]">
            <BarChart
              data={studentsByDepartment.map((d) => ({
                label: d.department,
                value: d.students,
              }))}
            />
          </div>
        </div>

        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
                Students by Year
              </h3>
              <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
                Year-group enrollment distribution
              </p>
            </div>
            <span className="rounded-full bg-navy-50 px-3 py-1 text-[12px] font-700 text-navy-600">
              {years.length} years
            </span>
          </div>
          <div className="relative mt-6 h-[220px]">
            <BarChart
              data={studentsByYear.map((d) => ({
                label: d.year,
                value: d.students,
              }))}
              maxValue={30}
            />
          </div>
        </div>
      </div>

      {/* Student table with filters */}
      <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">
              Student Records
            </h3>
            <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">
              {loading ? 'Updating...' : `${filtered.length} of ${students.length} students`}
            </p>
          </div>
          <button className="flex items-center gap-2 self-start rounded-xl border border-navy-200 bg-white px-3.5 py-2 text-[13px] font-600 text-navy-700 transition-all hover:border-royal-300 hover:text-royal-600 sm:self-auto">
            <Download className="h-4 w-4" />
            Export
          </button>
        </div>

        {/* Filter bar */}
        <div className="mt-4 flex flex-col gap-2.5 sm:flex-row sm:items-center">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-[18px] w-[18px] -translate-y-1/2 text-navy-300" />
            <input
              type="search"
              placeholder="Search by name, email, or ID…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full rounded-xl border border-navy-200 bg-navy-50/40 py-2.5 pl-11 pr-4 text-[13px] font-500 text-navy-900 placeholder:text-navy-300 transition-all hover:border-navy-300 focus:border-royal-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-royal-500/10"
            />
          </div>

          {/* Department filter */}
          <div className="relative">
            <SlidersHorizontal className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
            <select
              value={deptFilter}
              onChange={(e) => setDeptFilter(e.target.value)}
              className="cursor-pointer appearance-none rounded-xl border border-navy-200 bg-white py-2.5 pl-9 pr-9 text-[13px] font-600 text-navy-700 transition-all hover:border-navy-300 focus:border-royal-500 focus:outline-none focus:ring-4 focus:ring-royal-500/10"
            >
              <option value="all">All Departments</option>
              {departments.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
          </div>

          {/* Year filter */}
          <div className="relative">
            <select
              value={yearFilter}
              onChange={(e) => setYearFilter(e.target.value)}
              className="cursor-pointer appearance-none rounded-xl border border-navy-200 bg-white py-2.5 pl-4 pr-9 text-[13px] font-600 text-navy-700 transition-all hover:border-navy-300 focus:border-royal-500 focus:outline-none focus:ring-4 focus:ring-royal-500/10"
            >
              <option value="all">All Years</option>
              {years.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>

          {hasFilters && (
            <button
              onClick={clearFilters}
              className="rounded-xl px-3 py-2.5 text-[13px] font-600 text-navy-500 transition-colors hover:bg-navy-50 hover:text-navy-700"
            >
              Clear
            </button>
          )}
        </div>

        {/* Table */}
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[640px]">
            <thead>
              <tr className="border-b border-navy-100 text-left text-[11px] font-700 uppercase tracking-wider text-navy-400">
                <th className="pb-3 pr-4">Student</th>
                <th className="pb-3 pr-4">ID</th>
                <th className="pb-3 pr-4">Department</th>
                <th className="pb-3 pr-4">Year</th>
                <th className="pb-3 pr-4">GPA</th>
                <th className="pb-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-navy-50">
              {filtered.length > 0 ? (
                filtered.map((s) => (
                  <tr key={s.student_id} className="group transition-colors hover:bg-navy-50/40">
                    <td className="py-3 pr-4">
                      <div className="flex items-center gap-3">
                        <div
                          className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${AVATAR_COLORS[s.student_id.length % AVATAR_COLORS.length]} text-[12px] font-700 text-white shadow-card`}
                        >
                          {getInitials(s.name)}
                        </div>
                        <div className="min-w-0">
                          <p className="text-[13px] font-700 text-navy-900">{s.name}</p>
                          <p className="truncate text-[11px] text-navy-400">{s.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 pr-4">
                      <span className="rounded-md bg-navy-50 px-2 py-0.5 font-mono text-[12px] font-600 text-navy-600">
                        {s.student_id}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-[13px] font-500 text-navy-600">{s.department}</td>
                    <td className="py-3 pr-4 text-[13px] font-500 text-navy-600">{s.year}</td>
                    <td className="py-3 pr-4">
                      <span className="text-[13px] font-700 text-navy-900">{s.avg_gpa == null ? '--' : s.avg_gpa.toFixed(2)}</span>
                    </td>
                    <td className="py-3">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-1 text-[11px] font-700 ${STATUS_STYLES[displayStatus(s.status)] ?? 'bg-navy-50 text-navy-600'}`}
                      >
                        {displayStatus(s.status)}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="py-10 text-center">
                    <p className="text-sm font-600 text-navy-400">
                      No students match your filters.
                    </p>
                    <button
                      onClick={clearFilters}
                      className="mt-2 text-[13px] font-600 text-royal-600 hover:text-royal-700"
                    >
                      Clear all filters
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
