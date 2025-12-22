export function TopStudents({ items }: { items: Array<{ id: number | string; name?: string; engagement?: number; successRate?: number; riskScore: number }> }) {
  return (
    <div className="bg-white shadow rounded p-4">
      <div className="font-semibold mb-2">Top étudiants à surveiller</div>
      {(!items || items.length === 0) && <div className="text-gray-500">Aucun étudiant à risque</div>}
      {items && items.length > 0 && (
        <div className="overflow-auto">
          <table className="min-w-full divide-y">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left p-2">Étudiant</th>
                <th className="text-left p-2">Engagement</th>
                <th className="text-left p-2">Succès</th>
                <th className="text-left p-2">Score risque</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {items.map((s) => (
                <tr key={String(s.id)}>
                  <td className="p-2">{s.name || `#${s.id}`}</td>
                  <td className="p-2">{s.engagement ?? '-'}</td>
                  <td className="p-2">{s.successRate ?? '-'}</td>
                  <td className="p-2 font-semibold">{s.riskScore}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}