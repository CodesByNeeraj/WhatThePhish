export default function Navbar({ lastUpdated, onNewCampaign }) {
  const time = lastUpdated
    ? lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : null;

  return (
    <nav className="sticky top-0 z-40 bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-8 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-blue-600 rounded-md flex items-center justify-center text-sm">
            🎣
          </div>
          <span className="font-semibold text-gray-900 tracking-tight">WhatThePhish</span>
        </div>

        <div className="flex items-center gap-5">
          {time && (
            <span className="text-xs text-gray-400">Updated {time}</span>
          )}
          <button
            onClick={onNewCampaign}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-md transition-colors"
          >
            <span className="text-base leading-none">+</span>
            New Campaign
          </button>
        </div>
      </div>
    </nav>
  );
}
