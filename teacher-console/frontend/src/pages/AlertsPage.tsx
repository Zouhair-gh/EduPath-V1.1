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
        <main className="flex-1 p-6">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-bold text-blue-700 flex items-center gap-2">
              <svg className="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M18.364 5.636l-1.414 1.414A9 9 0 105.636 18.364l1.414-1.414" /></svg>
              Alertes
            </h1>
            <button className="px-4 py-2 border rounded bg-blue-600 text-white hover:bg-blue-700 transition" onClick={() => exportAlerts(courseId)}>Exporter CSV</button>
          </div>
          <section className="bg-white p-6 rounded shadow">
            <AlertsTable data={data} loading={isLoading || isPending}
              error={error ? (error as any).message : undefined}
              onResolve={onResolve}
              onSeverity={onSeverity}
              onAssign={onAssign}
              onComment={onComment}
            />
          </section>
        </main>
      </div>
    </div>
  );
}
