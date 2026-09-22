import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  ArrowDown,
  BarChart3,
  Check,
  Circle,
  Clock3,
  Database,
  Layers3,
  LoaderCircle,
  Radio,
  RefreshCw,
  Server,
  Sparkles,
  Layers,
  Upload,
  X,
} from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';
import { campusApi, type PipelineHistoryResponse, type PipelineStatus } from '@/services/api';

const PIPELINE_STAGES = [
  { key: 'DATA_UPLOAD', label: 'Data Upload', icon: Upload, backendStage: 'QUEUED' },
  { key: 'KAFKA', label: 'Kafka', icon: Radio, backendStage: 'INGESTION' },
  { key: 'REDIS', label: 'Redis', icon: Server, backendStage: null },
  { key: 'SPARK', label: 'Spark', icon: Sparkles, backendStage: 'INGESTION' },
  { key: 'CLEANING', label: 'Cleaning', icon: Layers3, backendStage: 'CLEANING' },
  { key: 'VALIDATION', label: 'Validation', icon: Check, backendStage: 'VALIDATION' },
  { key: 'TRANSFORMATION', label: 'Transformation', icon: Activity, backendStage: 'TRANSFORMATION' },
  { key: 'BRONZE', label: 'Bronze', icon: Layers, backendStage: 'INGESTION' },
  { key: 'SILVER', label: 'Silver', icon: Layers, backendStage: 'VALIDATION' },
  { key: 'GOLD', label: 'Gold', icon: Database, backendStage: 'STORAGE' },
  { key: 'ANALYTICS', label: 'Analytics', icon: BarChart3, backendStage: 'ANALYTICS' },
  { key: 'FASTAPI', label: 'FastAPI', icon: Server, backendStage: null },
  { key: 'DASHBOARD', label: 'Dashboard', icon: BarChart3, backendStage: null },
] as const;

const BACKEND_ORDER = ['QUEUED', 'INGESTION', 'CLEANING', 'VALIDATION', 'TRANSFORMATION', 'STORAGE', 'ANALYTICS', 'COMPLETED'];
const ACTIVE_STATES = new Set(['QUEUED', 'RUNNING']);

type StageState = 'complete' | 'running' | 'pending' | 'failed';

function numberValue(value: number | string | null | undefined) {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatDate(value: string | null | undefined) {
  if (!value) return 'Not available';
  return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
}

function formatDuration(startedAt: string | null | undefined, completedAt: string | null | undefined) {
  if (!startedAt) return 'n/a';
  const end = completedAt ? new Date(completedAt).getTime() : Date.now();
  const start = new Date(startedAt).getTime();
  if (!Number.isFinite(start) || !Number.isFinite(end)) return 'n/a';
  return `${Math.max(0, (end - start) / 1000).toFixed(1)}s`;
}

function stateForStage(stageKey: string, status: PipelineStatus | null): StageState {
  if (!status) return 'pending';
  const stage = PIPELINE_STAGES.find((item) => item.key === stageKey);
  const currentIndex = BACKEND_ORDER.indexOf(status.current_stage);
  const stageIndex = stage?.backendStage ? BACKEND_ORDER.indexOf(stage.backendStage) : -1;

  if (status.pipeline_status === 'FAILED') {
    if (stageKey === 'REDIS' && !status.error_message) return 'complete';
    if (stageIndex === currentIndex) return 'failed';
    return stageIndex >= 0 && currentIndex > stageIndex ? 'complete' : 'pending';
  }
  if (stageKey === 'REDIS') return status.current_stage === 'INGESTION' ? 'running' : 'complete';
  if (stageKey === 'DATA_UPLOAD') return status.current_stage === 'QUEUED' ? 'running' : 'complete';
  if (stageKey === 'KAFKA') return status.current_stage === 'INGESTION' ? 'running' : 'complete';
  if (stageKey === 'SPARK') return status.current_stage === 'INGESTION' ? 'running' : 'complete';
  if (stageKey === 'FASTAPI' || stageKey === 'DASHBOARD') return status.current_stage === 'COMPLETED' ? 'complete' : 'pending';
  if (status.current_stage === stage?.backendStage) return status.pipeline_status === 'COMPLETED' ? 'complete' : 'running';
  return stageIndex >= 0 && currentIndex > stageIndex ? 'complete' : 'pending';
}

const STATE_STYLES: Record<StageState, { label: string; color: string; bg: string; Icon: typeof Check }> = {
  complete: { label: 'Completed', color: 'text-green-600', bg: 'bg-green-50', Icon: Check },
  running: { label: 'Running', color: 'text-royal-600', bg: 'bg-royal-50', Icon: LoaderCircle },
  pending: { label: 'Pending', color: 'text-navy-400', bg: 'bg-navy-50', Icon: Circle },
  failed: { label: 'Failed', color: 'text-red-600', bg: 'bg-red-50', Icon: X },
};

function stageCount(key: string, status: PipelineStatus) {
  if (key === 'DATA_UPLOAD' || key === 'KAFKA' || key === 'SPARK') return numberValue(status.records_received);
  if (key === 'CLEANING') return numberValue(status.records_cleaned);
  if (key === 'VALIDATION') return numberValue(status.records_validated);
  if (key === 'TRANSFORMATION' || key === 'GOLD' || key === 'ANALYTICS') return numberValue(status.records_written);
  if (key === 'BRONZE') return numberValue(status.records_received);
  if (key === 'SILVER') return numberValue(status.records_validated);
  return null;
}

export function PipelineMonitorPage({ onNavigate }: { onNavigate?: (id: string) => void }) {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [history, setHistory] = useState<PipelineHistoryResponse['history']>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadPipeline = async (showSpinner = false) => {
    if (showSpinner) setRefreshing(true);
    try {
      const [liveStatus, liveHistory] = await Promise.all([campusApi.getPipelineStatus(), campusApi.getPipelineHistory()]);
      setStatus(liveStatus);
      setHistory(liveHistory.history);
      setError(null);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : 'Unable to load live pipeline status.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    void loadPipeline();
    const interval = window.setInterval(() => {
      if (!status || ACTIVE_STATES.has(status.pipeline_status) || !['COMPLETED', 'FAILED'].includes(status.current_stage)) void loadPipeline();
    }, 5000);
    return () => window.clearInterval(interval);
  }, [status]);

  const isRunning = Boolean(status && (ACTIVE_STATES.has(status.pipeline_status) || !['COMPLETED', 'FAILED'].includes(status.current_stage)));
  const completedStages = useMemo(() => status ? PIPELINE_STAGES.filter((stage) => stateForStage(stage.key, status) === 'complete').length : 0, [status]);

  if (loading) return <div className="flex min-h-[400px] items-center justify-center text-sm text-navy-400">Loading live pipeline status...</div>;

  if (error && !status) {
    return <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-red-100 bg-white p-8 text-center shadow-card"><X className="h-10 w-10 text-red-400" /><p className="mt-4 font-display text-xl font-700 text-navy-900">Live status unavailable</p><p className="mt-2 max-w-md text-sm text-navy-400">{error}</p><button onClick={() => void loadPipeline(true)} className="mt-5 rounded-xl bg-royal-600 px-4 py-2.5 text-sm font-700 text-white hover:bg-royal-700">Retry</button></div>;
  }

  return (
    <div className="space-y-5">
      <PageHeader title="Pipeline Monitor" subtitle="Watch the live data engineering pipeline move into trusted analytics" />

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-navy-100 bg-white px-5 py-4 shadow-card">
        <div className="flex items-center gap-3"><span className={`flex h-10 w-10 items-center justify-center rounded-xl ${isRunning ? 'bg-royal-50 text-royal-600' : status?.pipeline_status === 'FAILED' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}><Activity className={`h-5 w-5 ${isRunning ? 'animate-pulse' : ''}`} /></span><div><p className="text-[11px] font-700 uppercase tracking-[0.16em] text-navy-400">Live Redis state</p><p className="font-display text-lg font-700 text-navy-900">{status?.pipeline_status ?? 'No run recorded'}</p><p className="text-xs text-navy-400">{status?.current_stage ?? 'Waiting for a pipeline run'}</p></div></div>
        <div className="flex items-center gap-3"><span className="text-xs text-navy-400">{isRunning ? 'Refreshing every 5s' : 'Live refresh paused'}</span><button onClick={() => void loadPipeline(true)} disabled={refreshing} aria-label="Refresh pipeline status" className="flex items-center gap-2 rounded-xl border border-navy-200 px-3.5 py-2.5 text-sm font-700 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div>
      </div>

      {error && <div className="rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-700">Live refresh warning: {error}</div>}

      {status?.pipeline_status === 'COMPLETED' && <section className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-green-100 bg-green-50/70 px-5 py-4 shadow-card"><div><p className="font-display text-lg font-800 text-green-700">PIPELINE COMPLETED</p><p className="mt-1 text-sm text-green-700/80">Kafka, Redis, Spark, the lake layers, analytics, and the API are ready.</p></div><button type="button" onClick={() => onNavigate?.('overview')} className="rounded-xl bg-green-600 px-4 py-2.5 text-sm font-800 text-white hover:bg-green-700">View Updated Dashboard</button></section>}
      {status?.pipeline_status === 'FAILED' && <section className="rounded-2xl border border-red-100 bg-red-50 px-5 py-4 shadow-card"><p className="font-display text-lg font-800 text-red-700">PIPELINE FAILED</p><p className="mt-1 text-sm text-red-700/80">{status.error_message || 'The backend reported a failure without an error message.'}</p></section>}

      <section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6">
        <div className="flex items-center justify-between gap-3"><div><h2 className="font-display text-lg font-700 text-navy-900">Data engineering flow</h2><p className="mt-1 text-sm text-navy-400">Stage state is derived from the live Redis pipeline status.</p></div><span className="hidden rounded-full bg-navy-50 px-3 py-1 text-xs font-700 text-navy-500 sm:inline-flex">{completedStages}/{PIPELINE_STAGES.length} completed</span></div>
        <div className="mt-6 grid gap-3 md:grid-cols-4 xl:grid-cols-6">
          {PIPELINE_STAGES.map((stage, index) => {
            const state = stateForStage(stage.key, status);
            const style = STATE_STYLES[state];
            const Icon = style.Icon;
            const StageIcon = stage.icon;
            const count = status ? stageCount(stage.key, status) : null;
            return <div key={stage.key} className="relative rounded-xl border border-navy-100 bg-canvas p-4"><div className="flex items-center justify-between gap-2"><span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-royal-600 shadow-sm"><StageIcon className="h-4 w-4" /></span><span className={`flex items-center gap-1 text-[10px] font-800 uppercase tracking-wide ${style.color}`}><Icon className={`h-3 w-3 ${state === 'running' ? 'animate-spin' : ''}`} />{style.label}</span></div><p className="mt-4 text-sm font-700 text-navy-900">{stage.label}</p><p className="mt-1 text-xs text-navy-400">{count == null ? 'Records n/a' : `${count.toLocaleString()} records`}</p><p className="mt-2 text-[11px] text-navy-400">Duration n/a</p>{index < PIPELINE_STAGES.length - 1 && <ArrowDown className="absolute -bottom-4 left-1/2 z-10 h-4 w-4 -translate-x-1/2 text-navy-300 md:hidden" />}</div>;
          })}
        </div>
      </section>

      <section className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6"><div className="flex items-center gap-2"><Database className="h-5 w-5 text-royal-600" /><h2 className="font-display text-lg font-700 text-navy-900">Current batch</h2></div><div className="mt-5 grid grid-cols-2 gap-x-5 gap-y-5 sm:grid-cols-4">{[['Batch ID', status?.batch_id], ['Dataset', status?.dataset], ['Started', formatDate(status?.started_at)], ['Completed', formatDate(status?.completed_at)], ['Input Records', numberValue(status?.records_received).toLocaleString()], ['Processed Records', numberValue(status?.records_validated).toLocaleString()], ['Rejected Records', numberValue(status?.records_rejected).toLocaleString()], ['Output Records', numberValue(status?.records_written).toLocaleString()]].map(([label, value]) => <div key={label as string}><p className="text-xs text-navy-400">{label}</p><p className="mt-1 break-words text-sm font-800 text-navy-900">{value ?? 'n/a'}</p></div>)}</div><div className="mt-5 flex items-center gap-2 border-t border-navy-100 pt-4 text-xs text-navy-400"><Clock3 className="h-4 w-4" />Elapsed duration: <span className="font-700 text-navy-700">{formatDuration(status?.started_at, status?.completed_at)}</span></div>{status?.error_message && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{status.error_message}</p>}</div>
        <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6"><h2 className="font-display text-lg font-700 text-navy-900">State legend</h2><div className="mt-5 space-y-3">{Object.entries(STATE_STYLES).map(([key, value]) => { const Icon = value.Icon; return <div key={key} className="flex items-center gap-3"><span className={`flex h-8 w-8 items-center justify-center rounded-lg ${value.bg} ${value.color}`}><Icon className="h-4 w-4" /></span><span className="text-sm font-700 text-navy-800">{value.label}</span></div>; })}</div><p className="mt-5 text-xs leading-5 text-navy-400">The API currently reports pipeline-level stage transitions. Stage durations are shown as unavailable until the backend exposes per-stage timing.</p></div>
      </section>

      <section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6"><div className="flex items-center justify-between"><div><h2 className="font-display text-lg font-700 text-navy-900">Pipeline history</h2><p className="mt-1 text-sm text-navy-400">Recent Redis status snapshots for the active and completed batches.</p></div><Clock3 className="h-5 w-5 text-navy-300" /></div><div className="mt-5 overflow-x-auto"><table className="w-full min-w-[620px] text-left text-sm"><thead><tr className="border-b border-navy-100 text-xs uppercase tracking-wide text-navy-400"><th className="pb-3 pr-4">Batch</th><th className="pb-3 pr-4">Dataset</th><th className="pb-3 pr-4">Stage</th><th className="pb-3 pr-4">Status</th><th className="pb-3">Written</th></tr></thead><tbody>{history.map((entry, index) => <tr key={`${entry.batch_id}-${entry.current_stage}-${index}`} className="border-b border-navy-50 last:border-0"><td className="py-3 pr-4 font-700 text-navy-800">{entry.batch_id}</td><td className="py-3 pr-4 text-navy-600">{entry.dataset}</td><td className="py-3 pr-4 text-navy-600">{entry.current_stage}</td><td className="py-3 pr-4 text-navy-600">{entry.pipeline_status}</td><td className="py-3 text-navy-600">{numberValue(entry.records_written).toLocaleString()}</td></tr>)}{history.length === 0 && <tr><td colSpan={5} className="py-8 text-center text-sm text-navy-400">No pipeline history is available yet.</td></tr>}</tbody></table></div></section>
    </div>
  );
}
