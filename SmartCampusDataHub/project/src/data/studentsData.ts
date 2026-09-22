import {
  Users,
  Building2,
  GraduationCap,
  CalendarCheck,
  CheckCircle2,
  XCircle,
  Clock,
  FileText,
  type LucideIcon,
} from 'lucide-react';
import type { Trend, KpiMetric } from './overviewData';

export const DEPARTMENTS = [
  'Computer Sci.',
  'Engineering',
  'Business',
  'Arts & Hum.',
  'Sciences',
  'Medicine',
] as const;

export const YEARS = ['Year 1', 'Year 2', 'Year 3', 'Year 4'] as const;

export const STUDENTS_KPIS: KpiMetric[] = [
  {
    label: 'Total Students',
    value: '86',
    change: '+4 this week',
    trend: 'up',
    icon: Users,
    accent: 'royal',
  },
  {
    label: 'Departments',
    value: '6',
    change: 'All active',
    trend: 'flat',
    icon: Building2,
    accent: 'navy',
  },
  {
    label: 'Year Groups',
    value: '4',
    change: 'Balanced',
    trend: 'flat',
    icon: GraduationCap,
    accent: 'teal',
  },
];

export interface YearData {
  year: string;
  students: number;
}

export const STUDENTS_BY_YEAR: YearData[] = [
  { year: 'Year 1', students: 26 },
  { year: 'Year 2', students: 24 },
  { year: 'Year 3', students: 21 },
  { year: 'Year 4', students: 15 },
];

export interface Student {
  id: string;
  name: string;
  email: string;
  department: string;
  year: string;
  gpa: number;
  status: 'Active' | 'On Leave' | 'Graduated';
  avatarColor: string;
}

const AVATAR_COLORS = [
  'from-royal-500 to-royal-700',
  'from-emerald-500 to-emerald-700',
  'from-navy-600 to-navy-800',
  'from-amber-500 to-amber-600',
  'from-teal-500 to-teal-700',
  'from-violet-500 to-violet-700',
  'from-rose-500 to-rose-700',
  'from-cyan-500 to-cyan-700',
];

export const STUDENTS: Student[] = [
  { id: 'S001', name: 'Vaishnavi Kulkarni', email: 'vaishnavi@university.edu', department: 'Computer Sci.', year: 'Year 3', gpa: 3.92, status: 'Active', avatarColor: AVATAR_COLORS[0] },
  { id: 'S002', name: 'Arjun Mehta', email: 'arjun.mehta@university.edu', department: 'Engineering', year: 'Year 2', gpa: 3.75, status: 'Active', avatarColor: AVATAR_COLORS[1] },
  { id: 'S003', name: 'Priya Sharma', email: 'priya.sharma@university.edu', department: 'Business', year: 'Year 4', gpa: 3.81, status: 'Active', avatarColor: AVATAR_COLORS[2] },
  { id: 'S004', name: 'Rohan Patel', email: 'rohan.patel@university.edu', department: 'Computer Sci.', year: 'Year 1', gpa: 3.60, status: 'Active', avatarColor: AVATAR_COLORS[3] },
  { id: 'S005', name: 'Ananya Reddy', email: 'ananya.r@university.edu', department: 'Sciences', year: 'Year 3', gpa: 3.88, status: 'Active', avatarColor: AVATAR_COLORS[4] },
  { id: 'S006', name: 'Karthik Nair', email: 'karthik.nair@university.edu', department: 'Medicine', year: 'Year 4', gpa: 3.95, status: 'Active', avatarColor: AVATAR_COLORS[5] },
  { id: 'S007', name: 'Sneha Iyer', email: 'sneha.iyer@university.edu', department: 'Arts & Hum.', year: 'Year 2', gpa: 3.70, status: 'Active', avatarColor: AVATAR_COLORS[6] },
  { id: 'S008', name: 'Aditya Joshi', email: 'aditya.j@university.edu', department: 'Engineering', year: 'Year 1', gpa: 3.45, status: 'Active', avatarColor: AVATAR_COLORS[7] },
  { id: 'S009', name: 'Diya Gupta', email: 'diya.gupta@university.edu', department: 'Business', year: 'Year 3', gpa: 3.82, status: 'On Leave', avatarColor: AVATAR_COLORS[0] },
  { id: 'S010', name: 'Vikram Singh', email: 'vikram.s@university.edu', department: 'Computer Sci.', year: 'Year 4', gpa: 3.90, status: 'Active', avatarColor: AVATAR_COLORS[1] },
  { id: 'S011', name: 'Ishita Verma', email: 'ishita.v@university.edu', department: 'Sciences', year: 'Year 1', gpa: 3.55, status: 'Active', avatarColor: AVATAR_COLORS[2] },
  { id: 'S012', name: 'Arnav Desai', email: 'arnav.desai@university.edu', department: 'Engineering', year: 'Year 3', gpa: 3.68, status: 'Active', avatarColor: AVATAR_COLORS[3] },
  { id: 'S013', name: 'Meera Krishnan', email: 'meera.k@university.edu', department: 'Medicine', year: 'Year 2', gpa: 3.85, status: 'Active', avatarColor: AVATAR_COLORS[4] },
  { id: 'S014', name: 'Sai Prasad', email: 'sai.prasad@university.edu', department: 'Arts & Hum.', year: 'Year 4', gpa: 3.72, status: 'Graduated', avatarColor: AVATAR_COLORS[5] },
  { id: 'S015', name: 'Tanvi Bhat', email: 'tanvi.bhat@university.edu', department: 'Business', year: 'Year 1', gpa: 3.65, status: 'Active', avatarColor: AVATAR_COLORS[6] },
];

export const ATTENDANCE_KPIS: KpiMetric[] = [
  {
    label: 'Average Attendance',
    value: '92.4%',
    change: '+1.2%',
    trend: 'up',
    icon: CalendarCheck,
    accent: 'green',
  },
  {
    label: 'Present',
    value: '79',
    change: '92% of total',
    trend: 'up',
    icon: CheckCircle2,
    accent: 'royal',
  },
  {
    label: 'Absent',
    value: '4',
    change: '4.7%',
    trend: 'down',
    icon: XCircle,
    accent: 'amber',
  },
  {
    label: 'Late',
    value: '2',
    change: '2.3%',
    trend: 'flat',
    icon: Clock,
    accent: 'navy',
  },
  {
    label: 'Excused',
    value: '1',
    change: '1.2%',
    trend: 'flat',
    icon: FileText,
    accent: 'teal',
  },
];

export interface AttendanceByDept {
  department: string;
  rate: number;
}

export const ATTENDANCE_BY_DEPARTMENT: AttendanceByDept[] = [
  { department: 'Computer Sci.', rate: 95 },
  { department: 'Engineering', rate: 91 },
  { department: 'Business', rate: 94 },
  { department: 'Arts & Hum.', rate: 88 },
  { department: 'Sciences', rate: 93 },
  { department: 'Medicine', rate: 96 },
];

export interface LowAttendanceStudent {
  id: string;
  name: string;
  department: string;
  year: string;
  attendancePct: number;
  missed: number;
  total: number;
  trend: Trend;
}

export const LOW_ATTENDANCE_STUDENTS: LowAttendanceStudent[] = [
  { id: 'S004', name: 'Rohan Patel', department: 'Computer Sci.', year: 'Year 1', attendancePct: 71, missed: 9, total: 31, trend: 'down' },
  { id: 'S008', name: 'Aditya Joshi', department: 'Engineering', year: 'Year 1', attendancePct: 74, missed: 8, total: 31, trend: 'down' },
  { id: 'S007', name: 'Sneha Iyer', department: 'Arts & Hum.', year: 'Year 2', attendancePct: 78, missed: 7, total: 31, trend: 'flat' },
  { id: 'S011', name: 'Ishita Verma', department: 'Sciences', year: 'Year 1', attendancePct: 79, missed: 7, total: 33, trend: 'up' },
  { id: 'S015', name: 'Tanvi Bhat', department: 'Business', year: 'Year 1', attendancePct: 81, missed: 6, total: 32, trend: 'up' },
];
