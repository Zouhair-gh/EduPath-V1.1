import type { Student } from '@/types';
import { useStudentAdmin } from '@/hooks/useStudentAdmin';
import { useToast } from '@/components/Notifications/ToastProvider';

export function StudentsTable({ data, loading, error, courseId = 1 }: { data: Student[] | undefined; loading: boolean; error?: string; courseId?: number; }) {
  if (loading) return <div className="animate-pulse text-gray-500">Chargement des étudiants…</div>;
  if (error) return <div className="text-red-600">Erreur: {error}</div>;
  if (!data || data.length === 0) return <div className="text-gray-500">Aucun étudiant disponible</div>;
  const { addNote, addTag } = useStudentAdmin(courseId);
  const { notify } = useToast();
  return (
    <div className="overflow-auto rounded border">
      <table className="min-w-full divide-y">
        <thead className="bg-gray-50">
          <tr>
            <th className="text-left p-2">Nom</th>
            <th className="text-left p-2">Email</th>
            <th className="text-left p-2">Engagement</th>
            <th className="text-left p-2">Succès</th>
            <th className="text-left p-2">Actions</th>
          </tr>
        </thead>
        <tbody className="divide-y">
          {data.map((s) => (
            <tr key={String(s.id)} className="hover:bg-gray-50">
              <td className="p-2">{s.name || `Étudiant ${s.id}`}</td>
              <td className="p-2">{s.email || '-'}</td>
              <td className="p-2">{s.engagement ?? '-'}</td>
              <td className="p-2">{s.successRate ?? '-'}</td>
              <td className="p-2">
                <div className="flex items-center gap-2">
                  <button className="px-2 py-1 text-sm border rounded" onClick={() => {
                    const content = window.prompt('Ajouter une note:');
                    if (!content) return;
                    addNote.mutate({ studentId: s.id!, content }, {
                      onSuccess: () => notify({ type: 'success', message: 'Note ajoutée' }),
                      onError: (e: any) => notify({ type: 'error', message: e?.message || 'Échec ajout note' }),
                    });
                  }}>Note</button>
                  <button className="px-2 py-1 text-sm border rounded" onClick={() => {
                    const tag = window.prompt('Ajouter un tag:');
                    if (!tag) return;
                    addTag.mutate({ studentId: s.id!, tag }, {
                      onSuccess: () => notify({ type: 'success', message: 'Tag ajouté' }),
                      onError: (e: any) => notify({ type: 'error', message: e?.message || 'Échec ajout tag' }),
                    });
                  }}>Tag</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}