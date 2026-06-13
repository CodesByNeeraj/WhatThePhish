export default function StatCard({ label, value, sub, valueClassName = 'text-gray-900' }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 px-6 py-5">
      <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">
        {label}
      </p>
      <p className={`text-4xl font-bold tracking-tight leading-none mb-1.5 ${valueClassName}`}>
        {value ?? '—'}
      </p>
      <p className="text-xs text-gray-400">{sub}</p>
    </div>
  );
}
