export default function EmptyState({ icon, message }) {
  return (
    <div className="py-12 text-center">
      <div className="text-3xl mb-2 opacity-30">{icon}</div>
      <p className="text-sm text-gray-400">{message}</p>
    </div>
  );
}
