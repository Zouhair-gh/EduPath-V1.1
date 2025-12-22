export interface Alert {
  id: number;
  studentId: number;
  studentName?: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  riskFactors: string[];
  recommendedActions: string[];
  status: 'ACTIVE' | 'RESOLVED' | 'DISMISSED';
  createdAt: string;
}

export interface ClassOverview {
  totalStudents: number;
  averageEngagement: number;
  averageSuccessRate: number;
  atRiskCount: number;
  profileDistribution: { label: string; count: number; percentage: number; }[];
  recentAlerts: Alert[];
}

export interface Student {
  id: number | string;
  name?: string;
  email?: string;
  courseId?: number;
  engagement?: number;
  successRate?: number;
}

export interface ClassDetails {
  totals: {
    students: number;
    averageEngagement: number;
    averageSuccessRate: number;
    alerts: { active: number; high: number; medium: number; low: number };
  };
  profiles: {
    distribution: { label: string; count: number; percentage: number }[];
  };
  trends: {
    engagementMA7: number | null;
    engagementMA30: number | null;
  };
  topStudents: Array<{
    id: number | string;
    name?: string;
    engagement?: number;
    successRate?: number;
    riskScore: number;
  }>;
  recentAlerts: Alert[];
}
