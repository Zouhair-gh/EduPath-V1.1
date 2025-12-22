import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { Student } from '@/types';

export function useStudents(courseId?: number | string, filters: Record<string, any> = {}) {
  return useQuery<Student[]>({
    queryKey: ['students', courseId, filters],
    queryFn: async () => {
      const { data } = await api.get('/students', { params: { courseId, ...filters } });
      return data as Student[];
    },
    staleTime: 15_000,
  });
}