import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/api';
import type { Alert } from '@/types';

export function useAlertActions() {
  const qc = useQueryClient();
  const invalidate = () => qc.invalidateQueries({ queryKey: ['alerts'] });

  const unresolve = useMutation({
    mutationFn: async (id: number | string) => {
      const { data } = await api.patch(`/alerts/${id}/unresolve`);
      return data as { id: number | string; status: string };
    },
    onSuccess: invalidate,
  });

  const setSeverity = useMutation({
    mutationFn: async ({ id, severity }: { id: number | string; severity: Alert['severity'] }) => {
      const { data } = await api.patch(`/alerts/${id}/severity`, { severity });
      return data as { id: number | string; severity: Alert['severity'] };
    },
    onSuccess: invalidate,
  });

  const assign = useMutation({
    mutationFn: async ({ id, assignee }: { id: number | string; assignee: string }) => {
      const { data } = await api.patch(`/alerts/${id}/assign`, { assignee });
      return data as { id: number | string; assignedTo: string };
    },
    onSuccess: invalidate,
  });

  const comment = useMutation({
    mutationFn: async ({ id, content }: { id: number | string; content: string }) => {
      const { data } = await api.post(`/alerts/${id}/comment`, { content });
      return data as { id: number | string; comment: string };
    },
    onSuccess: invalidate,
  });

  const bulkResolve = useMutation({
    mutationFn: async (ids: Array<number | string>) => {
      const { data } = await api.post(`/alerts/bulk/resolve`, { ids });
      return data as { resolved: number };
    },
    onSuccess: invalidate,
  });

  return { unresolve, setSeverity, assign, comment, bulkResolve };
}
