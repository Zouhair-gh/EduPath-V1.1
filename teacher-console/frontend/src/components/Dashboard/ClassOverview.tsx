import { useClassData } from '@/hooks/useClassData';

export function ClassOverview({ courseId }: { courseId: number }) {
  const { data, isLoading } = useClassData(courseId);
  if (isLoading || !data) return <div className="p-4">Loading...</div>;
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <StatCard title="Étudiants" value={data.totalStudents} />
      <StatCard title="Engagement moyen" value={`${data.averageEngagement}%`} />
      <StatCard title="Taux de réussite" value={`${data.averageSuccessRate}%`} />
      <StatCard title="À risque" value={data.atRiskCount} />
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number | string }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}
