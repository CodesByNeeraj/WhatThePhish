import Badge from './Badge';
import EmptyState from './EmptyState';

const TECHNIQUES = {
  credential_harvesting:   'Credential Harvesting',
  invoice_fraud:           'Invoice Fraud',
  it_helpdesk:             'IT Helpdesk',
  executive_impersonation: 'Executive Impersonation',
  delivery_notification:   'Delivery Notification',
};

export default function CampaignsTable({ campaigns }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">All Campaigns</h3>
      </div>

      {campaigns.length === 0 ? (
        <EmptyState icon="🗂️" message="No campaigns launched yet" />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-100">
                {['Campaign ID', 'Department', 'Technique', 'Urgency', 'Recipients'].map(h => (
                  <th
                    key={h}
                    className="px-6 py-3 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider whitespace-nowrap"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {campaigns.map(c => (
                <tr key={c.campaign_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-3 font-mono text-xs text-gray-400">{c.campaign_id}</td>
                  <td className="px-6 py-3 text-sm text-gray-700">{c.department}</td>
                  <td className="px-6 py-3 text-sm text-gray-700">
                    {TECHNIQUES[c.technique] ?? c.technique}
                  </td>
                  <td className="px-6 py-3"><Badge value={c.urgency} /></td>
                  <td className="px-6 py-3 text-sm text-gray-500">{c.recipients_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
