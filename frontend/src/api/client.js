const BASE = '/api';

export async function fetchStats() {
  const res = await fetch(`${BASE}/stats`);
  if (!res.ok) throw new Error('Failed to fetch stats');
  return res.json();
}

export async function fetchCampaigns() {
  const res = await fetch(`${BASE}/campaigns`);
  if (!res.ok) throw new Error('Failed to fetch campaigns');
  return res.json();
}

export async function createCampaign(payload) {
  const res = await fetch(`${BASE}/campaign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error('Failed to create campaign');
  return res.json();
}

export async function fetchEmployeesByDepartment(department) {
  const res = await fetch(`${BASE}/employees/${encodeURIComponent(department)}`);
  if (!res.ok) throw new Error('Failed to fetch employees from Splunk');
  return res.json();
}
