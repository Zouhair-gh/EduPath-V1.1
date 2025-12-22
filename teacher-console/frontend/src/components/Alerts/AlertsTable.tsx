import type { Alert } from '@/types';

export function AlertsTable({ data, loading, error, onResolve, onSeverity, onAssign, onComment }: {
  data: Alert[] | undefined;
  loading: boolean;
  error?: string;
  onResolve: (id: number | string) => void;
  onSeverity: (id: number | string, severity: Alert['severity']) => void;
  onAssign: (id: number | string, assignee: string) => void;
  onComment: (id: number | string, content: string) => void;
}) {
  if (loading) return <div className="animate-pulse text-gray-500">Chargement des alertes…</div>;
  if (error) return <div className="text-red-600">Erreur: {error}</div>;
  if (!data || data.length === 0) return <div className="text-gray-500">Aucune alerte</div>;
  return (
    <div className="overflow-auto rounded border">
      <table className="min-w-full divide-y">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left p-2">Étudiant</th>
            <th className="text-left p-2">Sévérité</th>
            <th className="text-left p-2">Actions</th>
            <th className="text-left p-2">Actions</th>
            <th className="text-left p-2">Assignation</th>
            <th className="text-left p-2">Commentaire</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((a) => (
            <tr key={String(a.id)} className="hover:bg-gray-50">
              <td className="p-2">{a.studentName || a.studentId}</td>
              <td className="p-2">
                <span className={`px-2 py-1 rounded text-white ${a.severity === 'HIGH' ? 'bg-red-600' : a.severity === 'MEDIUM' ? 'bg-amber-600' : 'bg-green-600'}`}>{a.severity}</span>
              </td>
              <td className="p-2">
                <div className="flex items-center gap-2">
                  <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700" onClick={() => onResolve(a.id)}>Résoudre</button>
                  <select aria-label="Changer la sévérité" className="border rounded px-2 py-1 text-sm" value={a.severity} onChange={(e) => onSeverity(a.id, e.target.value as Alert['severity'])}>
                    <option value="HIGH">HIGH</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="LOW">LOW</option>
                  </select>
                </div>
              </td>
              <td className="p-2">
                <button className="px-2 py-1 text-sm border rounded" onClick={() => {
                  const val = window.prompt('Assigner à (email/nom):');
                  if (val) onAssign(a.id, val);
                }}>Assigner</button>
              </td>
              <td className="p-2">
                <button className="px-2 py-1 text-sm border rounded" onClick={() => {
                  const val = window.prompt('Ajouter un commentaire:');
                  if (val) onComment(a.id, val);
                }}>Commenter</button>
              </td>
              <td className="p-2">{new Date(a.createdAt).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}