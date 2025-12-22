export function Trends({ ma7, ma30 }: { ma7: number | null; ma30: number | null }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="font-semibold mb-2">Tendances d'engagement</div>
      <div className="space-y-3">
        <Bar label="MA7" value={ma7} color="bg-blue-600" />
        <Bar label="MA30" value={ma30} color="bg-indigo-600" />
      </div>
    </div>
  );
}

function Bar({ label, value, color }: { label: string; value: number | null; color: string }) {
  const v = value == null ? 0 : Math.max(0, Math.min(100, Number(value)));
  return (
    <div>
      <div className="text-sm text-gray-600 mb-1">{label}: {value == null ? '-' : `${v.toFixed(1)}%`}</div>
      <div className="w-full bg-gray-200 rounded h-2">
        <div className={`${color} h-2 rounded`} style={{ width: `${v}%` }} />
      </div>
    </div>
  );
}