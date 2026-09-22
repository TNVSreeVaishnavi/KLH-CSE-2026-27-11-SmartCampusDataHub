import {
  LayoutDashboard,
  Users,
  CalendarCheck,
  BookOpen,
  CalendarDays,
  Bus,
  Building2,
  ShieldCheck,
  GitBranch,
  Workflow,
  UploadCloud,
  type LucideIcon,
} from 'lucide-react';

export interface NavItem {
  id: string;
  label: string;
  icon: LucideIcon;
}

export const NAV_ITEMS: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'students', label: 'Students', icon: Users },
  { id: 'attendance', label: 'Attendance', icon: CalendarCheck },
  { id: 'academics', label: 'Academics', icon: BookOpen },
  { id: 'events', label: 'Events', icon: CalendarDays },
  { id: 'transportation', label: 'Transportation', icon: Bus },
  { id: 'facilities', label: 'Facilities', icon: Building2 },
  { id: 'data-quality', label: 'Data Quality', icon: ShieldCheck },
  { id: 'pipeline-monitor', label: 'Pipeline Monitor', icon: GitBranch },
  { id: 'data-ingestion', label: 'Data Ingestion', icon: UploadCloud },
  { id: 'data-lineage', label: 'Data Lineage', icon: Workflow },
];

export interface SystemStatus {
  label: string;
  value: string;
}

export const SYSTEM_STATUS: SystemStatus[] = [
  { label: 'Database', value: 'Connected' },
  { label: 'Records', value: '86 students' },
  { label: 'Pipeline', value: 'Success' },
  { label: 'Version', value: '1.2.0' },
];
