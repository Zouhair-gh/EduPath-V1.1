import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { ClassDetails } from '@/types';

export function useClassDetails(courseId: number) {
  return useQuery<ClassDetails>({
    queryKey: ['class-details', courseId],
    queryFn: async () => {
      const { data } = await api.get(`/dashboard/class/${courseId}/details`);
      return data as ClassDetails;
    },
    staleTime: 15_000,
  });
}