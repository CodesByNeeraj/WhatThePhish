const STYLES = {
  high:   'bg-red-50 text-red-700 ring-1 ring-inset ring-red-600/20',
  medium: 'bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-600/20',
  low:    'bg-green-50 text-green-700 ring-1 ring-inset ring-green-600/20',
};

export default function Badge({ value }) {
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold uppercase tracking-wide ${STYLES[value] ?? STYLES.medium}`}>
      {value}
    </span>
  );
}
