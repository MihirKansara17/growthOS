import axios from 'axios';

// When deployed on Vercel, it will use the Render URL provided in Vercel environment variables.
// Otherwise, it defaults to your local FastAPI server.
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const api = {
  getTenants: () => axios.get(`${API_BASE}/tenants`).then(res => res.data),
  getKPIs: (tenantId: string, days = 30) => axios.get(`${API_BASE}/kpis?tenant_id=${tenantId}&days=${days}`).then(res => res.data),
  getCategories: (tenantId: string, days = 30) => axios.get(`${API_BASE}/categories?tenant_id=${tenantId}&days=${days}`).then(res => res.data),
  getRootCause: (tenantId: string, days = 30) => axios.get(`${API_BASE}/root-cause?tenant_id=${tenantId}&days=${days}`).then(res => res.data),
  getRFM: (tenantId: string) => axios.get(`${API_BASE}/rfm?tenant_id=${tenantId}`).then(res => res.data),
  getInventory: (tenantId: string, days = 30) => axios.get(`${API_BASE}/inventory?tenant_id=${tenantId}&days=${days}`).then(res => res.data),
  getAlerts: (tenantId: string) => axios.get(`${API_BASE}/alerts?tenant_id=${tenantId}`).then(res => res.data),
  simulate: (data: { tenant_id: string; discount_pct: number; price_change_pct: number; reorder_units: number }) => 
    axios.post(`${API_BASE}/simulate`, data).then(res => res.data),
  askAssistant: (tenantId: string, prompt: string) => 
    axios.post(`${API_BASE}/ask`, { tenant_id: tenantId, prompt }).then(res => res.data),
};
