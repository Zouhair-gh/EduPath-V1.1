export function StatsCards({ students, avgEng, avgSuc }: { students: number; avgEng: number; avgSuc: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Stat title="Étudiants" value={students} />
      <Stat title="Engagement moyen" value={`${Number(avgEng).toFixed(2)}%`} />
      <Stat title="Taux de réussite" value={`${Number(avgSuc).toFixed(2)}%`} />
    </div>
  );
}

function Stat({ title, value }: { title: string; value: number | string }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="text-sm text-gray-500">{title}</div>
      <div className="text-2xl font-semibold">{value}</div>
    </div>
  );
}