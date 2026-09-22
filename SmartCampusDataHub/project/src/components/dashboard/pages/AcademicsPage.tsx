import { useEffect, useState } from 'react';
import type { ReactNode } from 'react';
import { AlertTriangle, BookOpen, GraduationCap, RefreshCw, TrendingUp, Users } from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';
import { DonutChart } from '@/components/dashboard/charts/DonutChart';
import { HorizontalBarChart } from '@/components/dashboard/charts/HorizontalBarChart';
import { campusApi, type AcademicResponse } from '@/services/api';

const PERFORMANCE_COLORS = ['#1d54f0', '#10b981', '#f59e0b', '#ef4444'];

function formatGpa(value: number | null | undefined) {
  return value == null ? '--' : value.toFixed(2);
}

export function AcademicsPage() {
  const [academics, setAcademics] = useState<AcademicResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const loadAcademics = async () => {
    setError(null);
    try {
      setAcademics(await campusApi.getAcademics());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load academic data.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadAcademics();
  }, []);

  if (loading) {
    return <div className="flex min-h-[400px] items-center justify-center text-sm text-navy-400">Loading academic data...</div>;
  }

  if (error) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-red-100 bg-white p-8 text-center shadow-card">
        <AlertTriangle className="h-10 w-10 text-red-400" />
        <p className="mt-4 font-display text-xl font-700 text-navy-900">Unable to load academic data</p>
        <p className="mt-2 max-w-md text-sm text-navy-400">{error}</p>
      </div>
    );
  }

  if (!academics || academics.statistics.total_students === 0) {
    return (
      <div className="space-y-5">
        <PageHeader title="Academic Performance" subtitle="Track academic outcomes across departments and students" />
        <div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-dashed border-navy-200 bg-white p-8 text-center shadow-card">
          <BookOpen className="h-10 w-10 text-navy-300" />
          <p className="mt-4 font-display text-xl font-700 text-navy-900">No academic data available</p>
          <p className="mt-2 max-w-md text-sm text-navy-400">Academic records will appear here once the pipeline has loaded them.</p>
        </div>
      </div>
    );
  }

  const { statistics, grade_statistics: gradeStats } = academics;
  const performanceDistribution = [
    { label: 'Excellent (3.5+)', value: gradeStats.excellent_count, color: PERFORMANCE_COLORS[0] },
    { label: 'Good (3.0-3.49)', value: gradeStats.good_count, color: PERFORMANCE_COLORS[1] },
    { label: 'Average (2.0-2.99)', value: gradeStats.average_count, color: PERFORMANCE_COLORS[2] },
    { label: 'Below average (<2.0)', value: gradeStats.below_average_count, color: PERFORMANCE_COLORS[3] },
  ].filter((item) => item.value > 0);

  return (
    <div className="space-y-5">
      <div className="flex items-end justify-between gap-4"><PageHeader title="Academic Performance" subtitle="Track academic outcomes across departments and students" /><button onClick={() => { setRefreshing(true); void loadAcademics(); }} disabled={refreshing} aria-label="Refresh academic data" className="flex items-center gap-2 rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[
          { label: 'Average Academic Performance', value: `${formatGpa(statistics.avg_gpa)} GPA`, icon: GraduationCap, tone: 'from-royal-500 to-royal-700' },
          { label: 'Highest Score', value: `${formatGpa(statistics.max_gpa)} GPA`, icon: TrendingUp, tone: 'from-emerald-500 to-emerald-700' },
          { label: 'Students Evaluated', value: `${statistics.total_students}`, icon: Users, tone: 'from-navy-600 to-navy-800' },
        ].map(({ label, value, icon: Icon, tone }) => (
          <div key={label} className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card animate-fade-in-up">
            <div className={`flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${tone} text-white`}>
              <Icon className="h-5 w-5" strokeWidth={2.2} />
            </div>
            <p className="mt-4 text-[13px] font-600 text-navy-400">{label}</p>
            <p className="font-display text-3xl font-800 tracking-tight text-navy-900">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-5">
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6 lg:col-span-3">
          <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">Academic Performance by Department</h3>
          <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">Average GPA across academic departments</p>
          <div className="mt-6">
            <HorizontalBarChart
              data={academics.by_department.map((department) => ({ label: department.department, value: department.avg_gpa, suffix: ' GPA' }))}
              maxValue={4}
            />
          </div>
        </div>

        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6 lg:col-span-2">
          <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">Performance Distribution</h3>
          <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">Students grouped by GPA range</p>
          <div className="mt-6 flex justify-center">
            {performanceDistribution.length > 0 ? (
              <DonutChart data={performanceDistribution} centerLabel="Evaluated" centerValue={`${statistics.total_students}`} />
            ) : (
              <p className="py-16 text-sm text-navy-400">No performance distribution available.</p>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
        <AcademicTable
          title="Top Performers"
          subtitle="Students with the highest average GPA"
          emptyMessage="No top performer records available."
          records={academics.top_performers.records}
          renderRow={(student) => (
            <tr key={student.student_id} className="border-t border-navy-50">
              <td className="py-3 pr-4"><p className="text-[13px] font-700 text-navy-900">{student.name}</p><p className="font-mono text-[11px] text-navy-400">{student.student_id}</p></td>
              <td className="py-3 pr-4 text-[13px] text-navy-600">{student.courses}</td>
              <td className="py-3 text-right text-[13px] font-800 text-green-600">{formatGpa(student.avg_gpa)}</td>
            </tr>
          )}
          columns={['Student', 'Courses', 'GPA']}
        />

        <AcademicTable
          title="Students Requiring Academic Attention"
          subtitle="Students below a 2.0 average GPA"
          emptyMessage="No students currently require academic attention."
          records={academics.struggling_students.records}
          renderRow={(student) => (
            <tr key={student.student_id} className="border-t border-navy-50">
              <td className="py-3 pr-4"><p className="text-[13px] font-700 text-navy-900">{student.name}</p><p className="font-mono text-[11px] text-navy-400">{student.student_id}</p></td>
              <td className="py-3 pr-4 text-[13px] text-navy-600">{student.department}</td>
              <td className="py-3 text-right text-[13px] font-800 text-red-600">{formatGpa(student.avg_gpa)}</td>
            </tr>
          )}
          columns={['Student', 'Department', 'GPA']}
        />
      </div>
    </div>
  );
}

function AcademicTable<T>({ title, subtitle, emptyMessage, records, renderRow, columns }: {
  title: string;
  subtitle: string;
  emptyMessage: string;
  records: T[];
  renderRow: (record: T) => ReactNode;
  columns: string[];
}) {
  return (
    <section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
      <h3 className="font-display text-base font-700 text-navy-900 sm:text-lg">{title}</h3>
      <p className="mt-0.5 text-[12px] text-navy-400 sm:text-[13px]">{subtitle}</p>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full min-w-[360px]">
          <thead><tr className="text-left text-[11px] font-700 uppercase tracking-wider text-navy-400">{columns.map((column, index) => <th key={column} className={`pb-2 ${index === columns.length - 1 ? 'text-right' : 'pr-4'}`}>{column}</th>)}</tr></thead>
          <tbody>{records.length > 0 ? records.slice(0, 10).map(renderRow) : <tr><td colSpan={columns.length} className="py-8 text-center text-sm font-600 text-navy-400">{emptyMessage}</td></tr>}</tbody>
        </table>
      </div>
    </section>
  );
}