import EmptyState from './EmptyState';

function rateClass(rate) {
  if (rate >= 20) return 'text-red-600 font-semibold';
  if (rate >= 10) return 'text-amber-600 font-semibold';
  return 'text-emerald-600 font-semibold';
}

export default function DeptTable({ byDept = {} }) {
  const rows = Object.entries(byDept).sort((a, b) => {
    const ra = a[1].sent > 0 ? a[1].clicks / a[1].sent : 0;
    const rb = b[1].sent > 0 ? b[1].clicks / b[1].sent : 0;
    return rb - ra;
  });

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">Department Breakdown</h3>
      </div>

      {rows.length === 0 ? (
        <EmptyState icon="📋" message="No data yet" />
      ) : (
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100">
              {['Department', 'Sent', 'Clicks', 'Rate'].map(h => (
                <th
                  key={h}
                  className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-50">
            {rows.map(([dept, d]) => {
              const rate = d.sent > 0 ? +(d.clicks / d.sent * 100).toFixed(1) : 0;
              return (
                <tr key={dept} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-3 text-sm text-gray-700">{dept}</td>
                  <td className="px-6 py-3 text-sm text-gray-500">{d.sent}</td>
                  <td className="px-6 py-3 text-sm text-gray-500">{d.clicks}</td>
                  <td className={`px-6 py-3 text-sm ${rateClass(rate)}`}>{rate}%</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </div>
  );
}
