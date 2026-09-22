import { ArrowDown, BarChart3, Database, FileInput, Radio, Server, Sparkles, Workflow } from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';

const NODES = [
  { label: 'Data Sources', detail: 'CSV files provide the campus records.', icon: FileInput, tone: 'bg-amber-50 text-amber-700' },
  { label: 'Kafka', detail: 'Streams each accepted dataset into the pipeline.', icon: Radio, tone: 'bg-royal-50 text-royal-700' },
  { label: 'Redis', detail: 'Publishes live batch state for monitoring.', icon: Server, tone: 'bg-red-50 text-red-700' },
  { label: 'Spark', detail: 'Runs distributed cleaning and transformation.', icon: Sparkles, tone: 'bg-orange-50 text-orange-700' },
  { label: 'Bronze', detail: 'Preserves the ingested source records.', icon: Database, tone: 'bg-amber-50 text-amber-700' },
  { label: 'Silver', detail: 'Stores validated records and rejected data separately.', icon: Database, tone: 'bg-slate-100 text-slate-700' },
  { label: 'Gold', detail: 'Publishes analytics-ready Parquet outputs.', icon: Database, tone: 'bg-yellow-50 text-yellow-700' },
  { label: 'Analytics', detail: 'Queries trusted data for campus insights.', icon: BarChart3, tone: 'bg-teal-50 text-teal-700' },
  { label: 'FastAPI', detail: 'Serves live metrics and records to the dashboard.', icon: Server, tone: 'bg-green-50 text-green-700' },
  { label: 'Dashboard', detail: 'Presents the pipeline and domain results.', icon: Workflow, tone: 'bg-navy-50 text-navy-700' },
];

export function DataLineagePage() {
  return <div className="space-y-5">
    <PageHeader title="Data Lineage" subtitle="Follow one campus record from source CSV to a trusted dashboard insight" />
    <section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-7">
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
        {NODES.map((node, index) => { const Icon = node.icon; return <div key={node.label} className="relative">
          <div className="flex min-h-[142px] flex-col rounded-xl border border-navy-100 bg-canvas p-4">
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${node.tone}`}><Icon className="h-5 w-5" /></div>
            <p className="mt-4 text-sm font-800 text-navy-900">{node.label}</p>
            <p className="mt-1 text-xs leading-5 text-navy-500">{node.detail}</p>
          </div>
          {index < NODES.length - 1 && <ArrowDown className="absolute -bottom-4 left-1/2 z-10 h-4 w-4 -translate-x-1/2 text-navy-300 md:hidden" />}
        </div>; })}
      </div>
    </section>
    <section className="grid gap-5 lg:grid-cols-3">
      <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card lg:col-span-2"><h2 className="font-display text-lg font-700 text-navy-900">How to explain the flow</h2><p className="mt-3 text-sm leading-6 text-navy-500">The source file is accepted by FastAPI, streamed through Kafka, and tracked in Redis. Spark writes immutable Bronze data, validates into Silver, transforms into Gold, and makes the result available to analytics queries and the dashboard.</p></div>
      <div className="rounded-2xl border border-royal-100 bg-royal-50/60 p-5"><p className="text-[11px] font-800 uppercase tracking-[0.16em] text-royal-600">Presentation cue</p><p className="mt-2 text-sm leading-6 text-navy-700">Run a dataset from Data Ingestion, then open Pipeline Monitor to connect this architecture to live status and record counts.</p></div>
    </section>
  </div>;
}