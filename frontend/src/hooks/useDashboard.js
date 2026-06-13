import { useState, useEffect, useCallback } from 'react';
import { fetchStats, fetchCampaigns } from '../api/client';

export function useDashboard() {
  const [stats, setStats]             = useState(null);
  const [campaigns, setCampaigns]     = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [statsData, campaignsData] = await Promise.all([
        fetchStats(),
        fetchCampaigns(),
      ]);
      setStats(statsData);
      setCampaigns(campaignsData.campaigns ?? []);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, 30_000);
    return () => clearInterval(id);
  }, [refresh]);

  return { stats, campaigns, lastUpdated, loading, error, refresh };
}
