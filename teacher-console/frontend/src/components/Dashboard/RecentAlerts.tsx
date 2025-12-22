import type { Alert } from '@/types';
import { useResolveAlert } from '@/hooks/useAlerts';
import { useToast } from '@/components/Notifications/ToastProvider';

export function RecentAlerts({ alerts }: { alerts: Alert[] }) {
  const { mutate: resolveAlert } = useResolveAlert();
  const { notify } = useToast();
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="font-semibold mb-2">Dernières alertes</div>
      {(!alerts || alerts.length === 0) && <div className="text-gray-500">Aucune alerte récente</div>}
      {alerts && alerts.length > 0 && (
        <ul className="divide-y">
          {alerts.map(a => (
            <li key={a.id} className="py-2 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 rounded text-white text-xs ${a.severity === 'HIGH' ? 'bg-red-600' : a.severity === 'MEDIUM' ? 'bg-amber-600' : 'bg-green-600'}`}>{a.severity}</span>
                <div className="text-sm text-gray-700">Étudiant {a.studentName || a.studentId}</div>
                <div className="text-xs text-gray-500">{new Date(a.createdAt).toLocaleString()}</div>
              </div>
              <button className="px-2 py-1 text-sm bg-blue-600 text-white rounded" onClick={() => resolveAlert(a.id, {
                onSuccess: () => notify({ type: 'success', message: `Alerte ${a.id} résolue` }),
                onError: (e: any) => notify({ type: 'error', message: `Échec: ${e?.message || e}` })
              })}>Résoudre</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}