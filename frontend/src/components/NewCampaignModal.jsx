import { useState } from 'react';
import { createCampaign, fetchEmployeesByDepartment } from '../api/client';

const DEPARTMENTS = ['Finance', 'HR', 'Engineering', 'Sales', 'Operations', 'Executive', 'Marketing', 'Legal', 'IT','Security'];

const TECHNIQUES = [
  { value: 'credential_harvesting',   label: 'Credential Harvesting' },
  { value: 'invoice_fraud',           label: 'Invoice Fraud' },
  { value: 'it_helpdesk',             label: 'IT Helpdesk Impersonation' },
  { value: 'executive_impersonation', label: 'Executive Impersonation' },
  { value: 'delivery_notification',   label: 'Delivery Notification' },
];

const INPUT_CLS = 'w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500';

function Field({ label, hint, children }) {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>
      {children}
      {hint && <p className="mt-1.5 text-xs text-gray-400">{hint}</p>}
    </div>
  );
}

function parseRecipients(raw) {
  return raw
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
    .map(line => {
      const [email, ...rest] = line.split(',');
      return { email: email.trim(), name: rest.join(',').trim() };
    });
}

export default function NewCampaignModal({ open, onClose, onLaunched }) {
  const [dept,         setDept]         = useState('Finance');
  const [urgency,      setUrgency]      = useState('medium');
  const [technique,    setTechnique]    = useState('credential_harvesting');
  const [recipients,   setRecipients]   = useState('');
  const [loading,      setLoading]      = useState(false);
  const [importing,    setImporting]    = useState(false);
  const [importStatus, setImportStatus] = useState('');
  const [error,        setError]        = useState('');

  if (!open) return null;

  async function handleImportFromSplunk() {
    setImporting(true);
    setImportStatus('');
    setError('');
    try {
      const data = await fetchEmployeesByDepartment(dept);
      if (!data.employees.length) {
        setImportStatus(`No employees found in Splunk for "${dept}".`);
        return;
      }
      const lines = data.employees.map(e => e.name ? `${e.email}, ${e.name}` : e.email);
      setRecipients(lines.join('\n'));
      setImportStatus(`Imported ${data.count} employee${data.count !== 1 ? 's' : ''} from Splunk.`);
    } catch {
      setError('Could not reach Splunk. Check MCP connection.');
    } finally {
      setImporting(false);
    }
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    const parsed = parseRecipients(recipients);
    if (!parsed.length) {
      setError('Add at least one recipient.');
      return;
    }

    setLoading(true);
    try {
      const data = await createCampaign({ department: dept, urgency, technique, recipients: parsed });
      setRecipients('');
      setImportStatus('');
      onLaunched(data.campaign_id);
    } catch {
      setError('Failed to launch campaign. Is the server running?');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={e => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md mx-4">

        <div className="flex items-start justify-between px-6 py-5 border-b border-gray-100">
          <div>
            <h2 className="text-base font-semibold text-gray-900">Launch Campaign</h2>
            <p className="text-xs text-gray-400 mt-0.5">Configure and send a phishing simulation</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors text-xl leading-none mt-0.5">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="px-6 py-5">

            <Field label="Target Department">
              <select value={dept} onChange={e => { setDept(e.target.value); setImportStatus(''); }} className={INPUT_CLS}>
                {DEPARTMENTS.map(d => <option key={d}>{d}</option>)}
              </select>
            </Field>

            <Field label="Urgency Level">
              <select value={urgency} onChange={e => setUrgency(e.target.value)} className={INPUT_CLS}>
                <option value="high">High — immediate action required</option>
                <option value="medium">Medium — action needed soon</option>
                <option value="low">Low — routine notification</option>
              </select>
            </Field>

            <Field label="Phishing Technique">
              <select value={technique} onChange={e => setTechnique(e.target.value)} className={INPUT_CLS}>
                {TECHNIQUES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </Field>

            {/* Recipients field with Splunk import */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-1.5">
                <label className="block text-sm font-medium text-gray-700">Recipients</label>
                <button
                  type="button"
                  onClick={handleImportFromSplunk}
                  disabled={importing}
                  className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {importing ? (
                    <>
                      <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                      </svg>
                      Querying Splunk…
                    </>
                  ) : (
                    <>
                      <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Import from Splunk
                    </>
                  )}
                </button>
              </div>

              <textarea
                value={recipients}
                onChange={e => setRecipients(e.target.value)}
                rows={4}
                className={`${INPUT_CLS} resize-none font-mono text-xs`}
                placeholder={'jane@company.com, Jane Smith\njohn@company.com'}
              />

              {importStatus && (
                <p className="mt-1.5 text-xs text-emerald-600">{importStatus}</p>
              )}
              {!importStatus && (
                <p className="mt-1.5 text-xs text-gray-400">
                  One per line: email or email, Full Name — or import directly from Splunk above
                </p>
              )}
            </div>

            {error && <p className="text-xs text-red-600">{error}</p>}

          </div>

          <div className="flex justify-end gap-3 px-6 py-4 border-t border-gray-100 bg-gray-50 rounded-b-xl">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Launching…' : 'Launch Campaign'}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
