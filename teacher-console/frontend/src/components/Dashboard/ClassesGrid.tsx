import { useClassesOverview } from '@/hooks/useClassesOverview';

export function ClassesGrid({ onSelect }: { onSelect: (courseId: number) => void }) {
  const { data, isLoading } = useClassesOverview();
  if (isLoading) return <div className="bg-white p-4 rounded shadow">Chargement des classes…</div>;
  if (!data || data.length === 0) return null;
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {data.map(c => (
        <button key={c.courseId} className="bg-white p-4 rounded shadow text-left hover:ring-2 hover:ring-blue-400"
          onClick={() => onSelect(c.courseId)}>
          <div className="text-sm text-gray-500">Cours {c.courseId}</div>
          <div className="mt-2 flex items-center justify-between">
            <div>
              <div className="text-xl font-semibold">{c.totalStudents} étudiants</div>
              <div className="text-xs text-gray-600">Alerts: {c.atRiskCount}</div>
            </div>
            <div className="text-right text-xs text-gray-600">
              <div>Eng: {Number(c.averageEngagement || 0).toFixed(1)}%</div>
              <div>Suc: {Number(c.averageSuccessRate || 0).toFixed(1)}%</div>
            </div>
          </div>
        </button>
      ))}
    </div>
  );
}