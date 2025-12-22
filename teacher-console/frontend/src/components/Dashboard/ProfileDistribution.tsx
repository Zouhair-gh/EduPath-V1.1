export function ProfileDistribution({ items }: { items: { label: string; count: number; percentage: number }[] }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="font-semibold mb-2">Profils</div>
      {(!items || items.length === 0) && <div className="text-gray-500">Aucune donnée</div>}
      <div className="space-y-2">
        {items?.map((p, idx) => (
          <div key={`${p.label}-${idx}`}>
            <div className="flex justify-between text-sm text-gray-600">
              <span>{p.label}</span>
              <span>{p.percentage}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded h-2">
              <div className="bg-teal-600 h-2 rounded" style={{ width: `${Math.min(100, Math.max(0, p.percentage))}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}