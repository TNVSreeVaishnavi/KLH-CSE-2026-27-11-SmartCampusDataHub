import { useRef, useState } from 'react';
import { AlertCircle, CheckCircle2, FileText, UploadCloud, X } from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';
import { campusApi, type PipelineUploadResponse } from '@/services/api';

const DATASETS = ['Students', 'Attendance', 'Academics', 'Events', 'Transportation', 'Facilities'] as const;
const MAX_FILE_SIZE = 25 * 1024 * 1024;

type DatasetLabel = (typeof DATASETS)[number];

function datasetKey(label: DatasetLabel) {
  return label.toLowerCase();
}

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

export function DataIngestionPage({ onNavigate }: { onNavigate: (id: string) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dataset, setDataset] = useState<DatasetLabel>('Students');
  const [file, setFile] = useState<File | null>(null);
  const [upload, setUpload] = useState<PipelineUploadResponse | null>(null);
  const [preview, setPreview] = useState<string[][]>([]);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const selectFile = (selected: File | undefined) => {
    setError(null);
    setUpload(null);
    if (!selected) return;
    if (!selected.name.toLowerCase().endsWith('.csv')) {
      setFile(null);
      setError('Please choose a CSV file.');
      return;
    }
    if (selected.size === 0) {
      setFile(null);
      setError('This file is empty. Choose a CSV containing campus records.');
      return;
    }
    if (selected.size > MAX_FILE_SIZE) {
      setFile(null);
      setError('The file is larger than the 25 MB upload limit.');
      return;
    }
    setFile(selected);
    const reader = new FileReader();
    reader.onload = () => {
      const text = typeof reader.result === 'string' ? reader.result : '';
      const rows = text
        .split(/\r?\n/)
        .filter(Boolean)
        .slice(0, 6)
        .map((row) => row.split(',').map((cell) => cell.trim().replace(/^"|"$/g, '')));
      setPreview(rows);
    };
    reader.readAsText(selected);
  };

  const startPipeline = async () => {
    if (!file) {
      setError('Select a CSV file before starting the pipeline.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const result = await campusApi.uploadDataset(datasetKey(dataset), file);
      setUpload(result);
      onNavigate('pipeline-monitor');
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'The upload service is unavailable.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-5">
      <PageHeader title="Data Ingestion" subtitle="Send a campus dataset through the real streaming and lake pipeline" />

      {upload ? (
        <section className="rounded-2xl border border-green-100 bg-white p-6 shadow-card sm:p-8">
          <div className="flex items-start gap-4"><span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-green-50 text-green-600"><CheckCircle2 className="h-6 w-6" /></span><div><p className="text-[11px] font-800 uppercase tracking-[0.16em] text-green-600">Upload accepted</p><h2 className="mt-1 font-display text-2xl font-800 text-navy-900">Pipeline queued</h2><p className="mt-2 text-sm text-navy-500">{upload.filename} is moving through Kafka, Redis, Spark, and the Parquet lake.</p></div></div>
          <div className="mt-6 grid gap-4 rounded-xl bg-canvas p-4 sm:grid-cols-3"><div><p className="text-xs text-navy-400">Batch ID</p><p className="mt-1 break-all text-sm font-800 text-navy-900">{upload.batch_id}</p></div><div><p className="text-xs text-navy-400">Dataset</p><p className="mt-1 text-sm font-800 text-navy-900">{upload.dataset}</p></div><div><p className="text-xs text-navy-400">Records received</p><p className="mt-1 text-sm font-800 text-navy-900">{upload.records_received.toLocaleString()}</p></div></div>
          <p className="mt-5 text-sm text-navy-400">Opening the live Pipeline Monitor...</p>
        </section>
      ) : (
        <section className="max-w-3xl rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-8">
          <div className="flex items-start gap-4"><span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-royal-50 text-royal-600"><UploadCloud className="h-6 w-6" /></span><div><h2 className="font-display text-xl font-800 text-navy-900">Upload Campus Dataset</h2><p className="mt-1 text-sm text-navy-400">Choose a validated CSV source to begin a monitored pipeline run.</p></div></div>

          <label className="mt-8 block text-sm font-700 text-navy-800" htmlFor="dataset-type">Dataset Type</label>
          <select id="dataset-type" value={dataset} onChange={(event) => setDataset(event.target.value as DatasetLabel)} className="mt-2 w-full rounded-xl border border-navy-200 bg-white px-4 py-3 text-sm font-600 text-navy-800 outline-none transition focus:border-royal-500 focus:ring-4 focus:ring-royal-100">
            {DATASETS.map((option) => <option key={option}>{option}</option>)}
          </select>

          <input ref={inputRef} className="sr-only" type="file" accept=".csv,text/csv" onChange={(event) => selectFile(event.target.files?.[0])} />
          <button type="button" onClick={() => inputRef.current?.click()} className="mt-6 flex w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-navy-200 bg-canvas px-5 py-10 text-center transition hover:border-royal-400 hover:bg-royal-50/40"><FileText className="h-8 w-8 text-royal-500" /><span className="mt-3 text-sm font-800 text-navy-800">Choose CSV file</span><span className="mt-1 text-xs text-navy-400">CSV only, up to 25 MB</span></button>

          {file && <>
            <div className="mt-4 flex items-center justify-between gap-3 rounded-xl border border-navy-100 bg-navy-50/60 px-4 py-3"><div className="flex min-w-0 items-center gap-3"><FileText className="h-5 w-5 shrink-0 text-royal-600" /><div className="min-w-0"><p className="truncate text-sm font-700 text-navy-800">{file.name}</p><p className="text-xs text-navy-400">{formatSize(file.size)} · local preview</p></div></div><button type="button" onClick={() => { setFile(null); setPreview([]); if (inputRef.current) inputRef.current.value = ''; }} aria-label="Remove selected file" className="rounded-lg p-1.5 text-navy-400 hover:bg-white hover:text-navy-700"><X className="h-4 w-4" /></button></div>
            {preview.length > 0 && <div className="mt-4 overflow-x-auto rounded-xl border border-navy-100"><div className="border-b border-navy-100 bg-navy-50 px-4 py-2 text-xs font-800 uppercase tracking-wide text-navy-500">Record preview · first {Math.max(0, preview.length - 1)} rows</div><table className="w-full min-w-[520px] text-left text-xs"><tbody>{preview.map((row, rowIndex) => <tr key={rowIndex} className={rowIndex === 0 ? 'bg-navy-50/50 font-800 text-navy-700' : 'border-t border-navy-50 text-navy-600'}>{row.slice(0, 8).map((cell, cellIndex) => <td key={cellIndex} className="max-w-[180px] truncate px-3 py-2">{cell || '—'}</td>)}</tr>)}</tbody></table></div>}
          </>}

          {error && <div className="mt-4 flex items-start gap-2 rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700"><AlertCircle className="mt-0.5 h-4 w-4 shrink-0" /><span>{error}</span></div>}
          <button type="button" onClick={() => void startPipeline()} disabled={submitting} className="mt-6 flex w-full items-center justify-center rounded-xl bg-royal-600 px-4 py-3.5 text-sm font-800 tracking-wide text-white shadow-sm transition hover:bg-royal-700 disabled:cursor-not-allowed disabled:opacity-60">{submitting ? 'STARTING PIPELINE...' : 'START PIPELINE'}</button>
        </section>
      )}
    </div>
  );
}
