import {
  BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts';
import EmptyState from './EmptyState';

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-white border border-gray-200 rounded-md shadow-sm px-3 py-2">
      <p className="text-xs font-semibold text-gray-700 mb-0.5">{label}</p>
      <p className="text-xs text-gray-500">{payload[0].value}% click rate</p>
    </div>
  );
}

function barColor(rate) {
  if (rate >= 20) return '#ef4444';
  if (rate >= 10) return '#f59e0b';
  return '#3b82f6';
}

export default function DeptChart({ byDept = {} }) {
  const data = Object.entries(byDept).map(([dept, d]) => ({
    dept,
    rate: d.sent > 0 ? +(d.clicks / d.sent * 100).toFixed(1) : 0,
  }));

  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">Click Rate by Department</h3>
      </div>
      <div className="p-6">
        {data.length === 0 ? (
          <EmptyState icon="📊" message="No campaign data yet" />
        ) : (
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data} barSize={36} margin={{ top: 4, right: 4, left: -16, bottom: 0 }}>
              <XAxis
                dataKey="dept"
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#9ca3af' }}
              />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#9ca3af' }}
                tickFormatter={v => `${v}%`}
                domain={[0, 100]}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.04)' }} />
              <Bar dataKey="rate" radius={[4, 4, 0, 0]}>
                {data.map((entry, i) => (
                  <Cell key={i} fill={barColor(entry.rate)} fillOpacity={0.85} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
