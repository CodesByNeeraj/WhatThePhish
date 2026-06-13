import { useState } from 'react';
import { useDashboard } from './hooks/useDashboard';
import Navbar from './components/Navbar';
import StatCard from './components/StatCard';
import DeptChart from './components/DeptChart';
import DeptTable from './components/DeptTable';
import CampaignsTable from './components/CampaignsTable';
import ClickersTable from './components/ClickersTable';
import NewCampaignModal from './components/NewCampaignModal';
import Toast from './components/Toast';

export default function App() {
  const { stats, campaigns, lastUpdated, refresh } = useDashboard();
  const [modalOpen, setModalOpen] = useState(false);
  const [toast, setToast]         = useState({ visible: false, message: '' });

  function showToast(message) {
    setToast({ visible: true, message });
    setTimeout(() => setToast(t => ({ ...t, visible: false })), 3500);
  }

  function handleLaunched(campaignId) {
    setModalOpen(false);
    showToast(`Campaign ${campaignId} is launching.`);
    setTimeout(refresh, 4000);
  }

  const rate = stats?.click_rate_percent ?? 0;
  const rateClass = rate >= 20 ? 'text-red-600' : rate >= 10 ? 'text-amber-600' : 'text-emerald-600';

  return (
    <div className="min-h-screen bg-white">
      <Navbar lastUpdated={lastUpdated} onNewCampaign={() => setModalOpen(true)} />

      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="mb-7">
          <h1 className="text-xl font-bold text-gray-900 tracking-tight">Campaign Dashboard</h1>
          <p className="text-sm text-gray-400 mt-1">
            Phishing simulation overview and employee training metrics
          </p>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <StatCard
            label="Campaigns"
            value={stats?.total_campaigns}
            sub="Total launched"
          />
          <StatCard
            label="Emails Sent"
            value={stats?.total_emails_sent}
            sub="Across all campaigns"
          />
          <StatCard
            label="Click Rate"
            value={stats ? `${stats.click_rate_percent}%` : null}
            sub={stats ? `${stats.total_clicks} of ${stats.total_emails_sent} clicked` : 'Employees who clicked'}
            valueClassName={rateClass}
          />
          <StatCard
            label="Remediations"
            value={stats?.total_remediations_sent}
            sub="Training emails sent"
            valueClassName="text-emerald-600"
          />
        </div>

        {/* Chart + department table */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <DeptChart byDept={stats?.by_department} />
          <DeptTable byDept={stats?.by_department} />
        </div>

        {/* Clickers table */}
        <div className="mb-6">
          <ClickersTable clickers={stats?.clickers} />
        </div>

        {/* Campaigns table */}
        <CampaignsTable campaigns={campaigns} />
      </main>

      <NewCampaignModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onLaunched={handleLaunched}
      />

      <Toast message={toast.message} visible={toast.visible} />
    </div>
  );
}
