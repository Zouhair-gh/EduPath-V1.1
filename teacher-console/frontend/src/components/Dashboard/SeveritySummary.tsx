export function SeveritySummary({ counts }: { counts: { active: number; high: number; medium: number; low: number } }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="flex items-center justify-between mb-2">
        <div className="font-semibold">Alertes actives</div>
        <span className="text-sm text-gray-500">{counts.active} total</span>
      </div>
      <div className="flex gap-2">
        <Badge color="bg-red-600" label="High" value={counts.high} />
        <Badge color="bg-amber-600" label="Medium" value={counts.medium} />
        <Badge color="bg-green-600" label="Low" value={counts.low} />
      </div>
    </div>
  );
}

function Badge({ color, label, value }: { color: string; label: string; value: number }) {
  return (
    <div className={`text-white ${color} px-3 py-2 rounded flex items-center gap-2`}>
      <span className="text-sm">{label}</span>
      <span className="font-semibold">{value}</span>
    </div>
  );
}