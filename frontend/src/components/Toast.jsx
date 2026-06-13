export default function Toast({ message, visible }) {
  return (
    <div
      className={`fixed bottom-6 right-6 z-50 flex items-center gap-2.5 bg-gray-900 text-white text-sm px-4 py-3 rounded-lg shadow-lg transition-all duration-300 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
      }`}
    >
      <span className="text-emerald-400">✓</span>
      {message}
    </div>
  );
}
