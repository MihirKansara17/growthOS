import React, { useState } from 'react';
import { api } from '../api/client';
import { Sliders, Calculator, CheckCircle2, AlertTriangle } from 'lucide-react';

interface Props {
  tenantId: string;
}

export const DecisionSimulator: React.FC<Props> = ({ tenantId }) => {
  const [discount, setDiscount] = useState(10);
  const [priceChange, setPriceChange] = useState(0);
  const [reorderUnits, setReorderUnits] = useState(100);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const runSim = () => {
    setLoading(true);
    api.simulate({
      tenant_id: tenantId,
      discount_pct: discount,
      price_change_pct: priceChange,
      reorder_units: reorderUnits
    }).then(data => {
      setResult(data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Sliders size={18} color="#2563eb" /> Interactive What-If Scenario Controls
        </h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 20 }}>
          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: 500, color: '#475569', display: 'block', marginBottom: 6 }}>
              Promotional Discount: <strong>{discount}%</strong>
            </label>
            <input type="range" min="0" max="40" value={discount} onChange={e => setDiscount(Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: 500, color: '#475569', display: 'block', marginBottom: 6 }}>
              Base Price Change: <strong>{priceChange}%</strong>
            </label>
            <input type="range" min="-20" max="30" value={priceChange} onChange={e => setPriceChange(Number(e.target.value))} style={{ width: '100%' }} />
          </div>
          <div>
            <label style={{ fontSize: '0.85rem', fontWeight: 500, color: '#475569', display: 'block', marginBottom: 6 }}>
              Reorder Units: <strong>{reorderUnits}</strong>
            </label>
            <input type="number" value={reorderUnits} onChange={e => setReorderUnits(Number(e.target.value))} style={{ width: '100%', padding: '6px 10px', border: '1px solid #cbd5e1', borderRadius: 6 }} />
          </div>
        </div>
        <button onClick={runSim} style={{ marginTop: 20, background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '10px 20px', fontWeight: 600, fontSize: '0.9rem', display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <Calculator size={16} /> {loading ? "Running P&L Simulation..." : "Simulate Scenario Impact"}
        </button>
      </div>

      {result && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div className="card" style={{ background: result.margin_impact_amount >= 0 ? '#ecfdf5' : '#fffbeb', border: `1px solid ${result.margin_impact_amount >= 0 ? '#a7f3d0' : '#fde68a'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontWeight: 600, color: result.margin_impact_amount >= 0 ? '#047857' : '#b45309' }}>
              {result.margin_impact_amount >= 0 ? <CheckCircle2 size={20} /> : <AlertTriangle size={20} />}
              <span>{result.recommendation}</span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div className="card">
              <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Projected 30-Day Revenue</span>
              <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#0f172a' }}>₹{result.projected_30d_revenue.toLocaleString()}</div>
              <div style={{ fontSize: '0.85rem', color: result.revenue_impact_amount >= 0 ? '#059669' : '#dc2626', marginTop: 4 }}>
                {result.revenue_impact_amount >= 0 ? '+' : ''}₹{result.revenue_impact_amount.toLocaleString()} ({result.revenue_impact_pct}%)
              </div>
            </div>
            <div className="card">
              <span style={{ fontSize: '0.85rem', color: '#64748b' }}>Projected Gross Margin</span>
              <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#0f172a' }}>₹{result.projected_gross_margin.toLocaleString()}</div>
              <div style={{ fontSize: '0.85rem', color: result.margin_impact_amount >= 0 ? '#059669' : '#dc2626', marginTop: 4 }}>
                {result.margin_impact_amount >= 0 ? '+' : ''}₹{result.margin_impact_amount.toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
