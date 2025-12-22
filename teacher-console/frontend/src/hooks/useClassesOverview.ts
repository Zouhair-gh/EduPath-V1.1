import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export type CourseOverview = {
  courseId: number;
  totalStudents: number;
  averageEngagement: number;
  averageSuccessRate: number;
  atRiskCount: number;
  profileDistribution: { label: string; count: number; percentage: number }[];
};

export function useClassesOverview() {
  return useQuery<CourseOverview[]>({
    queryKey: ['classes-overview'],
    queryFn: async () => {
      const { data } = await api.get('/dashboard/classes');
      return data as CourseOverview[];
    },
    staleTime: 15_000,
  });
}