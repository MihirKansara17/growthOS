import React, { useEffect, useState } from 'react';
import { api } from './api/client';
import { CommandCenter } from './components/CommandCenter';
import { RootCauseInvestigation } from './components/RootCauseInvestigation';
import { InventoryIntelligence } from './components/InventoryIntelligence';
import { DecisionSimulator } from './components/DecisionSimulator';
import { AskGrowthOS } from './components/AskGrowthOS';
import { LayoutDashboard, Search, Package, Sliders, MessageSquare, Building2, Store } from 'lucide-react';

export function App() {
  const [tenants, setTenants] = useState<any[]>([]);
  const [selectedTenant, setSelectedTenant] = useState('tenant_apex');
  const [activeTab, setActiveTab] = useState<'command' | 'rca' | 'inventory' | 'simulator' | 'ai'>('command');

  useEffect(() => {
    api.getTenants().then(data => setTenants(data)).catch(console.error);
  }, []);

  const currentTenantObj = tenants.find(t => t.id === selectedTenant);

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc', color: '#0f172a' }}>
      {/* Top Professional Header */}
      <header style={{ background: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '12px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ background: '#2563eb', color: '#ffffff', padding: '6px 12px', borderRadius: 6, fontWeight: 700, fontSize: '1.1rem', letterSpacing: '0.5px' }}>
            GrowthOS V2
          </div>
          <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 500 }}>AI Decision Intelligence for Indian Retail</span>
        </div>

        {/* Tenant Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: '#f1f5f9', padding: '4px 12px', borderRadius: 6, border: '1px solid #cbd5e1' }}>
          <Building2 size={16} color="#475569" />
          <span style={{ fontSize: '0.85rem', fontWeight: 500, color: '#475569' }}>Demo Profile:</span>
          <select
            value={selectedTenant}
            onChange={e => setSelectedTenant(e.target.value)}
            style={{ background: 'transparent', border: 'none', fontWeight: 600, color: '#0f172a', cursor: 'pointer', outline: 'none' }}
          >
            {tenants.map(t => (
              <option key={t.id} value={t.id}>
                {t.name} ({t.maturity_level})
              </option>
            ))}
          </select>
        </div>
      </header>

      {/* Sub-header Profile Description */}
      {currentTenantObj && (
        <div style={{ background: '#eff6ff', borderBottom: '1px solid #dbeafe', padding: '8px 24px', fontSize: '0.82rem', color: '#1e40af', display: 'flex', alignItems: 'center', gap: 8 }}>
          <Store size={14} />
          <span><strong>Profile Intelligence:</strong> {currentTenantObj.description}</span>
        </div>
      )}

      {/* Main Container */}
      <div style={{ display: 'flex', maxWidth: 1400, margin: '20px auto', padding: '0 24px', gap: 24 }}>
        {/* Sidebar Navigation */}
        <nav style={{ width: 220, display: 'flex', flexDirection: 'column', gap: 4 }}>
          <button
            onClick={() => setActiveTab('command')}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 6, border: 'none',
              background: activeTab === 'command' ? '#2563eb' : 'transparent',
              color: activeTab === 'command' ? '#ffffff' : '#475569',
              fontWeight: 500, textAlign: 'left'
            }}
          >
            <LayoutDashboard size={18} /> Executive Dashboard
          </button>

          <button
            onClick={() => setActiveTab('rca')}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 6, border: 'none',
              background: activeTab === 'rca' ? '#2563eb' : 'transparent',
              color: activeTab === 'rca' ? '#ffffff' : '#475569',
              fontWeight: 500, textAlign: 'left'
            }}
          >
            <Search size={18} /> Root-Cause Analysis
          </button>

          <button
            onClick={() => setActiveTab('inventory')}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 6, border: 'none',
              background: activeTab === 'inventory' ? '#2563eb' : 'transparent',
              color: activeTab === 'inventory' ? '#ffffff' : '#475569',
              fontWeight: 500, textAlign: 'left'
            }}
          >
            <Package size={18} /> Inventory Intelligence
          </button>

          <button
            onClick={() => setActiveTab('simulator')}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 6, border: 'none',
              background: activeTab === 'simulator' ? '#2563eb' : 'transparent',
              color: activeTab === 'simulator' ? '#ffffff' : '#475569',
              fontWeight: 500, textAlign: 'left'
            }}
          >
            <Sliders size={18} /> Decision Simulator
          </button>

          <button
            onClick={() => setActiveTab('ai')}
            style={{
              display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 6, border: 'none',
              background: activeTab === 'ai' ? '#2563eb' : 'transparent',
              color: activeTab === 'ai' ? '#ffffff' : '#475569',
              fontWeight: 500, textAlign: 'left'
            }}
          >
            <MessageSquare size={18} /> Ask GrowthOS AI
          </button>
        </nav>

        {/* Dynamic Content View */}
        <main style={{ flex: 1 }}>
          {activeTab === 'command' && <CommandCenter tenantId={selectedTenant} />}
          {activeTab === 'rca' && <RootCauseInvestigation tenantId={selectedTenant} />}
          {activeTab === 'inventory' && <InventoryIntelligence tenantId={selectedTenant} />}
          {activeTab === 'simulator' && <DecisionSimulator tenantId={selectedTenant} />}
          {activeTab === 'ai' && <AskGrowthOS tenantId={selectedTenant} />}
        </main>
      </div>
    </div>
  );
}

export default App;
