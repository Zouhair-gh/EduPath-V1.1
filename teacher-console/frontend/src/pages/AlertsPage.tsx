import { Navbar } from '@/components/Layout/Navbar';
import { Sidebar } from '@/components/Layout/Sidebar';
import { useAlerts, useResolveAlert } from '@/hooks/useAlerts';
import { useAlertActions } from '@/hooks/useAlertActions';
import { useExports } from '@/hooks/useExports';
import { AlertsTable } from '@/components/Alerts/AlertsTable';
import { useEffect, useRef } from 'react';
import { useToast } from '@/components/Notifications/ToastProvider';

export default function AlertsPage() {
  const courseId = 1;
  const { data, isLoading, error } = useAlerts(courseId);
  const { mutate: resolveAlert, isPending } = useResolveAlert();
  const { notify } = useToast();
  const { setSeverity, assign, comment } = useAlertActions();
  const { exportAlerts } = useExports();

  const lastCountRef = useRef<number>(0);
  useEffect(() => {
    if (!data) return;
    const highCount = data.filter(a => a.severity === 'HIGH').length;
    if (highCount > lastCountRef.current) {
      notify({ type: 'warning', title: 'Nouvelles alertes', message: `${highCount - lastCountRef.current} alerte(s) critique(s) détectée(s)` });
    }
    lastCountRef.current = highCount;
  }, [data, notify]);

  const onResolve = (id: number | string) => {
    resolveAlert(id, {
      onSuccess: () => notify({ type: 'success', message: `Alerte ${id} résolue` }),
      onError: (e: any) => notify({ type: 'error', message: `Échec résolution: ${e?.message || e}` })
    });
  };
  const onSeverity = (id: number | string, severity: any) => {
    setSeverity.mutate({ id, severity }, {
      onSuccess: () => notify({ type: 'success', message: `Sévérité mise à jour` }),
      onError: (e: any) => notify({ type: 'error', message: `Échec MAJ sévérité: ${e?.message || e}` })
    });
  };
  const onAssign = (id: number | string, assignee: string) => {
    assign.mutate({ id, assignee }, {
      onSuccess: () => notify({ type: 'success', message: `Assigné à ${assignee}` }),
      onError: (e: any) => notify({ type: 'error', message: `Échec assignation: ${e?.message || e}` })
    });
  };
  const onComment = (id: number | string, content: string) => {
    comment.mutate({ id, content }, {
      onSuccess: () => notify({ type: 'success', message: `Commentaire ajouté` }),
      onError: (e: any) => notify({ type: 'error', message: `Échec commentaire: ${e?.message || e}` })
    });
  };
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 p-6">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-semibold">Alertes</h1>
            <button className="px-3 py-1 border rounded" onClick={() => exportAlerts(courseId)}>Exporter CSV</button>
          </div>
          <div className="bg-white p-4 rounded shadow">
            <AlertsTable data={data} loading={isLoading || isPending}
              error={error ? (error as any).message : undefined}
              onResolve={onResolve}
              onSeverity={onSeverity}
              onAssign={onAssign}
              onComment={onComment}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
