import React, { useEffect, useState } from 'react';
import { api } from '../api/client';
import { Package, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

interface Props {
  tenantId: string;
}

export const InventoryIntelligence: React.FC<Props> = ({ tenantId }) => {
  const [inv, setInv] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api.getInventory(tenantId).then(data => {
      setInv(data);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [tenantId]);

  if (loading || !inv) return <div style={{ padding: 40, color: '#475569' }}>Calculating Days of Cover & Inventory Health...</div>;

  if (inv.status === "NO_INVENTORY_DATA") {
    return (
      <div className="card" style={{ padding: 30, textAlign: 'center' }}>
        <AlertTriangle size={32} color="#d97706" style={{ margin: '0 auto 12px' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#0f172a' }}>Limited Inventory Depth</h3>
        <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: 6 }}>{inv.message}</p>
        <div className="badge badge-yellow" style={{ marginTop: 16 }}>Data Quality Recommendation: Add SKU Stock Counts</div>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Inventory KPI Summary */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        <div className="card">
          <span style={{ fontSize: '0.85rem', color: '#475569' }}>Tracked SKUs</span>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#0f172a' }}>{inv.total_items_tracked}</div>
        </div>
        <div className="card" style={{ borderColor: '#fecaca' }}>
          <span style={{ fontSize: '0.85rem', color: '#dc2626', fontWeight: 600 }}>Critical Stockout Risk (&lt; 7 Days)</span>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#dc2626' }}>{inv.stockout_risk_items_count} items</div>
        </div>
        <div className="card">
          <span style={{ fontSize: '0.85rem', color: '#d97706' }}>Overstocked (&gt; 60 Days)</span>
          <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#d97706' }}>{inv.overstock_items_count} items</div>
        </div>
      </div>

      {/* Inventory Items Table */}
      <div className="card">
        <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Package size={18} color="#2563eb" /> Days of Cover & Reorder Point Analysis
        </h3>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: '10px 8px' }}>Product</th>
              <th style={{ padding: '10px 8px' }}>Category</th>
              <th style={{ padding: '10px 8px' }}>Stock on Hand</th>
              <th style={{ padding: '10px 8px' }}>Daily Velocity</th>
              <th style={{ padding: '10px 8px' }}>Days of Cover</th>
              <th style={{ padding: '10px 8px' }}>Status</th>
              <th style={{ padding: '10px 8px' }}>Rec. Reorder Qty</th>
            </tr>
          </thead>
          <tbody>
            {inv.items.map((item: any) => (
              <tr key={`${item.product_id}-${item.store_name}`} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: 8, fontWeight: 500, color: '#0f172a' }}>{item.product_name}</td>
                <td style={{ padding: 8, color: '#475569' }}>{item.category}</td>
                <td style={{ padding: 8, fontWeight: 600 }}>{item.stock_on_hand}</td>
                <td style={{ padding: 8 }}>{item.daily_velocity} / day</td>
                <td style={{ padding: 8, fontWeight: 600, color: item.days_of_cover < 7 ? '#dc2626' : '#059669' }}>
                  {item.days_of_cover} days
                </td>
                <td style={{ padding: 8 }}>
                  {item.status === 'STOCKOUT_RISK' ? (
                    <span className="badge badge-red">Stockout Risk</span>
                  ) : item.status === 'OVERSTOCK' ? (
                    <span className="badge badge-yellow">Overstock</span>
                  ) : (
                    <span className="badge badge-green">Healthy</span>
                  )}
                </td>
                <td style={{ padding: 8, fontWeight: 600, color: item.recommended_reorder_qty > 0 ? '#2563eb' : '#94a3b8' }}>
                  {item.recommended_reorder_qty > 0 ? `+${item.recommended_reorder_qty} units` : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
