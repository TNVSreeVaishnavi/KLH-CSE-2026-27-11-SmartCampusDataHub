import { useEffect, useState } from 'react';
import { Construction } from 'lucide-react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { OverviewPage } from './pages/OverviewPage';
import { StudentsPage } from './pages/StudentsPage';
import { AttendancePage } from './pages/AttendancePage';
import { AcademicsPage } from './pages/AcademicsPage';
import { PipelineMonitorPage } from './pages/PipelineMonitorPage';
import { DataIngestionPage } from './pages/DataIngestionPage';
import { DataLineagePage } from './pages/DataLineagePage';
import { DataQualityPage, EventsPage, FacilitiesPage, TransportationPage } from './pages/DataDomainPages';
import { NAV_ITEMS } from '@/data/navigation';
import { useSession } from '@/auth/session';
import { campusApi, type HealthResponse, type PipelineResponse } from '@/services/api';

export function DashboardShell() {
  const { user } = useSession();
  const [activeId, setActiveId] = useState('overview');
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [pipeline, setPipeline] = useState<PipelineResponse | null>(null);

  useEffect(() => {
    void Promise.all([campusApi.getHealth(), campusApi.getPipeline()])
      .then(([healthData, pipelineData]) => {
        setHealth(healthData);
        setPipeline(pipelineData);
      })
      .catch(() => {
        setHealth(null);
        setPipeline(null);
      });
  }, []);

  const activeLabel = NAV_ITEMS.find((n) => n.id === activeId)?.label ?? 'Overview';
  const isActiveOverview = activeId === 'overview';

  const handleNavigate = (id: string) => {
    setActiveId(id);
    setMobileNavOpen(false);
  };

  return (
    <div className="flex h-[100svh] w-full overflow-hidden bg-canvas">
      <Sidebar
        activeId={activeId}
        onNavigate={handleNavigate}
        mobileOpen={mobileNavOpen}
        onCloseMobile={() => setMobileNavOpen(false)}
        health={health}
        pipeline={pipeline}
      />

      {/* Main area */}
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onOpenMobileNav={() => setMobileNavOpen(true)} />

        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
          {/* Page content */}
          <div key={activeId} className="animate-fade-in-up">
            {isActiveOverview ? (
              <OverviewPage userName={user?.name ?? 'User'} />
            ) : activeId === 'students' ? (
              <StudentsPage />
            ) : activeId === 'attendance' ? (
              <AttendancePage />
            ) : activeId === 'academics' ? (
              <AcademicsPage />
            ) : activeId === 'pipeline-monitor' ? (
              <PipelineMonitorPage onNavigate={handleNavigate} />
            ) : activeId === 'data-ingestion' ? (
              <DataIngestionPage onNavigate={handleNavigate} />
            ) : activeId === 'data-lineage' ? (
              <DataLineagePage />
            ) : activeId === 'events' ? (
              <EventsPage />
            ) : activeId === 'transportation' ? (
              <TransportationPage />
            ) : activeId === 'facilities' ? (
              <FacilitiesPage />
            ) : activeId === 'data-quality' ? (
              <DataQualityPage />
            ) : (
              <>
                <div className="mb-6 max-w-4xl">
                  <p className="text-[13px] font-600 text-royal-600">
                    Welcome back, {user?.name ?? 'User'}!
                  </p>
                  <h1 className="mt-1 font-display text-2xl font-800 tracking-tight text-navy-900 sm:text-3xl">
                    {activeLabel}
                  </h1>
                  <p className="mt-2 text-sm text-navy-400">
                    Manage and monitor {activeLabel.toLowerCase()} data across campus.
                  </p>
                </div>
                <PlaceholderPage label={activeLabel} />
              </>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

function PlaceholderPage({ label }: { label: string }) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center rounded-2xl border border-dashed border-navy-200 bg-white/60 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-navy-50 text-navy-300">
        <Construction className="h-8 w-8" />
      </div>
      <h3 className="mt-5 font-display text-xl font-700 text-navy-800">{label}</h3>
      <p className="mt-2 max-w-sm text-sm text-navy-400">
        This module is part of the Smart Campus Data Hub and will be populated with live data
        from your data engineering pipeline.
      </p>
    </div>
  );
}
