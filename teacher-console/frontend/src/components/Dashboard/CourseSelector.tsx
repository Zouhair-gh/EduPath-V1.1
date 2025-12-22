import { useClassesOverview } from '@/hooks/useClassesOverview';

export function CourseSelector({ value, onChange }: { value?: number; onChange: (v: number) => void }) {
  const { data, isLoading } = useClassesOverview();
  if (isLoading) return <div className="text-sm text-gray-500">Chargement des cours…</div>;
  const options = (data || []).map(c => ({ id: c.courseId, label: `Cours ${c.courseId} (${c.totalStudents} étudiants)` }));
  if (!options.length) return null;
  return (
    <div className="flex items-center gap-2">
      <label className="text-sm text-gray-600">Cours:</label>
      <select
        className="border rounded px-2 py-1"
        value={value ?? options[0].id}
        onChange={(e) => onChange(Number(e.target.value))}
      >
        {options.map(o => (
          <option key={o.id} value={o.id}>{o.label}</option>
        ))}
      </select>
    </div>
  );
}