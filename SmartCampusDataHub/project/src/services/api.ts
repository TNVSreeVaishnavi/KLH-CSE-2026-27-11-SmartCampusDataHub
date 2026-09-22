const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

export interface OverviewResponse {
  kpis: {
    total_students: number;
    average_attendance: number;
    average_gpa: number;
    total_events: number;
    transportation_vehicles: number;
    active_facilities: number;
  };
  students_by_department: Array<{ department: string; count: number }>;
  attendance_by_status: Array<{ status: string; count: number; avg_attendance: number }>;
  recent_events: Array<{
    event_id: string;
    name: string;
    date: string;
    event_type: string | null;
    location: string | null;
    capacity: number | null;
    organizer: string | null;
  }>;
  pipeline: PipelineSummary;
}

export interface HealthResponse {
  status: string;
  api: string;
  version: string;
  database: string;
  database_path: string;
  records: Record<string, number>;
}

export interface PipelineStatus {
  pipeline_status: string;
  current_stage: string;
  dataset: string;
  batch_id: string;
  started_at: string | null;
  completed_at: string | null;
  records_received: number | string;
  records_cleaned: number | string;
  records_validated: number | string;
  records_rejected: number | string;
  records_written: number | string;
  error_message: string;
}

export interface PipelineHistoryResponse {
  history: PipelineStatus[];
}

export interface PipelineUploadResponse {
  batch_id: string;
  dataset: string;
  filename: string;
  status: string;
  records_received: number;
}

export interface PipelineExecution {
  execution_id: number;
  start_time: string;
  end_time: string | null;
  status: string;
  duration_seconds: number | null;
  total_input_records: number | null;
  total_output_records: number | null;
  error_message?: string | null;
}

export interface PipelineStage {
  metric_id?: number;
  execution_id?: number;
  stage_name: string;
  input_records?: number;
  output_records?: number;
  records_removed?: number;
  status: string;
  duration_seconds: number;
  error_message?: string | null;
}

export interface PipelineSummary {
  last_execution: PipelineExecution | null;
  total_executions: number;
  successful_executions: number;
  success_rate: number;
  average_duration_seconds: number;
}

export interface PipelineResponse {
  summary: PipelineSummary;
  execution_id: number | null;
  stages: PipelineStage[];
  domains: Array<Record<string, unknown>>;
}

export interface StudentRecord {
  student_id: string;
  name: string;
  email: string;
  age: number | null;
  gender: string | null;
  department: string;
  status: string;
  age_group: string | null;
  year: string;
  avg_gpa: number | null;
}

export interface StudentsResponse {
  records: StudentRecord[];
  total: number;
}

export interface AttendanceRecord {
  student_id: string;
  name: string;
  email?: string;
  department?: string;
  avg_attendance: number;
  sessions_tracked?: number;
  missed_sessions?: number;
}

export interface AttendanceResponse {
  statistics: {
    total_students: number;
    avg_attendance: number;
    min_attendance: number;
    max_attendance: number;
  };
  by_status: Array<{ status: string; count: number; avg_attendance: number }>;
  by_department: Array<{ department: string; students: number; avg_attendance: number; total_sessions: number }>;
  low_attendance: { records: AttendanceRecord[]; total: number };
  trends: Array<Record<string, string | number>>;
}

export interface AcademicResponse {
  statistics: {
    total_students: number;
    avg_gpa: number;
    min_gpa: number | null;
    max_gpa: number | null;
  };
  grades: Array<{ grade: string; count: number }>;
  by_department: Array<{
    department: string;
    students: number;
    avg_gpa: number;
    min_gpa: number | null;
    max_gpa: number | null;
    total_courses: number;
  }>;
  top_performers: {
    records: Array<{
      student_id: string;
      name: string;
      email: string | null;
      avg_gpa: number;
      courses: number;
    }>;
    total: number;
  };
  struggling_students: {
    records: Array<{
      student_id: string;
      name: string;
      department: string;
      avg_gpa: number;
      courses: number;
      failing_grades: number;
    }>;
    total: number;
  };
  grade_statistics: {
    total_grades: number;
    avg_gpa: number;
    min_gpa: number | null;
    max_gpa: number | null;
    excellent_count: number;
    good_count: number;
    average_count: number;
    below_average_count: number;
  };
  top_courses: Array<{
    course_id: string;
    course_name: string;
    enrollment: number;
    avg_gpa: number;
    excellent_students: number;
  }>;
}

export interface EventsResponse {
  statistics: { total_events: number; total_capacity: number; avg_capacity: number };
  by_location: Array<{ location: string; count: number; total_capacity: number }>;
  records: Array<{ event_id: string; name: string; date: string; location: string; capacity: number; organizer: string }>;
  total: number;
}

export interface TransportationResponse {
  status: Array<Record<string, string | number>>;
  by_type: Array<Record<string, string | number>>;
  utilization: Array<Record<string, string | number>>;
  health: Record<string, string | number>;
}

export interface FacilitiesResponse {
  status: Array<Record<string, string | number>>;
  by_type: Array<Record<string, string | number>>;
  overview: Array<Record<string, string | number>>;
  maintenance: Record<string, string | number>;
  by_location: Array<Record<string, string | number>>;
}

export interface DataQualityResponse {
  metrics: Record<string, Record<string, string | number | null>>;
  basic_metrics: Record<string, Record<string, string | number>>;
}

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`;
    try {
      const body = (await response.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // Keep the status-based message when the server does not return JSON.
    }
    throw new Error(detail);
  }

  return response.json() as Promise<T>;
}

export const campusApi = {
  getOverview: () => request<OverviewResponse>('/api/overview'),
  getStudents: (params: { department?: string; year?: number } = {}) => {
    const query = new URLSearchParams();
    if (params.department) query.set('department', params.department);
    if (params.year) query.set('year', `${params.year}`);
    const suffix = query.toString() ? `?${query.toString()}` : '';
    return request<StudentsResponse>(`/api/students${suffix}`);
  },
  getAttendance: (params: { department?: string; threshold?: number } = {}) => {
    const query = new URLSearchParams();
    if (params.department) query.set('department', params.department);
    if (params.threshold !== undefined) query.set('threshold', `${params.threshold}`);
    const suffix = query.toString() ? `?${query.toString()}` : '';
    return request<AttendanceResponse>(`/api/attendance${suffix}`);
  },
  getAcademics: () => request<AcademicResponse>('/api/academics'),
  getEvents: () => request<EventsResponse>('/api/events'),
  getTransportation: () => request<TransportationResponse>('/api/transportation'),
  getFacilities: () => request<FacilitiesResponse>('/api/facilities'),
  getDataQuality: () => request<DataQualityResponse>('/api/data-quality'),
  getHealth: () => request<HealthResponse>('/api/health'),
  getPipelineStatus: () => request<PipelineStatus>('/api/pipeline/status'),
  getPipelineHistory: () => request<PipelineHistoryResponse>('/api/pipeline/history'),
  getPipeline: () => request<PipelineResponse>('/api/pipeline'),
  uploadDataset: async (dataset: string, file: File) => {
    const formData = new FormData();
    formData.append('dataset', dataset);
    formData.append('file', file);
    const response = await fetch(`${API_BASE_URL}/api/ingestion/upload`, {
      method: 'POST',
      headers: { Accept: 'application/json' },
      body: formData,
    });
    if (!response.ok) {
      let detail = `Upload failed with status ${response.status}`;
      try {
        const body = (await response.json()) as { detail?: string };
        if (body.detail) detail = body.detail;
      } catch {
        // Keep the status-based message when the server does not return JSON.
      }
      throw new Error(detail);
    }
    return response.json() as Promise<PipelineUploadResponse>;
  },
};
