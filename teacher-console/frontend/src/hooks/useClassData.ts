import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { ClassOverview } from '@/types';

export function useClassData(courseId: number) {
  return useQuery<ClassOverview>({
    queryKey: ['class-overview', courseId],
    queryFn: async () => {
      const { data } = await api.get(`/dashboard/class/${courseId}`);
      return data as ClassOverview;
    },
  });
}
