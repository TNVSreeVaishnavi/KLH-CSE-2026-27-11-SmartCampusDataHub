import {
  Users,
  CalendarCheck,
  GraduationCap,
  CalendarDays,
  Bus,
  Building2,
  type LucideIcon,
} from 'lucide-react';

export type Trend = 'up' | 'down' | 'flat';

export interface KpiMetric {
  label: string;
  value: string;
  change: string;
  trend: Trend;
  icon: LucideIcon;
  accent: 'royal' | 'green' | 'navy' | 'amber' | 'teal' | 'violet';
}

export const OVERVIEW_KPIS: KpiMetric[] = [
  {
    label: 'Total Students',
    value: '86',
    change: '+4 this week',
    trend: 'up',
    icon: Users,
    accent: 'royal',
  },
  {
    label: 'Average Attendance',
    value: '92.4%',
    change: '+1.2%',
    trend: 'up',
    icon: CalendarCheck,
    accent: 'green',
  },
  {
    label: 'Academic Performance',
    value: '3.68 GPA',
    change: '+0.14',
    trend: 'up',
    icon: GraduationCap,
    accent: 'navy',
  },
  {
    label: 'Total Events',
    value: '12',
    change: '+3 this month',
    trend: 'up',
    icon: CalendarDays,
    accent: 'amber',
  },
  {
    label: 'Transportation Usage',
    value: '1,420',
    change: '+86 rides',
    trend: 'up',
    icon: Bus,
    accent: 'teal',
  },
  {
    label: 'Facilities Active',
    value: '34 / 36',
    change: '2 maintenance',
    trend: 'flat',
    icon: Building2,
    accent: 'violet',
  },
];

export interface DepartmentData {
  department: string;
  students: number;
}

export const STUDENTS_BY_DEPARTMENT: DepartmentData[] = [
  { department: 'Computer Sci.', students: 24 },
  { department: 'Engineering', students: 18 },
  { department: 'Business', students: 15 },
  { department: 'Arts & Hum.', students: 11 },
  { department: 'Sciences', students: 10 },
  { department: 'Medicine', students: 8 },
];

export interface AttendanceSegment {
  label: string;
  value: number;
  color: string;
}

export const ATTENDANCE_SEGMENTS: AttendanceSegment[] = [
  { label: 'Present', value: 79, color: '#1d54f0' },
  { label: 'Absent', value: 4, color: '#ef4444' },
  { label: 'Late', value: 2, color: '#f59e0b' },
  { label: 'Excused', value: 1, color: '#94a3b8' },
];

export type EventStatus = 'Scheduled' | 'Completed' | 'Ongoing';

export interface CampusEvent {
  event: string;
  type: string;
  date: string;
  participants: number;
  status: EventStatus;
}

export const RECENT_EVENTS: CampusEvent[] = [
  {
    event: 'Tech Symposium 2026',
    type: 'Academic',
    date: 'Sep 12, 2026',
    participants: 142,
    status: 'Scheduled',
  },
  {
    event: 'Inter-Dept Football',
    type: 'Sports',
    date: 'Sep 08, 2026',
    participants: 68,
    status: 'Completed',
  },
  {
    event: 'AI Research Workshop',
    type: 'Workshop',
    date: 'Sep 06, 2026',
    participants: 34,
    status: 'Ongoing',
  },
  {
    event: 'Cultural Fest Preview',
    type: 'Cultural',
    date: 'Sep 15, 2026',
    participants: 210,
    status: 'Scheduled',
  },
  {
    event: 'Hackathon — Data Hub',
    type: 'Competition',
    date: 'Sep 03, 2026',
    participants: 56,
    status: 'Completed',
  },
];

export interface KeyInsight {
  title: string;
  description: string;
  metric: string;
  icon: LucideIcon;
  accent: 'royal' | 'green' | 'amber' | 'navy';
}

export const KEY_INSIGHTS: KeyInsight[] = [
  {
    title: 'Attendance trending upward',
    description: 'Average daily attendance rose 1.2% over the last 7 days, driven by improved morning transport.',
    metric: '92.4%',
    icon: CalendarCheck,
    accent: 'green',
  },
  {
    title: 'CS department growth',
    description: 'Computer Science enrolled 4 new students this week, now the largest department on campus.',
    metric: '+28%',
    icon: Users,
    accent: 'royal',
  },
  {
    title: 'Facilities utilization high',
    description: '94% of facilities are active. Library and Lab 3 are at peak capacity during afternoon slots.',
    metric: '94%',
    icon: Building2,
    accent: 'amber',
  },
  {
    title: 'Pipeline health stable',
    description: 'Data ingestion and transformation completed successfully for 14 consecutive batches.',
    metric: '14/14',
    icon: GraduationCap,
    accent: 'navy',
  },
];

export type ServiceStatus = 'Operational' | 'Degraded' | 'Down';

export interface SystemService {
  name: string;
  status: ServiceStatus;
  latency: string;
  uptime: string;
}

export const SYSTEM_SERVICES: SystemService[] = [
  { name: 'Data Ingestion', status: 'Operational', latency: '0.8s', uptime: '99.9%' },
  { name: 'Data Cleaning', status: 'Operational', latency: '1.1s', uptime: '99.8%' },
  { name: 'Data Validation', status: 'Operational', latency: '0.4s', uptime: '100%' },
  { name: 'Data Transformation', status: 'Operational', latency: '1.5s', uptime: '99.7%' },
  { name: 'Database Load', status: 'Operational', latency: '0.3s', uptime: '99.9%' },
  { name: 'Analytics Engine', status: 'Operational', latency: '0.6s', uptime: '99.8%' },
];
