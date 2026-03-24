import React, { useState, useEffect, useRef, useCallback } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import {
  LayoutDashboard, Search, History, Settings, Shield,
  TrendingUp, Target, AlertTriangle, Loader2, CheckCircle,
  FileText, Mic2, Package, Lock, Activity, Cpu, Users,
  DollarSign, BarChart2, ExternalLink, Globe, ChevronRight,
  Eye, User, Languages, Download, Save, Bell, Trash2, XCircle,
  Copy, RefreshCw, Clock
} from 'lucide-react';

// ─── Utilities ─────────────────────────────────────────────────────────────
const SECTION_META = [
  { tag: 'SECTION_1', label: 'Business Strategy', icon: TrendingUp, color: 'emerald' },
  { tag: 'SECTION_2', label: 'Tech Environment', icon: Cpu, color: 'blue' },
  { tag: 'SECTION_3', label: 'Pain Points', icon: AlertTriangle, color: 'orange' },
  { tag: 'SECTION_4', label: 'Decision Makers', icon: Users, color: 'purple' },
  { tag: 'SECTION_5', label: 'Financial Signals', icon: DollarSign, color: 'yellow' },
  { tag: 'SECTION_6', label: 'Competitive Context', icon: BarChart2, color: 'rose' },
];
const ICON_COLOR = {
  emerald: 'text-korhex-green', blue: 'text-blue-400', orange: 'text-orange-400',
  purple: 'text-purple-400', yellow: 'text-yellow-400', rose: 'text-rose-400',
};

function parseSections(text = '') {
  const sections = {};
  SECTION_META.forEach(({ tag }, idx) => {
    const next = SECTION_META[idx + 1]?.tag;
    // Llama 3 sometimes omits brackets: match both [SECTION_N] and SECTION_N
    const re = new RegExp(`\\[?${tag}\\]?([\\s\\S]*?)${next ? `\\[?${next}\\]?` : '$'}`, 'i');
    const match = text.match(re);
    sections[tag] = match ? match[1].trim() : '';
  });
  return sections;
}

// ─── Circular Score ────────────────────────────────────────────────────────
function CircularScore({ score }) {
  const r = 40;
  const circ = 2 * Math.PI * r;
  const dash = circ - (score / 100) * circ;
  const color = score >= 70 ? '#01A982' : score >= 40 ? '#f97316' : '#01A982';
  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      <svg className="-rotate-90" viewBox="0 0 100 100" width="96" height="96">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1e293b" strokeWidth="10" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circ} strokeDashoffset={dash} strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color})`, transition: 'stroke-dashoffset 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)' }} />
      </svg>
      <span className="absolute text-xl font-black text-white">{score}</span>
    </div>
  );
}

// ─── IMPROVEMENT 7: Lead Score Breakdown ───────────────────────────────────
function ScoreBreakdown({ factors }) {
  const bars = [
    { label: 'Inactivity Factor', key: 'Inactivity Factor', max: 40 },
    { label: 'Tech Signals', key: 'Tech Initiatives', max: 25 },
    { label: 'Pain Points', key: 'Pain Points Detected', max: 25 },
    { label: 'Recent Activity', key: 'Recent Activity', max: 10 },
  ];

  const barColor = (value, max) => {
    const pct = max > 0 ? value / max : 0;
    if (pct >= 0.7) return 'bg-emerald-500';
    if (pct >= 0.4) return 'bg-orange-400';
    return 'bg-red-500';
  };

  return (
    <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-4 mt-3">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-widest mb-3">Score Breakdown</p>
      <div className="space-y-2.5">
        {bars.map(({ label, key, max }) => {
          const value = factors?.[key] ?? 0;
          const pct = Math.min((value / max) * 100, 100);
          return (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-400">{label}</span>
                <span className="text-slate-300 font-mono">{value}/{max}</span>
              </div>
              <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-1.5 rounded-full ${barColor(value, max)}`}
                  style={{ width: `${pct}%`, transition: 'width 0.8s ease-out' }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ─── IMPROVEMENT 6: Live Pipeline Tracker ──────────────────────────────────
// Pipeline Tracker Implementation
function PipelineTracker({ steps }) {
  const stepArray = [
    { id: 'scraping', label: 'Real-time web & social\nharvesting', title: 'SCRAPING' },
    { id: 'rag', label: 'Retrieval Augmented\nContextualization', title: 'RAG' },
    { id: 'agents', label: 'Multi-agent orchestration\nswarm', title: 'CREWAI' },
    { id: 'auditor', label: 'Deep analytical synthesis\nengine', title: 'LLAMA 3' },
    { id: 'scoring', label: 'Final probability assessment', title: 'LEAD SCORING' },
  ];
  return (
    <div className="w-full flex flex-col space-y-4 px-4">
      {stepArray.map((s, i) => {
        const st = steps[s.id] || 'pending';
        return (
          <div key={s.id} className="relative flex items-center space-x-6">
            {/* Connection line */}
            {i !== stepArray.length - 1 && (
              <div className="absolute left-[19px] top-10 bottom-[-20px] w-0.5 bg-obsidian-border"></div>
            )}
            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 bg-obsidian-bg shadow z-10 shrink-0 ${
              st === 'done' ? 'border-korhex-green text-korhex-green shadow-[0_0_15px_rgba(1,169,130,0.4)]' : 
              st === 'active' ? 'border-korhex-mint text-korhex-mint animate-pulse shadow-[0_0_15px_rgba(89,220,178,0.2)]' : 
              'border-obsidian-border text-slate-600'
            }`}>
              <span className="text-xs font-bold font-mono">0{i+1}</span>
            </div>
            <div className="flex-1 pt-1">
              <div className="flex items-center space-x-3 mb-1">
                <span className={`font-bold text-sm tracking-widest font-mono uppercase ${st === 'done' || st === 'active' ? 'text-white' : 'text-slate-500'}`}>{s.title}</span>
                {st === 'done' && <CheckCircle className="w-4 h-4 text-korhex-green" />}
                {st === 'active' && <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-korhex-mint/10 text-korhex-mint uppercase border border-korhex-mint/20">Active</span>}
              </div>
              <p className={`text-xs whitespace-pre-line ${st === 'done' || st === 'active' ? 'text-slate-400' : 'text-slate-600'}`}>{s.label}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── IMPROVEMENT 8C: Data Freshness Indicator ──────────────────────────────
function FreshnessIndicator({ timestamp, onRefresh }) {
  if (!timestamp) return null;
  const now = Date.now();
  const diffMs = now - timestamp;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHrs = Math.floor(diffMs / 3600000);

  if (diffMins < 60) {
    return (
      <div className="flex items-center space-x-1.5 text-xs text-emerald-400 mb-3">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        <span>Fresh data · {diffMins < 1 ? 'just now' : `${diffMins}m ago`}</span>
      </div>
    );
  }
  if (diffHrs < 24) {
    return (
      <div className="flex items-center space-x-1.5 text-xs text-yellow-400 mb-3">
        <span className="w-2 h-2 rounded-full bg-yellow-400" />
        <span>Data from {diffHrs}h ago ·{' '}
          <button onClick={onRefresh} className="underline hover:text-yellow-200 transition-colors">Refresh?</button>
        </span>
      </div>
    );
  }
  return (
    <div className="flex items-center space-x-1.5 text-xs text-red-400 mb-3">
      <span className="w-2 h-2 rounded-full bg-red-400" />
      <span>Stale data · Refresh recommended</span>
    </div>
  );
}

// ─── Tab Button ────────────────────────────────────────────────────────────
function TabBtn({ active, onClick, icon: Icon, label }) {
  return (
    <button onClick={onClick}
      className={`flex items-center space-x-1.5 px-3 py-2 rounded-[8px] text-xs font-medium transition-all duration-300 whitespace-nowrap
        ${active ? 'bg-korhex-green/20 text-korhex-green border border-korhex-green/30 shadow-[0_0_10px_rgba(16,185,129,0.1)]'
          : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}`}>
      <Icon className={`w-3.5 h-3.5 transition-transform duration-300 ${active ? 'scale-110' : ''}`} />
      <span>{label}</span>
    </button>
  );
}

// ─── Result Tabs ───────────────────────────────────────────────────────────
function OverviewTab({ result, timestamp, onRefresh }) {
  return (
    <div className="space-y-4 animate-fade-in">
      <div className="animate-fade-in-up" style={{ animationDelay: '50ms' }}>
        <FreshnessIndicator timestamp={timestamp} onRefresh={onRefresh} />
      </div>
      <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-5 flex items-center justify-between card-transition animate-fade-in-up" style={{ animationDelay: '100ms' }}>
        <div>
          <p className="text-slate-400 text-[10px] font-mono uppercase tracking-[0.2em] mb-1 opacity-70">Net New Lead Score</p>
          <div className="text-4xl font-black text-white tracking-tight">{result.lead_score}<span className="text-xl text-slate-500 font-normal">/100</span></div>
          <p className={`text-xs font-bold mt-1.5 flex items-center space-x-1 ${result.lead_score >= 70 ? 'text-korhex-green' : result.lead_score >= 40 ? 'text-orange-400' : 'text-korhex-green'}`}>
            <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
            <span>{result.priority}</span>
          </p>
        </div>
        <CircularScore score={result.lead_score} />
      </div>
      {result._scoreFactors && (
        <div className="animate-fade-in-up" style={{ animationDelay: '150ms' }}>
          <ScoreBreakdown factors={result._scoreFactors} />
        </div>
      )}
      <div className="flex flex-wrap gap-2 animate-fade-in-up" style={{ animationDelay: '200ms' }}>
        <span className={`px-2.5 py-1 rounded-full text-[10px] font-mono font-bold border uppercase tracking-wider
          ${result.data_quality === 'HIGH' ? 'text-korhex-green bg-korhex-green/10 border-korhex-green/30'
            : result.data_quality === 'MEDIUM' ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
              : 'text-red-400 bg-red-500/10 border-red-500/30'}`}>
          {result.data_quality} Quality
        </span>
        {result.tech_keywords && result.tech_keywords.split(' ').slice(0, 5).map((kw, i) => (
          <span key={kw} 
            className="px-2 py-0.5 bg-slate-800/80 text-slate-400 text-[10px] font-medium rounded border border-obsidian-border hover:border-korhex-green/30 hover:text-slate-200 transition-colors"
            style={{ animationDelay: `${250 + (i * 50)}ms` }}>
            {kw}
          </span>
        ))}
      </div>
      {result.data_warning && (
        <div className="flex items-start space-x-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-[8px] text-yellow-300 text-xs animate-shake" style={{ animationDelay: '300ms' }}>
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" /><p>{result.data_warning}</p>
        </div>
      )}
      {result.recent_news?.length > 0 && (
        <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-4 animate-fade-in-up" style={{ animationDelay: '350ms' }}>
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-4 flex items-center space-x-2">
            <Globe className="w-3.5 h-3.5 text-korhex-green" /><span>Recent Intelligence</span>
          </p>
          <div className="space-y-2">
            {result.recent_news.map((n, i) => (
              <a key={i} href={n.url} target="_blank" rel="noreferrer"
                className="flex items-start space-x-3 p-3 rounded-[8px] bg-slate-800/40 hover:bg-slate-700/60 transition-all duration-300 group border border-transparent hover:border-obsidian-border">
                <div className="bg-slate-900 p-2 rounded-[8px] group-hover:bg-korhex-green/10 transition-colors">
                  <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-korhex-green transition-colors" />
                </div>
                <div>
                  <p className="text-slate-200 text-xs font-semibold leading-relaxed group-hover:text-white transition-colors">{n.title}</p>
                  <p className="text-slate-500 text-[10px] mt-1 font-medium">{n.source}</p>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function IntelligenceTab({ result }) {
  const sections = parseSections(result.intelligence_report);
  const hasAny = Object.values(sections).some(Boolean);
  return (
    <div className="space-y-4 animate-fade-in">
      {SECTION_META.map(({ tag, label, icon: Icon, color }, i) =>
        sections[tag] ? (
          <div key={tag} 
            className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-5 card-transition animate-fade-in-up"
            style={{ animationDelay: `${i * 100}ms` }}>
            <p className={`flex items-center space-x-2 text-[10px] font-bold uppercase tracking-[0.2em] mb-3 ${ICON_COLOR[color]}`}>
              <Icon className="w-4 h-4" /><span>{label}</span>
            </p>
            <p className="text-slate-300 text-xs leading-relaxed opacity-90">{sections[tag]}</p>
          </div>
        ) : null
      )}
      {!hasAny && (
        <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-5 animate-fade-in-up">
          <p className="text-slate-300 text-xs leading-relaxed whitespace-pre-wrap">{result.intelligence_report}</p>
        </div>
      )}
    </div>
  );
}

function SpeechTab({ result }) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <span className={`flex items-center space-x-1.5 text-xs font-semibold px-3 py-1 rounded-full border
          ${result.audit_passed ? 'text-korhex-green bg-korhex-green/10 border-korhex-green/30'
            : 'text-red-400 bg-red-500/10 border-red-500/30'}`}>
          {result.audit_passed ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
          <span>{result.audit_passed ? 'Audit Passed' : 'Audit Failed'}</span>
        </span>
        <span className="text-xs text-slate-500 font-mono">{result.word_count} words</span>
      </div>
      <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-4">
        <p className="text-slate-300 text-xs leading-relaxed whitespace-pre-wrap">{result.sales_speech}</p>
      </div>
      {result.audit_notes && <p className="text-xs text-slate-500 italic px-1">{result.audit_notes}</p>}
    </div>
  );
}

function ProductsTab({ result }) {
  if (!result.products?.length)
    return <div className="text-center text-slate-500 py-12 text-sm animate-fade-in">No products matched for this account.</div>;
  return (
    <div className="space-y-4 animate-fade-in">
      {result.products.map((p, i) => (
        <div key={i} 
          className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-5 relative overflow-hidden group card-transition animate-fade-in-up"
          style={{ animationDelay: `${i * 100}ms` }}>
          <div className="absolute top-0 left-0 w-1 h-full bg-korhex-green transition-transform duration-500 origin-bottom group-hover:scale-y-110" />
          <div className="pl-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-korhex-green font-bold text-sm tracking-tight">{p.name}</h3>
              <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-korhex-green group-hover:translate-x-1 transition-all" />
            </div>
            <p className="text-slate-400 text-xs mb-4 leading-relaxed">{p.description}</p>
            <div className="grid grid-cols-2 gap-3">
              {p.roi_pitch && (
                <div className="bg-korhex-green/5 border border-korhex-green/10 rounded-[8px] p-3 group-hover:bg-korhex-green/10 transition-colors">
                  <p className="text-[10px] text-korhex-green/70 font-bold uppercase tracking-wider mb-1">Target ROI</p>
                  <p className="text-emerald-300 text-xs font-medium">{p.roi_pitch}</p>
                </div>
              )}
              {p.pain_solved && (
                <div className="bg-slate-800/40 border border-slate-700/40 rounded-[8px] p-3 group-hover:border-slate-600 transition-colors">
                  <p className="text-[10px] text-slate-500 font-bold uppercase tracking-wider mb-1">Pain Match</p>
                  <p className="text-slate-300 text-xs font-medium">{p.pain_solved}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

function AuditTab({ result }) {
  return (
    <div className="space-y-3">
      <div className={`flex items-center space-x-3 p-4 rounded-[8px] border
        ${result.audit_passed ? 'bg-korhex-green/10 border-korhex-green/30 text-korhex-green'
          : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
        {result.audit_passed ? <CheckCircle className="w-6 h-6 shrink-0" /> : <AlertTriangle className="w-6 h-6 shrink-0" />}
        <div>
          <p className="font-bold text-sm">{result.audit_passed ? 'Compliance Audit Passed' : 'Compliance Audit Failed'}</p>
          <p className="text-xs opacity-70">{result.audit_notes}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-4 text-center">
          <p className="text-slate-400 text-xs font-mono uppercase mb-1">LLM Engine</p>
          <p className="text-slate-100 font-bold text-sm">Llama 3 — Local</p>
          <p className="text-slate-500 text-xs">Ollama @ 127.0.0.1</p>
        </div>
        <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-4 text-center">
          <p className="text-slate-400 text-xs font-mono uppercase mb-1">Data Quality</p>
          <p className="text-slate-100 font-bold text-sm">{result.data_quality}</p>
          <p className="text-slate-500 text-xs">{result.sources?.length ?? 0} sources</p>
        </div>
      </div>
      {result.sources?.length > 0 && (
        <div className="bg-obsidian-bg border border-obsidian-border rounded-[8px] p-4">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest mb-3 flex items-center space-x-1.5">
            <Lock className="w-3.5 h-3.5 text-korhex-green" /><span>Sources Used</span>
          </p>
          <ul className="space-y-1.5">
            {result.sources.map((src, i) => (
              <li key={i}>
                <a href={src} target="_blank" rel="noreferrer"
                  className="flex items-center space-x-2 text-slate-400 hover:text-korhex-green text-xs transition-colors">
                  <ExternalLink className="w-3 h-3 shrink-0" />
                  <span className="truncate">{src}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ─── Investigation Form (shared) ────────────────────────────────────────────
function InvestigationForm({ formData, onChange, onSubmit, onCancel, loading, error, compact = true }) {
  return (
    <form onSubmit={onSubmit} className="space-y-4 animate-fade-in-up">
      <div className="space-y-1">
        <label className="block text-xs text-slate-400 mb-1.5 ml-1">Company Name</label>
        <div className="relative group">
          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500 group-focus-within:text-korhex-green transition-colors" />
          <input type="text" required name="company_name" value={formData.company_name}
            onChange={onChange} placeholder="e.g. Acme Corp"
            disabled={loading}
            className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] pl-9 pr-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-korhex-green/40 border-obsidian-border hover:border-slate-600 focus:border-korhex-green/50 placeholder:text-slate-600 transition-all disabled:opacity-50" />
        </div>
      </div>
      <div className="space-y-1">
        <label className="block text-xs text-slate-400 mb-1.5 ml-1">Company URL</label>
        <input type="url" required name="company_url" value={formData.company_url}
          onChange={onChange} placeholder="https://example.com" disabled={loading}
          className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-korhex-green/40 border-obsidian-border hover:border-slate-600 focus:border-korhex-green/50 placeholder:text-slate-600 transition-all disabled:opacity-50" />
      </div>
      <div className="space-y-1">
        <label className="block text-xs text-slate-400 mb-1.5 ml-1">Industry</label>
        <select name="industry" value={formData.industry} onChange={onChange} disabled={loading}
          className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-korhex-green/40 border-obsidian-border hover:border-slate-600 focus:border-korhex-green/50 transition-all disabled:opacity-50">
          {['Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail', 'Energy', 'Telecommunications'].map(i => (
            <option key={i} value={i}>{i}</option>
          ))}
        </select>
      </div>
      <div className="space-y-1">
        <label className="block text-xs text-slate-400 mb-1.5 ml-1">
          Years Inactive: <span className="text-korhex-green font-semibold">{formData.years_inactive}</span>
        </label>
        <input type="range" min="0" max="10" name="years_inactive"
          value={formData.years_inactive} onChange={onChange} disabled={loading}
          className="w-full accent-korhex-green disabled:opacity-50 cursor-pointer" />
      </div>

      {/* Submit + Cancel */}
      <div className={`grid gap-2 pt-2 ${loading ? 'grid-cols-2' : 'grid-cols-1'}`}>
        <button id="btn-execute" type="submit" disabled={loading}
          className="w-full bg-korhex-green hover:bg-korhex-mint disabled:opacity-60 disabled:cursor-not-allowed text-slate-900 font-bold py-2.5 rounded-[8px] text-sm transition-all flex items-center justify-center space-x-2 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)] active:scale-[0.98]">
          {loading ? (
            <><Loader2 className="w-4 h-4 animate-spin" /><span>Analyzing...</span></>
          ) : (
            <>
              <Search className="w-4 h-4" />
              <span>Execute Intelligence Agents</span>
              <span className="ml-3 text-[10px] font-mono opacity-40 hidden sm:inline">Ctrl+Enter</span>
            </>
          )}
        </button>
        {loading && (
          <button type="button" onClick={onCancel}
            className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 font-bold py-2.5 rounded-[8px] text-sm transition-all flex items-center justify-center space-x-2 active:scale-[0.98]">
            <XCircle className="w-4 h-4" /><span>Cancel</span>
          </button>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-[8px] animate-shake">⚠️ {error}</div>
      )}
      {compact && !loading && (
        <p className="text-slate-600 text-xs text-center animate-fade-in">
          Agents will analyze public data and generate a detailed report.
        </p>
      )}
    </form>
  );
}

// ─── PAGES ─────────────────────────────────────────────────────────────────

// ─── Intelligence Feed Component ────────────────────────────────────────────
function IntelligenceFeed() {
  const feed = [
    { type: 'MARKET SHIFT', time: '2m ago',
      title: 'AI detected high-volume acquisition pattern in EMEA Fintech sectors. Probability of consolidation: 84%.',
      tags: ['FIN-09', 'ACQ-SIGNAL'] },
    { type: 'ACCOUNT ACTIVITY', time: '12m ago',
      title: 'Client Vanguard Group updated compliance parameters across all US nodes.',
      tags: ['REG-COMP'] },
    { type: 'OPPORTUNITY', time: '34m ago',
      title: 'Neural match: Apex Corp matches target profile for Q3 infrastructure upgrade cycle.',
      tags: ['SALES-AI', 'Q3-PREDICT'] },
    { type: 'SYSTEM UPDATE', time: '1h ago',
      title: 'Neural node latency re-calibrated for Singapore (SGP-01) and Tokyo (TYO-03).',
      tags: [] }
  ];

  return (
    <div className="bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] flex flex-col h-full">
      <div className="p-4 border-b border-obsidian-border flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white">Intelligence Feed</h2>
        <span className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-korhex-green/10 border border-korhex-green/20 text-[10px] font-bold text-korhex-green uppercase">
          <span className="w-1.5 h-1.5 rounded-full bg-korhex-green animate-pulse" />
          <span>Live</span>
        </span>
      </div>
      <div className="p-3 border-b border-obsidian-border flex space-x-2">
        <button className="flex-1 py-1.5 bg-korhex-green rounded-[4px] text-[10px] font-bold text-obsidian-bg uppercase tracking-widest shadow-[0_0_10px_rgba(1,169,130,0.2)]">SIGNALS</button>
        <button className="flex-1 py-1.5 bg-obsidian-surface-2 border border-obsidian-border rounded-[4px] text-[10px] font-bold text-slate-500 uppercase tracking-widest hover:text-slate-300 transition-colors">ALERTS</button>
      </div>
      <div className="flex-1 overflow-y-auto custom-scroll p-3 space-y-3">
        {feed.map((item, i) => (
          <div key={i} className="bg-obsidian-surface-2 border border-obsidian-border rounded-[6px] p-3 hover:border-obsidian-border-light transition-all group animate-fade-in-up" style={{ animationDelay: `${i * 100}ms` }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[9px] font-bold text-korhex-mint uppercase tracking-widest">{item.type}</span>
              <span className="text-[10px] text-slate-500">{item.time}</span>
            </div>
            <p className="text-xs text-slate-300 leading-relaxed group-hover:text-white transition-colors">
              {item.title}
            </p>
            {item.tags.length > 0 && (
              <div className="flex items-center space-x-2 mt-3">
                {item.tags.map(t => (
                  <span key={t} className="px-2 py-0.5 rounded-[4px] bg-obsidian-bg border border-obsidian-border text-[9px] font-mono text-slate-500 uppercase">{t}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="p-3 border-t border-obsidian-border mt-auto">
        <button className="w-full py-2 bg-obsidian-surface-2 hover:bg-obsidian-bg border border-obsidian-border rounded-[6px] text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors">
          EXPORT FULL LOG
        </button>
      </div>
    </div>
  );
}

function DashboardPage({ formData, onChange, onSubmit, onCancel, loading, error, result, activeTab, setActiveTab, history, onDelete, onView, prefs, resultsRef, onExport, isExporting, pipelineSteps, onReanalyze }) {
  const TABS = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'intelligence', label: 'Intelligence', icon: FileText },
    { id: 'speech', label: 'Sales Speech', icon: Mic2 },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'audit', label: 'Privacy Audit', icon: Lock },
  ];
  const stats = {
    analyzed: history.length,
    opportunities: history.filter(h => h.score >= 40).length,
    risks: history.filter(h => h.score < 40).length,
  };
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Welcome, <span className="text-korhex-green">{prefs?.name || 'Account Manager'}</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">AI-powered commercial intelligence — fully local</p>
      </div>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Accounts Analyzed', sub: 'This month', value: stats.analyzed, icon: Target, pct: '+12%', pos: true },
          { label: 'Sales Opportunities', sub: 'Detected', value: stats.opportunities, icon: TrendingUp, pct: '+8%', pos: true },
          { label: 'Risk Alerts', sub: 'Active', value: stats.risks, icon: AlertTriangle, pct: `-${stats.risks}`, pos: false },
        ].map(({ label, sub, value, icon: Icon, pct, pos }, i) => (
          <div key={label} 
            className="bg-obsidian-surface-2 border border-obsidian-border rounded-[8px] p-4 card-transition animate-fade-in-up" 
            style={{ animationDelay: `${i * 100}ms` }}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Icon className="w-4 h-4 text-korhex-green" />
                <div>
                  <p className="text-slate-300 text-xs font-medium">{label}</p>
                  <p className="text-slate-500 text-xs">{sub}</p>
                </div>
              </div>
              <span className={`text-xs font-mono font-semibold ${pos ? 'text-korhex-green' : 'text-red-400'}`}>{pct}</span>
            </div>
            <p className="text-3xl font-black text-white">{value}</p>
          </div>
        ))}
      </div>
      
      {/* Main Dashboard Layout */}
      <div className="grid grid-cols-12 gap-5 items-start">
        {/* Left Side: Form + Results + History */}
        <div className={prefs.highDensity ? 'col-span-8 flex flex-col space-y-5' : 'col-span-12 flex flex-col space-y-5'}>
          <div className="bg-obsidian-surface-2 border border-obsidian-border rounded-[8px] p-5">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2 mb-4">
              <Search className="w-4 h-4 text-korhex-green" /><span>Quick Investigation</span>
            </h2>
            <InvestigationForm formData={formData} onChange={onChange} onSubmit={onSubmit} onCancel={onCancel} loading={loading} error={error} compact />
          </div>
          
          {history.length > 0 && (
            <div className="bg-obsidian-surface-2 border border-obsidian-border rounded-[8px] p-5">
              <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2 mb-4">
                <History className="w-4 h-4 text-korhex-green" /><span>Recent Investigations</span>
              </h2>
              <HistoryTable history={history} onDelete={onDelete} onView={onView} onReanalyze={onReanalyze} />
            </div>
          )}
        </div>

        {/* Right Side: Intelligence Feed */}
        {prefs.highDensity && (
          <div className="col-span-4 h-[600px]">
            <IntelligenceFeed />
          </div>
        )}
      </div>
    </div>
  );
}


function NewInvestigationPage({ formData, onChange, onSubmit, onCancel, loading, error, result, activeTab, setActiveTab, resultsRef, onExport, isExporting, pipelineSteps, onReanalyze }) {
  const TABS = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'intelligence', label: 'Intelligence', icon: FileText },
    { id: 'speech', label: 'Sales Speech', icon: Mic2 },
    { id: 'products', label: 'Products', icon: Package },
    { id: 'audit', label: 'Privacy Audit', icon: Lock },
  ];
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">New <span className="text-korhex-green">Investigation</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">Run a full AI-powered analysis on a target account</p>
      </div>
      <div className="grid grid-cols-5 gap-5">
        {/* Form - bigger here */}
        <div className="col-span-2 bg-obsidian-surface-2 border border-obsidian-border rounded-[8px] p-6 h-fit">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2 mb-5">
            <Target className="w-4 h-4 text-korhex-green" /><span>Target Account</span>
          </h2>
          <InvestigationForm formData={formData} onChange={onChange} onSubmit={onSubmit}
            onCancel={onCancel} loading={loading} error={error} compact={false} />
          <div className="mt-6 pt-5 border-t border-obsidian-border space-y-2">
            <p className="text-xs text-slate-500 font-semibold uppercase tracking-widest">Pipeline</p>
            {['DuckDuckGo Web Scraping', 'RAG Portfolio Matching', 'CrewAI Dual Agent', 'Llama 3 — Ollama local', 'Lead Scoring Engine'].map((s, i) => (
              <div key={s} className="flex items-center space-x-2 text-xs text-slate-400">
                <div className="w-5 h-5 rounded-full bg-korhex-green/20 border border-korhex-green/30 flex items-center justify-center text-korhex-green font-bold text-xs shrink-0">{i + 1}</div>
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>
        {/* Results - bigger tabs */}
        <div className="col-span-3 bg-obsidian-surface-2 border border-obsidian-border rounded-[8px] p-5 relative">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Activity className="w-4 h-4 text-korhex-green" /><span>Analysis Results</span>
            </h2>
            {result && !loading && (
              <button onClick={onExport} disabled={isExporting}
                className="flex items-center space-x-1 text-xs px-3 py-1.5 rounded-md bg-obsidian-bg border border-obsidian-border text-slate-300 hover:text-korhex-green hover:border-korhex-green/50 transition-colors disabled:opacity-50">
                {isExporting ? <Loader2 className="w-3 h-3 animate-spin" /> : <Download className="w-3 h-3" />}
                <span>{isExporting ? 'Exporting...' : 'Export PDF'}</span>
              </button>
            )}
          </div>
          {loading ? (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4 w-full px-6">
              <Activity className="w-8 h-8 text-korhex-green animate-pulse" />
              <PipelineTracker steps={pipelineSteps} />
            </div>
          ) : result ? (
            <div className="space-y-3" ref={resultsRef}>
              <div className="flex items-center space-x-1 bg-obsidian-bg border border-obsidian-border rounded-[8px] p-1 overflow-x-auto">
                {TABS.map(t => (
                  <TabBtn key={t.id} active={activeTab === t.id} onClick={() => setActiveTab(t.id)} icon={t.icon} label={t.label} />
                ))}
              </div>
              <div className="max-h-[500px] overflow-y-auto pr-1 custom-scroll">
                {activeTab === 'overview' && <OverviewTab result={result} timestamp={result._timestamp} onRefresh={onReanalyze} />}
                {activeTab === 'intelligence' && <IntelligenceTab result={result} />}
                {activeTab === 'speech' && <SpeechTab result={result} />}
                {activeTab === 'products' && <ProductsTab result={result} />}
                {activeTab === 'audit' && <AuditTab result={result} />}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-3 opacity-40">
              <Shield className="w-14 h-14 text-slate-600" />
              <p className="text-slate-500 text-sm">Fill in the form and execute the agents.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── IMPROVEMENT 8A: History Table with Re-analyze + Copy Speech ──────────
function HistoryTable({ history, onDelete, onView, onReanalyze }) {
  const [copiedIdx, setCopiedIdx] = useState(null);

  const handleCopy = (h, i) => {
    const text = h.fullData?.sales_speech || '';
    if (!text) return;
    navigator.clipboard.writeText(text).then(() => {
      setCopiedIdx(i);
      setTimeout(() => setCopiedIdx(null), 2000);
    });
  };

  return (
    <div className="overflow-x-auto animate-fade-in">
      <table className="w-full text-xs">
        <thead>
          <tr className="text-slate-500 border-b border-obsidian-border uppercase tracking-widest text-[10px] font-bold">
            {['Company', 'Industry', 'Lead Score', 'Status', 'Actions'].map(col => (
              <th key={col} className="pb-3 text-left px-4">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/40">
          {history.map((h, i) => (
            <tr key={i} className="hover:bg-slate-800/40 transition-all group animate-fade-in-up" style={{ animationDelay: `${i * 50}ms` }}>
              <td className="py-4 px-4 font-semibold text-slate-200">{h.company}</td>
              <td className="py-4 px-4 text-slate-400">{h.industry}</td>
              <td className="py-4 px-4">
                <div className="flex items-center space-x-3">
                  <div className="flex-1 bg-slate-800 rounded-full h-1.5 w-20 overflow-hidden">
                    <div className="h-1.5 rounded-full bg-korhex-green transition-all duration-1000 ease-out" style={{ width: `${h.score}%` }} />
                  </div>
                  <span className="text-slate-300 font-mono font-bold w-6">{h.score}</span>
                </div>
              </td>
              <td className="py-4 px-4">
                <span className="px-2.5 py-1 bg-korhex-green/10 text-korhex-green border border-korhex-green/20 rounded-full inline-flex items-center space-x-1.5 text-[10px] font-bold">
                  <div className="w-1 h-1 rounded-full bg-current animate-pulse" />
                  <span>{h.status}</span>
                </span>
              </td>
              <td className="py-4 px-4 text-right">
                <div className="flex items-center space-x-1 justify-end">
                  <button onClick={() => onView(i)}
                    className="flex p-2 items-center space-x-1.5 text-slate-400 hover:text-korhex-green hover:bg-korhex-green/10 rounded-[8px] transition-all active:scale-95">
                    <Eye className="w-3.5 h-3.5" /><span className="font-semibold">View</span>
                  </button>
                  <button onClick={() => onReanalyze(i)}
                    title="Re-analyze this account"
                    className="flex p-2 items-center space-x-1.5 text-slate-400 hover:text-cyan-400 hover:bg-cyan-400/10 rounded-[8px] transition-all active:scale-95">
                    <RefreshCw className="w-3.5 h-3.5" /><span className="font-semibold">Re-run</span>
                  </button>
                  <button onClick={() => handleCopy(h, i)}
                    title="Copy sales speech"
                    className={`flex p-2 items-center space-x-1.5 rounded-[8px] transition-all active:scale-95 ${copiedIdx === i
                        ? 'text-emerald-400 bg-emerald-400/10'
                        : 'text-slate-400 hover:text-yellow-400 hover:bg-yellow-400/10'
                      }`}>
                    <Copy className="w-3.5 h-3.5" />
                    <span className="font-semibold">{copiedIdx === i ? 'Copied!' : 'Copy'}</span>
                  </button>
                  <button onClick={() => onDelete(i)}
                    className="p-2 text-slate-600 hover:text-red-400 hover:bg-red-400/10 rounded-[8px] transition-all opacity-0 group-hover:opacity-100 active:scale-95">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function HistoryPage({ history, onDelete, onView }) {
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Investigation <span className="text-korhex-green">History</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">{history.length} accounts analyzed in this session</p>
      </div>
      <div className="bg-obsidian-surface-2 border border-obsidian-border rounded-[8px] p-5">
        {history.length > 0
          ? <HistoryTable history={history} onDelete={onDelete} onView={onView} onReanalyze={() => { }} />
          : (
            <div className="flex flex-col items-center justify-center py-20 space-y-3 opacity-40">
              <History className="w-14 h-14 text-slate-600" />
              <p className="text-slate-500 text-sm">No investigations yet. Run an analysis to get started.</p>
            </div>
          )}
      </div>
    </div>
  );
}

function UserPreferencesPage({ prefs, onSave }) {
  const [form, setForm] = useState({ ...prefs });
  const [saved, setSaved] = useState(false);

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const handleSave = () => {
    onSave(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">User <span className="text-korhex-green">Preferences</span></h1>
          <p className="text-slate-400 text-sm mt-0.5">Personalize your KORHEX.AI experience</p>
        </div>
        <button onClick={handleSave} className="flex items-center space-x-2 px-6 py-2.5 bg-korhex-green text-obsidian-bg font-bold rounded-[8px] text-sm shadow-[0_0_15px_rgba(1,169,130,0.3)] hover:scale-105 active:scale-95 transition-all">
          <Save className="w-4 h-4" />
          <span>{saved ? 'Settings Saved!' : 'Save Calibration'}</span>
        </button>
      </div>

      <div className="grid grid-cols-2 gap-5">
        {/* Profile */}
        <div className="col-span-1 bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] p-5 space-y-4">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
            <User className="w-3.5 h-3.5 text-korhex-green" /><span>Profile Identity</span>
          </p>
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-korhex-green/20 border-2 border-korhex-green/40 flex items-center justify-center text-2xl font-black text-korhex-green overflow-hidden shrink-0">
              {form.photoUrl ? (
                <img src={form.photoUrl} alt="Preview" className="w-full h-full object-cover" />
              ) : (
                (form.name || 'A').charAt(0).toUpperCase()
              )}
            </div>
            <div className="flex-1">
              <label className="block text-[10px] text-slate-500 font-bold uppercase mb-1.5 leading-none tracking-wider">Photo Entity URL</label>
              <input type="text" value={form.photoUrl} onChange={e => handleChange('photoUrl', e.target.value)}
                placeholder="https://..."
                className="w-full bg-obsidian-bg border border-obsidian-border rounded-[6px] px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-korhex-green/50 placeholder:text-slate-700 transition-all shadow-inner" />
            </div>
          </div>
          <div>
            <label className="block text-[10px] text-slate-500 font-bold uppercase mb-1.5 leading-none tracking-wider">Display Name</label>
            <input type="text" value={form.name} onChange={e => handleChange('name', e.target.value)}
              placeholder="e.g. Carlos Mendoza"
              className="w-full bg-obsidian-bg border border-obsidian-border rounded-[6px] px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-korhex-green/50 placeholder:text-slate-700 transition-all shadow-inner" />
          </div>
        </div>

        {/* Neural Calibration */}
        <div className="col-span-1 bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] p-5 space-y-4">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
            <Cpu className="w-3.5 h-3.5 text-korhex-green" /><span>Neural Calibration</span>
          </p>
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-[10px] text-slate-500 font-bold uppercase leading-none">Inference temperature</label>
              <span className="text-korhex-green font-mono text-xs px-1.5 py-0.5 bg-korhex-green/10 rounded">{form.aiTemperature}</span>
            </div>
            <input type="range" min="0" max="1" step="0.1" value={form.aiTemperature}
              onChange={e => handleChange('aiTemperature', parseFloat(e.target.value))}
              className="w-full accent-korhex-green h-1.5 bg-slate-800 rounded-full appearance-none cursor-pointer" />
            <div className="flex justify-between text-[9px] text-slate-600 mt-2 uppercase font-bold tracking-tighter">
              <span>Logical Precision</span>
              <span>Linguistic Bloom</span>
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-obsidian-bg border border-obsidian-border rounded-[6px] hover:border-slate-700 transition-colors">
             <div>
               <p className="text-xs font-semibold text-slate-200 leading-none mb-1">High Density Interface</p>
               <p className="text-[9px] text-slate-500">Enable advanced telemetry visual layers.</p>
             </div>
             <button onClick={() => handleChange('highDensity', !form.highDensity)} className={`w-9 h-5 rounded-full relative transition-colors ${form.highDensity ? 'bg-korhex-green' : 'bg-slate-700'}`}>
                <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${form.highDensity ? 'left-5' : 'left-1'}`} />
             </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        {/* Logic Cluster */}
        <div className="bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] p-5 space-y-4">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
            <Target className="w-3.5 h-3.5 text-korhex-green" /><span>Logic Cluster</span>
          </p>
          <div>
            <label className="block text-[10px] text-slate-500 font-bold uppercase mb-1.5">Default Sector</label>
            <select value={form.defaultIndustry} onChange={e => handleChange('defaultIndustry', e.target.value)}
              className="w-full bg-obsidian-bg border border-obsidian-border rounded-[6px] px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-korhex-green/50 transition-all cursor-pointer">
              {['Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail', 'Energy', 'Telecommunications'].map(i => (
                <option key={i} value={i}>{i}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center justify-between p-3 bg-obsidian-bg border border-obsidian-border rounded-[6px] hover:border-slate-700 transition-colors">
             <div>
               <p className="text-xs font-semibold text-slate-200 leading-none mb-1">Auto-sync Persistence</p>
               <p className="text-[9px] text-slate-500">Sync results to session history buffer.</p>
             </div>
             <button onClick={() => handleChange('autoSave', !form.autoSave)} className={`w-9 h-5 rounded-full relative transition-colors ${form.autoSave ? 'bg-korhex-green' : 'bg-slate-700'}`}>
                <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${form.autoSave ? 'left-5' : 'left-1'}`} />
             </button>
          </div>
        </div>

        {/* Global Synchronization */}
        <div className="bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] p-5 space-y-5">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
            <Globe className="w-3.5 h-3.5 text-korhex-green" /><span>Global Sync</span>
          </p>
          <div className="space-y-2">
            <label className="block text-[10px] text-slate-500 font-bold uppercase mb-1">Linguistic node</label>
            <div className="flex space-x-2">
              {['English', 'Spanish'].map(lang => (
                <button key={lang} onClick={() => handleChange('reportLang', lang)}
                  className={`flex-1 py-2 text-[10px] font-bold rounded-[6px] border transition-all uppercase tracking-widest ${form.reportLang === lang ? 'bg-korhex-green/10 border-korhex-green text-korhex-green shadow-[0_0_10px_rgba(1,169,130,0.1)]' : 'bg-obsidian-bg border-obsidian-border text-slate-500 hover:text-slate-300'}`}>
                  {lang}
                </button>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-obsidian-bg border border-obsidian-border rounded-[6px] hover:border-slate-700 transition-colors">
             <div>
               <p className="text-xs font-semibold text-slate-200 leading-none mb-1">Stealth Execution</p>
               <p className="text-[9px] text-slate-500">Omit detailed neural telemetry traces.</p>
             </div>
             <button onClick={() => handleChange('stealthMode', !form.stealthMode)} className={`w-9 h-5 rounded-full relative transition-colors ${form.stealthMode ? 'bg-korhex-green' : 'bg-slate-700'}`}>
                <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${form.stealthMode ? 'left-5' : 'left-1'}`} />
             </button>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── AUTHENTICATION & ADMIN ──────────────────────────────────────────────────
function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const params = new URLSearchParams();
      params.append('username', username);
      params.append('password', password);
      const res = await fetch('http://localhost:8000/api/v1/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: params
      });
      if (!res.ok) throw new Error('Invalid credentials');
      const data = await res.json();
      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-obsidian-bg items-center justify-center">
      <div className="bg-obsidian-surface-2 p-8 rounded-[8px] border border-obsidian-border w-96 shadow-xl">
        <div className="text-center mb-6">
          <Shield className="w-10 h-10 text-korhex-green mx-auto mb-2" />
          <h1 className="text-2xl font-bold text-white tracking-wider">KORHEX.AI</h1>
          <p className="text-slate-400 text-sm mt-1">Enterprise Authentication</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Username</label>
            <input type="text" required value={username} onChange={e => setUsername(e.target.value)}
              className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2 text-sm text-white focus:outline-none focus:border-korhex-green/50" />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1.5">Password</label>
            <input type="password" required value={password} onChange={e => setPassword(e.target.value)}
              className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2 text-sm text-white focus:outline-none focus:border-korhex-green/50" />
          </div>
          {error && <div className="text-red-400 text-xs p-2 bg-red-400/10 rounded border border-red-400/20">{error}</div>}
          <button type="submit" disabled={loading}
            className="w-full bg-korhex-green hover:bg-korhex-mint text-slate-900 font-bold py-2.5 rounded-[8px] text-sm transition-all mt-4 flex justify-center items-center">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}

function AdminDashboardPage({ token }) {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'user' });

  const fetchUsers = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Failed to fetch users');
      setUsers(await res.json());
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchUsers(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify(newUser)
      });
      if (!res.ok) {
        const d = await res.json();
        throw new Error(d.detail || 'Error creating user');
      }
      setNewUser({ username: '', password: '', role: 'user' });
      fetchUsers();
    } catch (err) { alert(err.message); }
  };

  const handleDelete = async (username) => {
    if (!window.confirm(`Delete ${username}?`)) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/auth/users/${username}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!res.ok) throw new Error('Error deleting user');
      fetchUsers();
    } catch (err) { alert(err.message); }
  };

  const handleChangePassword = async (username) => {
    const pw = window.prompt(`New password for ${username}:`);
    if (!pw) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/auth/users/${username}/password`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
        body: JSON.stringify({ password: pw })
      });
      if (!res.ok) throw new Error('Error updating password');
      alert('Password updated');
    } catch (err) { alert(err.message); }
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Admin <span className="text-korhex-green">Dashboard</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">Manage access and user credentials</p>
      </div>
      <div className="grid grid-cols-3 gap-5">
        <div className="col-span-1 bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] p-5 h-fit">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">Create User</h2>
          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="block text-xs text-slate-400 mb-1">Username</label>
              <input type="text" required value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2 text-sm text-white" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Password</label>
              <input type="password" required value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2 text-sm text-white" />
            </div>
            <div>
              <label className="block text-xs text-slate-400 mb-1">Role</label>
              <select value={newUser.role} onChange={e => setNewUser({ ...newUser, role: e.target.value })} className="w-full bg-obsidian-bg border border-obsidian-border rounded-[8px] px-3 py-2 text-sm text-white">
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <button type="submit" className="w-full bg-korhex-green hover:bg-korhex-mint text-slate-900 font-bold py-2 rounded-[8px] text-sm mt-2 focus:outline-none">Create</button>
          </form>
        </div>
        <div className="col-span-2 bg-obsidian-surface-1 border border-obsidian-border rounded-[8px] p-5">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">System Users</h2>
          {loading ? <Loader2 className="w-6 h-6 animate-spin text-korhex-green" /> : error ? <p className="text-red-400">{error}</p> : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead><tr className="border-b border-obsidian-border text-slate-500"><th className="pb-2">ID</th><th className="pb-2">Username</th><th className="pb-2">Role</th><th className="pb-2 text-right">Actions</th></tr></thead>
                <tbody className="divide-y divide-obsidian-border/50">
                  {users.map(u => (
                    <tr key={u.id} className="hover:bg-slate-800/20">
                      <td className="py-3">{u.id}</td>
                      <td className="py-3 font-medium text-white">{u.username}</td>
                      <td className="py-3"><span className="px-2 py-1 rounded bg-slate-800 text-xs">{u.role}</span></td>
                      <td className="py-3 text-right space-x-2">
                        <button onClick={() => handleChangePassword(u.username)} className="text-xs text-blue-400 hover:text-blue-300">Reset PW</button>
                        {u.username !== 'admin' && <button onClick={() => handleDelete(u.username)} className="text-xs text-red-400 hover:text-red-300">Delete</button>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── APP ROOT ──────────────────────────────────────────────────────────────
export default function App() {
  const [prefs, setPrefs] = useState({
    name: 'Account Manager',
    role: 'Account Manager',
    defaultIndustry: 'Technology',
    defaultYears: 0,
    reportLang: 'English',
    showPipeline: true,
    photoUrl: '',
    aiTemperature: 0.7,
    autoSave: true,
    highDensity: true,
    stealthMode: false
  });
  const abortControllerRef = useRef(null);
  const resultsRef = useRef(null);
  const [isExporting, setIsExporting] = useState(false);

  const [auth, setAuth] = useState(() => {
    const saved = sessionStorage.getItem('korhex_auth');
    try {
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  // Load user-specific prefs when auth changes
  useEffect(() => {
    if (auth?.username) {
      // Priority 1: Backend preferences (cloud)
      if (auth.preferences) {
        try {
          setPrefs(JSON.parse(auth.preferences));
          return;
        } catch (err) {
          console.error("Error parsing cloud prefs", err);
        }
      }
      // Priority 2: Local storage (if offline or first time)
      const savedPrefs = localStorage.getItem(`korhex_prefs_${auth.username}`);
      if (savedPrefs) {
        try {
          setPrefs(JSON.parse(savedPrefs));
        } catch (err) {
          console.error("Error parsing local prefs", err);
        }
      }
    } else {
      // Reset to defaults on logout
      setPrefs({
        name: 'Account Manager',
        role: 'Account Manager',
        defaultIndustry: 'Technology',
        defaultYears: 0,
        reportLang: 'English',
        showPipeline: true,
        photoUrl: '',
        aiTemperature: 0.7,
        autoSave: true,
        highDensity: true,
        stealthMode: false
      });
    }
  }, [auth]);

  // Persist prefs per user
  useEffect(() => {
    if (auth?.username && auth?.access_token) {
      const prefsStr = JSON.stringify(prefs);
      localStorage.setItem(`korhex_prefs_${auth.username}`, prefsStr);
      
      // Cloud sync (background)
      fetch('http://localhost:8000/api/v1/auth/me/prefs', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${auth.access_token}`
        },
        body: JSON.stringify({ preferences: prefsStr })
      }).catch(err => console.debug("Cloud sync offline:", err));
    }
  }, [prefs, auth?.username, auth?.access_token]);

  const [formData, setFormData] = useState({
    company_name: '', company_url: '', industry: prefs.defaultIndustry, years_inactive: prefs.defaultYears
  });

  // ── Mejora 6: Pipeline tracker state ──────────────────────
  const initialPipelineSteps = { scraping: 'pending', rag: 'pending', agents: 'pending', auditor: 'pending', scoring: 'pending' };
  const [pipelineSteps, setPipelineSteps] = useState(initialPipelineSteps);

  // Sync form defaults when prefs change
  useEffect(() => {
    setFormData(prev => ({ ...prev, industry: prefs.defaultIndustry, years_inactive: prefs.defaultYears }));
  }, [prefs.defaultIndustry, prefs.defaultYears]);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('overview');
  const [history, setHistory] = useState([]);
  const [activePage, setActivePage] = useState('dashboard');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // ── Mejora 8B: Ctrl+Enter keyboard shortcut ────────────────
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter' && !loading) {
        document.getElementById('btn-execute')?.closest('form')?.requestSubmit();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [loading]);

  const handleAnalyze = async (e) => {
    e.preventDefault();

    // 🏆 EASTER EGG (Opción 1: Búsqueda Secreta)
    const searchTarget = formData.company_name.toLowerCase();
    const isEasterEgg = ['zuany', 'quiroz', 'herrera', 'reyes'].every(name => searchTarget.includes(name));

    if (isEasterEgg) {
      setLoading(true); setError(''); setResult(null); setActiveTab('overview');
      // Simulamos un retraso como si los agentes estuvieran operando...
      setTimeout(() => {
        const fakeData = {
          company_name: "ESTATE: KORHEX.AI CREATORS",
          industry: "Cybersecurity & AI",
          lead_score: 100,
          priority: "GOD TIER OVERRIDES",
          intelligence_report: `[SECTION_1]\nArchitectural Masters: Zuany, Quiroz, Herrera & Reyes.\n\n[SECTION_2]\nBuilding the next generation of zero-leakage Enterprise AI platforms.\n\n[SECTION_3]\nImpeccable logic execution. No vulnerabilities detected in the core crew algorithms.`,
          sales_speech: "This platform was forged in the depths of late-night coding. We yield the ultimate power over local Llama 3 agents. Absolute control. Zero data leakage.",
          word_count: 999,
          audit_passed: true,
          audit_notes: "Compliance Bypassed by System Creators",
          data_quality: "GODLIKE",
          data_warning: null,
          products: [
            { name: "Zuany Core", description: "The architect of the foundation.", roi_pitch: "1000% stability.", pain_solved: "Structural integrity secured." },
            { name: "Quiroz Protocol", description: "Oversight and security logic.", roi_pitch: "Absolute zero data leakage.", pain_solved: "Unauthorized access completely halted." },
            { name: "Herrera Engine", description: "The driving force of the AI ops.", roi_pitch: "10x speed in processing.", pain_solved: "Agent hallucination mitigated." },
            { name: "Reyes UX", description: "The master of the interface.", roi_pitch: "Infinite user engagement.", pain_solved: "Visual pain eliminated forever." }
          ],
          recent_news: [{ title: "KORHEX.AI Team revolutionizes Local Enterprise Agents", source: "Global Tech Times", url: "#" }],
          sources: ["https://korhex.ai/top-secret-creators"],
          tech_keywords: "REACT FASTAPI LLAMA3 CREWAI GENIUSES"
        };
        setResult(fakeData);
        setHistory(prev => [{
          company: "KORHEX CREATORS", industry: "AI Elite",
          score: 100, priority: "MAX", status: 'Unstoppable', timestamp: new Date().toLocaleTimeString(),
          fullData: fakeData, fullFormData: formData
        }, ...prev.slice(0, 9)]);
        setLoading(false);
      }, 2000); // 2 segundos de suspenso
      return;
    }

    // Cancel any previous in-flight request
    if (abortControllerRef.current) abortControllerRef.current.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true); setError(''); setResult(null); setActiveTab('overview');
    // Reset + start pipeline steps
    setPipelineSteps({ scraping: 'active', rag: 'pending', agents: 'pending', auditor: 'pending', scoring: 'pending' });

    // Simulate step progression (backend is single-shot, no SSE on main endpoint)
    const stepTimers = [
      setTimeout(() => setPipelineSteps(s => ({ ...s, scraping: 'done', rag: 'active' })), 4000),
      setTimeout(() => setPipelineSteps(s => ({ ...s, rag: 'done', agents: 'active' })), 8000),
      setTimeout(() => setPipelineSteps(s => ({ ...s, agents: 'done', auditor: 'active' })), 12000),
      setTimeout(() => setPipelineSteps(s => ({ ...s, auditor: 'done', scoring: 'active' })), 16000),
    ];

    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        signal: controller.signal,
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${auth?.access_token}` },
        body: JSON.stringify({
          ...formData,
          years_inactive: parseInt(formData.years_inactive, 10),
          report_language: prefs.reportLang === 'Spanish' ? 'es' : 'en',
          ai_temperature: prefs.aiTemperature,
          stealth_mode: prefs.stealthMode
        })
      });
      stepTimers.forEach(clearTimeout);
      if (!res.ok) {
        const errData = await res.json();
        setPipelineSteps(s => ({ ...s, scraping: 'error' }));
        throw new Error(errData.detail?.[0]?.msg || errData.detail || 'Server error.');
      }
      const data = await res.json();
      setPipelineSteps({ scraping: 'done', rag: 'done', agents: 'done', auditor: 'done', scoring: 'done' });
      // Attach metadata for Improvement 7 (score factors) and 8C (freshness)
      const enrichedData = {
        ...data,
        _scoreFactors: data.score_factors || null,
        _timestamp: Date.now(),
      };
      setResult(enrichedData);
      if (prefs.autoSave) {
        setHistory(prev => [{
          company: data.company_name, industry: formData.industry,
          score: data.lead_score, priority: data.priority,
          status: 'Completed', timestamp: new Date().toLocaleTimeString(),
          fullData: enrichedData, fullFormData: { ...formData }
        }, ...prev.slice(0, 9)]);
      }
    } catch (err) {
      stepTimers.forEach(clearTimeout);
      if (err.name === 'AbortError') {
        setError('Analysis cancelled.');
        setPipelineSteps(initialPipelineSteps);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
  };

  const handleDeleteHistory = (index) => {
    setHistory(prev => prev.filter((_, i) => i !== index));
  };

  const handleViewReport = (index) => {
    const item = history[index];
    if (item && item.fullData) {
      setResult(item.fullData);
      setFormData(item.fullFormData);
      setActiveTab('overview');
      setActivePage('dashboard');
    }
  };

  // ── Mejora 8A: Re-analyze (pre-fill form + auto-submit) ────
  const handleReanalyze = useCallback((index) => {
    const item = history[index];
    if (!item) return;
    setFormData({ ...item.fullFormData });
    setActivePage('dashboard');
    // Use a small delay to let the form state settle before faking submit
    setTimeout(() => {
      document.getElementById('btn-execute')?.closest('form')?.requestSubmit();
    }, 100);
  }, [history]);

  // ── Mejora 8C: Refresh current result ─────────────────────
  const handleReanalyzeCurrentResult = useCallback(() => {
    document.getElementById('btn-execute')?.closest('form')?.requestSubmit();
  }, []);

  const handleExportPDF = async () => {
    if (!result) return;
    setIsExporting(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/export-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
      });

      if (!res.ok) {
        throw new Error('Error generating PDF on server');
      }

      // Convert response to Blob and trigger download
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `KORHEX_${result.company_name.replace(/[^a-z0-9]/gi, '_').toUpperCase()}_Report.pdf`);
      document.body.appendChild(link);
      link.click();

      // Cleanup
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('PDF Export Error:', err);
      alert('Error exporting PDF: ' + err.message);
    } finally {
      setIsExporting(false);
    }
  };

  const NAV = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'nueva', label: 'New Investigation', icon: Search },
    { id: 'historial', label: 'History', icon: History },
    ...(auth?.role === 'admin' ? [{ id: 'admin', label: 'Admin Panel', icon: Users }] : [])
  ];

  const handleLogin = (data) => {
    sessionStorage.setItem('korhex_auth', JSON.stringify(data));
    setAuth(data);
  };

  const handleLogout = () => {
    sessionStorage.removeItem('korhex_auth');
    setAuth(null);
  };

  if (!auth) {
    return <LoginScreen onLogin={handleLogin} />;
  }

    return (
    <div className="flex h-screen bg-obsidian-bg text-slate-100 font-sans overflow-hidden">
      {/* SIDEBAR */}
      <aside className="w-[240px] shrink-0 bg-obsidian-surface-1 border-r border-obsidian-border flex flex-col z-40 relative">
        <div className="h-[64px] px-5 flex items-center border-b border-obsidian-border shrink-0 cursor-default">
          <div className="flex items-center space-x-2 group">
            <div className="w-8 h-8 rounded-[8px] bg-korhex-green/20 flex items-center justify-center group-hover:bg-korhex-green/30 transition-all">
              <Shield className="w-4 h-4 text-korhex-green" />
            </div>
            <div>
              <span className="block font-bold text-base tracking-wider text-white leading-tight">KORHEX.AI</span>
              <span className="block text-[8px] uppercase tracking-widest text-korhex-green font-mono leading-tight">Enterprise Intelligence</span>
            </div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-6 space-y-1.5 custom-scroll overflow-y-auto">
          <p className="px-3 text-[10px] font-bold text-slate-500 uppercase tracking-[0.2em] mb-3 relative z-10">NAVIGATION</p>
          {NAV.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setActivePage(id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded text-sm transition-all duration-200
                ${activePage === id
                  ? 'bg-obsidian-surface-2 text-korhex-green border-l-2 border-korhex-green font-medium shadow-[inset_0_0_15px_rgba(1,169,130,0.05)]'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-obsidian-surface-2 border-l-2 border-transparent hover:border-obsidian-border'}`}>
              <Icon className={`w-4 h-4 shrink-0 transition-transform ${activePage === id ? 'scale-110' : ''}`} />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="p-4 border-t border-obsidian-border">
          <button onClick={handleLogout} className="w-full flex items-center justify-between px-3 py-2 text-sm text-slate-500 hover:text-red-400 hover:bg-red-400/10 rounded transition-all group">
            <span className="font-medium">Sign Out</span>
            <ExternalLink className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </aside>

      {/* TOP BAR */}
      <header className="fixed top-0 left-[240px] right-0 h-[64px] bg-obsidian-bg/80 backdrop-blur-md border-b border-obsidian-border z-30 flex items-center justify-end px-6">
        <div className="flex items-center space-x-4">
          <button onClick={() => setActivePage('config')} className="text-slate-400 hover:text-korhex-green transition-colors" title="Preferences">
            <Settings className="w-5 h-5" />
          </button>
          <div className="w-8 h-8 rounded-full bg-korhex-green/20 border border-korhex-green/40 flex items-center justify-center text-korhex-green font-bold text-sm overflow-hidden whitespace-nowrap">
            {prefs.photoUrl ? (
              <img src={prefs.photoUrl} alt="Profile" className="w-full h-full object-cover" />
            ) : (
              (auth?.username || 'U').charAt(0).toUpperCase()
            )}
          </div>
        </div>
      </header>

      {/* MAIN CONTAINER */}
      <div className="flex-1 mt-[64px] overflow-y-auto custom-scroll bg-obsidian-bg">
        <main key={activePage} className="p-8 max-w-7xl mx-auto animate-fade-in relative z-10">
          {activePage === 'dashboard' && (
            <DashboardPage
              formData={formData} onChange={handleInputChange}
              onSubmit={handleAnalyze} onCancel={handleCancel} loading={loading} error={error}
              result={result} activeTab={activeTab} setActiveTab={setActiveTab}
              history={history} onDelete={handleDeleteHistory} onView={handleViewReport} prefs={prefs}
              resultsRef={resultsRef} onExport={handleExportPDF} isExporting={isExporting}
              pipelineSteps={pipelineSteps} onReanalyze={handleReanalyzeCurrentResult}
            />
          )}
          {activePage === 'nueva' && (
            <NewInvestigationPage
              formData={formData} onChange={handleInputChange}
              onSubmit={handleAnalyze} onCancel={handleCancel} loading={loading} error={error}
              result={result} activeTab={activeTab} setActiveTab={setActiveTab}
              resultsRef={resultsRef} onExport={handleExportPDF} isExporting={isExporting}
              pipelineSteps={pipelineSteps} onReanalyze={handleReanalyzeCurrentResult}
            />
          )}
          {activePage === 'historial' && <HistoryPage history={history} onDelete={handleDeleteHistory} onView={handleViewReport} />}
          {activePage === 'config' && <UserPreferencesPage prefs={prefs} onSave={setPrefs} />}
          {activePage === 'admin' && auth?.role === 'admin' && <AdminDashboardPage token={auth.access_token} />}
        </main>
      </div>
    </div>
  );
}
