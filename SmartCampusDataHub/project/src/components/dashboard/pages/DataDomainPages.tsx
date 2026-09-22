import { useEffect, useState, type ReactNode } from 'react';
import { AlertTriangle, Building2, CalendarDays, RefreshCw, Truck } from 'lucide-react';
import { PageHeader } from '@/components/dashboard/PageHeader';
import { campusApi, type DataQualityResponse, type EventsResponse, type FacilitiesResponse, type TransportationResponse } from '@/services/api';

type DataPageProps<T> = {
  title: string;
  subtitle: string;
  load: () => Promise<T>;
  empty: (data: T) => boolean;
  children: (data: T) => ReactNode;
};

function DataPage<T>({ title, subtitle, load, empty, children }: DataPageProps<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = async (showSpinner = false) => {
    if (showSpinner) setRefreshing(true);
    setError(null);
    try {
      setData(await load());
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : `Unable to load ${title.toLowerCase()}.`);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { void refresh(); }, []);

  if (loading) return <div className="flex min-h-[400px] items-center justify-center text-sm text-navy-400">Loading {title.toLowerCase()}...</div>;
  if (error && !data) return <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-red-100 bg-white p-8 text-center shadow-card"><AlertTriangle className="h-10 w-10 text-red-400" /><p className="mt-4 font-display text-xl font-700 text-navy-900">Unable to load {title.toLowerCase()}</p><p className="mt-2 max-w-md text-sm text-navy-400">{error}</p><button onClick={() => void refresh(true)} className="mt-5 rounded-xl border border-navy-200 px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600">Retry</button></div>;
  if (!data || empty(data)) return <div className="space-y-5"><PageHeader title={title} subtitle={subtitle} /><div className="flex min-h-[360px] flex-col items-center justify-center rounded-2xl border border-dashed border-navy-200 bg-white p-8 text-center shadow-card"><AlertTriangle className="h-10 w-10 text-navy-300" /><p className="mt-4 font-display text-xl font-700 text-navy-900">No {title.toLowerCase()} available</p><p className="mt-2 max-w-md text-sm text-navy-400">Gold Parquet has not produced records for this domain yet.</p><button onClick={() => void refresh(true)} className="mt-5 flex items-center gap-2 rounded-xl border border-navy-200 px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600"><RefreshCw className="h-4 w-4" /> Refresh</button></div></div>;

  return <div className="space-y-5"><div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between"><PageHeader title={title} subtitle={subtitle} /><button onClick={() => void refresh(true)} disabled={refreshing} aria-label={`Refresh ${title}`} className="flex items-center gap-2 self-start rounded-xl border border-navy-200 bg-white px-3.5 py-2.5 text-[13px] font-600 text-navy-700 hover:border-royal-300 hover:text-royal-600 disabled:opacity-60"><RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh</button></div>{error && <div className="rounded-xl border border-amber-100 bg-amber-50 px-4 py-3 text-sm text-amber-700">Refresh warning: {error}</div>}{children(data)}</div>;
}

function Metric({ label, value }: { label: string; value: string | number | null | undefined }) {
  return <div className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card"><p className="text-xs font-600 text-navy-400">{label}</p><p className="mt-2 font-display text-2xl font-800 text-navy-900">{value ?? 'n/a'}</p></div>;
}

export function EventsPage() {
  return <DataPage title="Events" subtitle="Campus events and participation capacity from Gold Parquet" load={campusApi.getEvents} empty={(data) => data.total === 0}>
    {(data: EventsResponse) => <><div className="grid gap-4 sm:grid-cols-3"><Metric label="Total Events" value={data.statistics.total_events} /><Metric label="Total Capacity" value={data.statistics.total_capacity} /><Metric label="Average Capacity" value={data.statistics.avg_capacity} /></div><section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6"><div className="flex items-center gap-2"><CalendarDays className="h-5 w-5 text-royal-600" /><h2 className="font-display text-lg font-700 text-navy-900">Recent Events</h2></div><div className="mt-4 overflow-x-auto"><table className="w-full min-w-[620px] text-left text-sm"><thead><tr className="border-b border-navy-100 text-xs uppercase tracking-wide text-navy-400"><th className="pb-3">Event</th><th className="pb-3">Date</th><th className="pb-3">Location</th><th className="pb-3">Capacity</th></tr></thead><tbody>{data.records.map((event) => <tr key={event.event_id} className="border-b border-navy-50 last:border-0"><td className="py-3 font-700 text-navy-800">{event.name}</td><td className="py-3 text-navy-600">{event.date}</td><td className="py-3 text-navy-600">{event.location}</td><td className="py-3 text-navy-600">{event.capacity}</td></tr>)}</tbody></table></div></section></>}
  </DataPage>;
}

export function TransportationPage() {
  return <DataPage title="Transportation" subtitle="Vehicle status, capacity, and utilization from Gold Parquet" load={campusApi.getTransportation} empty={(data) => data.health.total_vehicles === 0}>
    {(data: TransportationResponse) => <><div className="grid gap-4 sm:grid-cols-4"><Metric label="Total Vehicles" value={data.health.total_vehicles} /><Metric label="Active Vehicles" value={data.health.active_count} /><Metric label="Maintenance" value={data.health.maintenance_count} /><Metric label="Fleet Health" value={`${data.health.health_percentage ?? 0}%`} /></div><section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6"><div className="flex items-center gap-2"><Truck className="h-5 w-5 text-royal-600" /><h2 className="font-display text-lg font-700 text-navy-900">Vehicle Status</h2></div><div className="mt-4 grid gap-3 sm:grid-cols-3">{data.status.map((item, index) => <div key={`${String(item.status)}-${index}`} className="rounded-xl bg-canvas p-4"><p className="text-sm font-700 text-navy-800">{String(item.status)}</p><p className="mt-2 text-2xl font-800 text-navy-900">{String(item.count ?? 0)}</p><p className="text-xs text-navy-400">vehicles</p></div>)}</div></section></>}
  </DataPage>;
}

export function FacilitiesPage() {
  return <DataPage title="Facilities" subtitle="Facility operations, maintenance, and capacity from Gold Parquet" load={campusApi.getFacilities} empty={(data) => data.maintenance.total_facilities === 0}>
    {(data: FacilitiesResponse) => <><div className="grid gap-4 sm:grid-cols-4"><Metric label="Total Facilities" value={data.maintenance.total_facilities} /><Metric label="Operational" value={data.maintenance.operational_count} /><Metric label="Maintenance" value={data.maintenance.maintenance_count} /><Metric label="Operational Rate" value={`${data.maintenance.operational_percentage ?? 0}%`} /></div><section className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card sm:p-6"><div className="flex items-center gap-2"><Building2 className="h-5 w-5 text-royal-600" /><h2 className="font-display text-lg font-700 text-navy-900">Facility Status</h2></div><div className="mt-4 grid gap-3 sm:grid-cols-3">{data.status.map((item, index) => <div key={`${String(item.status)}-${index}`} className="rounded-xl bg-canvas p-4"><p className="text-sm font-700 text-navy-800">{String(item.status)}</p><p className="mt-2 text-2xl font-800 text-navy-900">{String(item.count ?? 0)}</p><p className="text-xs text-navy-400">facilities</p></div>)}</div></section></>}
  </DataPage>;
}

export function DataQualityPage() {
  return <DataPage title="Data Quality" subtitle="Validation and completeness metrics from Gold Parquet" load={campusApi.getDataQuality} empty={(data) => Object.keys(data.metrics).length === 0}>
    {(data: DataQualityResponse) => <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{Object.entries(data.metrics).map(([domain, metrics]) => <div key={domain} className="rounded-2xl border border-navy-100 bg-white p-5 shadow-card"><p className="font-display text-lg font-700 capitalize text-navy-900">{domain}</p><div className="mt-4 grid grid-cols-2 gap-3">{[['Input', metrics.input_records], ['Valid', metrics.valid_records], ['Rejected', metrics.rejected_records ?? 'n/a'], ['Missing', metrics.missing_values], ['Duplicates', metrics.duplicates], ['Quality', metrics.quality_score != null ? `${metrics.quality_score}%` : 'n/a']].map(([label, value]) => <div key={String(label)} className="rounded-lg bg-canvas p-3"><p className="text-[11px] text-navy-400">{label}</p><p className="mt-1 text-lg font-800 text-navy-900">{String(value ?? 'n/a')}</p></div>)}</div></div>)}</section>}
  </DataPage>;
}
