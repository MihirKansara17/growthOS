import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { TrendingUp, ShoppingBag, Users, AlertCircle, Award, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#2563eb', '#059669', '#d97706', '#7c3aed', '#dc2626'];

interface Props {
  tenantId: string;
}

export const CommandCenter: React.FC<Props> = ({ tenantId }) => {
  const [kpi, setKpi] = useState<any>(null);
  const [categories, setCategories] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      api.getKPIs(tenantId),
      api.getCategories(tenantId),
      api.getAlerts(tenantId)
    ]).then(([kpiData, catData, alertData]) => {
      setKpi(kpiData);
      setCategories(catData);
      setAlerts(alertData);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [tenantId]);

  if (loading || !kpi) {
    return <div style={{ padding: 40, color: '#475569' }}>Loading Command Center metrics...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Top Banner Alert System */}
      {alerts.length > 0 && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: 8, padding: '12px 16px', display: 'flex', alignItems: 'center', gap: 12 }}>
          <AlertCircle size={20} color="#b91c1c" />
          <div style={{ flex: 1 }}>
            <span style={{ fontWeight: 600, color: '#991b1b' }}>{alerts[0].title}: </span>
            <span style={{ color: '#7f1d1d', fontSize: '0.9rem' }}>{alerts[0].description}</span>
          </div>
          <span className="badge badge-red">{alerts[0].severity} SEVERITY</span>
        </div>
      )}

      {/* Metric Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: '0.85rem', color: '#475569', fontWeight: 500 }}>Health Score</span>
            <Award size={18} color="#2563eb" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#0f172a' }}>{kpi.health_score} <span style={{ fontSize: '0.9rem', color: '#64748b' }}>/ 100</span></div>
          <span className="badge badge-green" style={{ marginTop: 8 }}>Good Standing</span>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: '0.85rem', color: '#475569', fontWeight: 500 }}>30-Day Revenue</span>
            <TrendingUp size={18} color="#059669" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#0f172a' }}>₹{kpi.total_revenue.toLocaleString()}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 6, fontSize: '0.85rem', color: kpi.revenue_growth_pct >= 0 ? '#059669' : '#dc2626' }}>
            {kpi.revenue_growth_pct >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
            <span>{kpi.revenue_growth_pct}% vs last period</span>
          </div>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: '0.85rem', color: '#475569', fontWeight: 500 }}>Transactions</span>
            <ShoppingBag size={18} color="#d97706" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#0f172a' }}>{kpi.total_transactions}</div>
          <span style={{ fontSize: '0.85rem', color: '#64748b', marginTop: 6, display: 'block' }}>30 days total</span>
        </div>

        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <span style={{ fontSize: '0.85rem', color: '#475569', fontWeight: 500 }}>Avg Order Value (AOV)</span>
            <Users size={18} color="#7c3aed" />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#0f172a' }}>₹{kpi.average_order_value}</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginTop: 6, fontSize: '0.85rem', color: kpi.aov_growth_pct >= 0 ? '#059669' : '#dc2626' }}>
            {kpi.aov_growth_pct >= 0 ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
            <span>{kpi.aov_growth_pct}%</span>
          </div>
        </div>
      </div>

      {/* Main Revenue Trend Chart */}
      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: 16 }}>30-Day Revenue Trend</h3>
        <div style={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={kpi.daily_trend}>
              <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} />
              <Tooltip />
              <Area type="monotone" dataKey="revenue" stroke="#2563eb" fill="#eff6ff" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Category Share Distribution */}
      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: 16 }}>Revenue Share by Category</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20, alignItems: 'center' }}>
          <div style={{ height: 200 }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={categories} dataKey="revenue" nameKey="category" cx="50%" cy="50%" outerRadius={70}>
                  {categories.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {categories.map((cat, idx) => (
              <div key={cat.category} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#334155' }}>
                  <span style={{ width: 10, height: 10, borderRadius: '50%', background: COLORS[idx % COLORS.length] }}></span>
                  {cat.category}
                </span>
                <span style={{ fontWeight: 600, color: '#0f172a' }}>₹{cat.revenue.toLocaleString()} ({cat.share_pct}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
