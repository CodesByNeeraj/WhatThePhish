export default function ClickersTable({ clickers }) {
  if (!clickers?.length) return null;

  return (
    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-100">
        <h2 className="text-sm font-semibold text-gray-800">Employees Who Clicked</h2>
        <p className="text-xs text-gray-400 mt-0.5">{clickers.length} click{clickers.length !== 1 ? 's' : ''} recorded</p>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
            <th className="px-5 py-3 text-left font-medium">Name</th>
            <th className="px-5 py-3 text-left font-medium">Email</th>
            <th className="px-5 py-3 text-left font-medium">Department</th>
            <th className="px-5 py-3 text-left font-medium">Clicked At</th>
            <th className="px-5 py-3 text-left font-medium">Training</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {clickers.map((c, i) => (
            <tr key={i} className="hover:bg-gray-50 transition-colors">
              <td className="px-5 py-3 text-gray-800 font-medium">{c.name || '—'}</td>
              <td className="px-5 py-3 text-gray-600">{c.email}</td>
              <td className="px-5 py-3 text-gray-600">{c.department}</td>
              <td className="px-5 py-3 text-gray-400 text-xs">{new Date(c.clicked_at).toLocaleString('en-SG', { timeZone: 'Asia/Singapore' })}</td>
              <td className="px-5 py-3">
                {c.training_sent
                  ? <span className="text-xs font-medium text-emerald-600">Sent</span>
                  : <span className="text-xs font-medium text-amber-500">Pending</span>
                }
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
