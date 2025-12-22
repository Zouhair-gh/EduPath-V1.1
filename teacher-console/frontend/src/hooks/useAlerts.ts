import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { Alert } from '@/types';

export function useAlerts(courseId?: number | string, severity?: string) {
  return useQuery<Alert[]>({
    queryKey: ['alerts', courseId, severity],
    queryFn: async () => {
      const { data } = await api.get('/alerts', { params: { courseId, severity } });
      return data as Alert[];
    },
    refetchInterval: 15000,
    keepPreviousData: true,
  });
}

export function useResolveAlert() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: number | string) => {
      const { data } = await api.patch(`/alerts/${id}/resolve`);
      return data as { id: number | string; status: string };
    },
    onMutate: async (id: number | string) => {
      await qc.cancelQueries({ queryKey: ['alerts'] });
      const keys = qc.getQueryCache().findAll({ queryKey: ['alerts'] }).map(q => q.queryKey);
      const prev = keys.map((key) => ({ key, data: qc.getQueryData<Alert[]>(key) }));
      for (const { key, data } of prev) {
        if (!data) continue;
        qc.setQueryData<Alert[]>(key, data.filter(a => String(a.id) !== String(id)));
      }
      return { prev };
    },
    onError: (_err, _id, ctx) => {
      if (ctx?.prev) {
        for (const { key, data } of ctx.prev) {
          qc.setQueryData(key, data);
        }
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
}