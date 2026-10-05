import React, { useState } from 'react';
import { api } from '../api/client';
import { Bot, Send, Sparkles, ShieldCheck } from 'lucide-react';

interface Props {
  tenantId: string;
}

export const AskGrowthOS: React.FC<Props> = ({ tenantId }) => {
  const [prompt, setPrompt] = useState('');
  const [messages, setMessages] = useState<any[]>([
    { role: 'assistant', text: 'Hello! I am GrowthOS AI Decision Assistant. Ask me anything about revenue drops, inventory stockouts, or customer churn risks for your retail store.' }
  ]);
  const [loading, setLoading] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const userMsg = { role: 'user', text: prompt };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);
    const textToSend = prompt;
    setPrompt('');

    api.askAssistant(tenantId, textToSend).then(data => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        text: data.answer,
        mode: data.mode,
        evidence: data.evidence
      }]);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setMessages(prev => [...prev, { role: 'assistant', text: 'Error connecting to GrowthOS AI backend engine.' }]);
      setLoading(false);
    });
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', height: 520 }}>
      <div style={{ paddingBottom: 12, borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <Bot size={20} color="#2563eb" />
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#0f172a' }}>Ask GrowthOS AI Assistant</h3>
        </div>
        <span className="badge badge-blue" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <ShieldCheck size={12} /> Grounded Tool Execution
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '16px 0', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {messages.map((m, idx) => (
          <div key={idx} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '85%' }}>
            <div style={{
              background: m.role === 'user' ? '#2563eb' : '#f1f5f9',
              color: m.role === 'user' ? '#ffffff' : '#0f172a',
              padding: '10px 14px',
              borderRadius: 8,
              fontSize: '0.9rem',
              whiteSpace: 'pre-line'
            }}>
              {m.text}
            </div>
            {m.mode && (
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
                <Sparkles size={10} color="#2563eb" /> Powered by: {m.mode}
              </div>
            )}
          </div>
        ))}
        {loading && <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Analyzing backend evidence & generating answer...</div>}
      </div>

      <form onSubmit={handleSend} style={{ display: 'flex', gap: 8, paddingTop: 12, borderTop: '1px solid #e2e8f0' }}>
        <input
          type="text"
          placeholder="Ask e.g. Why did revenue drop? or Which items have stockout risk?"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          style={{ flex: 1, padding: '10px 14px', border: '1px solid #cbd5e1', borderRadius: 6, fontSize: '0.9rem' }}
        />
        <button type="submit" style={{ background: '#2563eb', color: '#fff', border: 'none', borderRadius: 6, padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
