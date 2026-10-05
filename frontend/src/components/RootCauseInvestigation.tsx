import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { HelpCircle, Store, Layers, Activity } from 'lucide-react';

interface Props {
  tenantId: string;
}

export const RootCauseInvestigation: React.FC<Props> = ({ tenantId }) => {
  const [rca, setRca] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getRootCause(tenantId).then(data => {
      setRca(data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [tenantId]);

  if (loading || !rca) return <div style={{ padding: 40, color: '#475569' }}>Running Root-Cause Decomposition...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Primary Diagnosis Box */}
      <div className="card" style={{ background: '#f8fafc', borderLeft: '4px solid #2563eb' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
          <Activity size={20} color="#2563eb" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a' }}>Automated Diagnostic Summary</h3>
        </div>
        <p style={{ color: '#334155', fontSize: '0.95rem' }}>{rca.primary_diagnosis}</p>
        <div style={{ display: 'flex', gap: 16, marginTop: 12, fontSize: '0.85rem' }}>
          <span style={{ color: '#64748b' }}>Evidence ID: <strong>{rca.evidence_id}</strong></span>
          <span style={{ color: '#64748b' }}>Variance: <strong style={{ color: rca.total_variance >= 0 ? '#059669' : '#dc2626' }}>₹{rca.total_variance.toLocaleString()} ({rca.variance_pct}%)</strong></span>
        </div>
      </div>

      {/* Decomposition Tree Split */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        {/* Volume vs Price Driver */}
        <div className="card">
          <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12 }}>1. Volume vs. Price/Mix Decomposition</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ background: '#f1f5f9', padding: 12, borderRadius: 6 }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Volume Effect</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: rca.volume_effect >= 0 ? '#059669' : '#dc2626' }}>
                ₹{rca.volume_effect.toLocaleString()}
              </div>
            </div>
            <div style={{ background: '#f1f5f9', padding: 12, borderRadius: 6 }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b' }}>Price & Product Mix Effect</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 700, color: rca.price_mix_effect >= 0 ? '#059669' : '#dc2626' }}>
                ₹{rca.price_mix_effect.toLocaleString()}
              </div>
            </div>
          </div>
        </div>

        {/* Store Level Drivers */}
        <div className="card">
          <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
            <Store size={16} /> 2. Store Level Variance Drivers
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {rca.store_drivers.map((s: any) => (
              <div key={s.store_id} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #f1f5f9', fontSize: '0.85rem' }}>
                <span style={{ color: '#0f172a', fontWeight: 500 }}>{s.store_name}</span>
                <span style={{ fontWeight: 600, color: s.impact_amount >= 0 ? '#059669' : '#dc2626' }}>
                  ₹{s.impact_amount.toLocaleString()} ({s.growth_pct}%)
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Category Drivers Table */}
      <div className="card">
        <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#475569', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Layers size={16} /> 3. Category Level Variance Breakdown
        </h4>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: 8 }}>Category</th>
              <th style={{ padding: 8 }}>Variance Impact (₹)</th>
              <th style={{ padding: 8 }}>Growth %</th>
            </tr>
          </thead>
          <tbody>
            {rca.category_drivers.map((c: any) => (
              <tr key={c.category} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: 8, fontWeight: 500, color: '#0f172a' }}>{c.category}</td>
                <td style={{ padding: 8, fontWeight: 600, color: c.impact_amount >= 0 ? '#059669' : '#dc2626' }}>
                  ₹{c.impact_amount.toLocaleString()}
                </td>
                <td style={{ padding: 8, color: c.growth_pct >= 0 ? '#059669' : '#dc2626' }}>{c.growth_pct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
