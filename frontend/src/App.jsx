import React, { useState, useEffect, useRef } from 'react';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import {
  LayoutDashboard, Search, History, Settings, Shield,
  TrendingUp, Target, AlertTriangle, Loader2, CheckCircle,
  FileText, Mic2, Package, Lock, Activity, Cpu, Users,
  DollarSign, BarChart2, ExternalLink, Globe, ChevronRight,
  Eye, User, Languages, Download, Save, Bell, Trash2, XCircle
} from 'lucide-react';

// ─── Utilities ─────────────────────────────────────────────────────────────
const SECTION_META = [
  { tag: 'SECTION_1', label: 'Business Strategy',   icon: TrendingUp,    color: 'emerald' },
  { tag: 'SECTION_2', label: 'Tech Environment',    icon: Cpu,           color: 'blue'    },
  { tag: 'SECTION_3', label: 'Pain Points',         icon: AlertTriangle, color: 'orange'  },
  { tag: 'SECTION_4', label: 'Decision Makers',     icon: Users,         color: 'purple'  },
  { tag: 'SECTION_5', label: 'Financial Signals',   icon: DollarSign,    color: 'yellow'  },
  { tag: 'SECTION_6', label: 'Competitive Context', icon: BarChart2,     color: 'rose'    },
];
const ICON_COLOR = {
  emerald:'text-hpe-green', blue:'text-blue-400', orange:'text-orange-400',
  purple:'text-purple-400',   yellow:'text-yellow-400', rose:'text-rose-400',
};

function parseSections(text = '') {
  const sections = {};
  SECTION_META.forEach(({ tag }, idx) => {
    const next  = SECTION_META[idx + 1]?.tag;
    const re    = new RegExp(`\\[${tag}\\]([\\s\\S]*?)${next ? `\\[${next}\\]` : '$'}`, 'i');
    const match = text.match(re);
    sections[tag] = match ? match[1].trim() : '';
  });
  return sections;
}

// ─── Circular Score ────────────────────────────────────────────────────────
function CircularScore({ score }) {
  const r    = 40;
  const circ = 2 * Math.PI * r;
  const dash = circ - (score / 100) * circ;
  const color = score >= 70 ? '#10b981' : score >= 40 ? '#f97316' : '#10b981';
  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      <svg className="-rotate-90" viewBox="0 0 100 100" width="96" height="96">
        <circle cx="50" cy="50" r={r} fill="none" stroke="#1e293b" strokeWidth="10" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circ} strokeDashoffset={dash} strokeLinecap="round"
          style={{ filter:`drop-shadow(0 0 6px ${color})`, transition:'stroke-dashoffset 0.8s ease' }} />
      </svg>
      <span className="absolute text-xl font-black text-white">{score}</span>
    </div>
  );
}

// ─── Tab Button ────────────────────────────────────────────────────────────
function TabBtn({ active, onClick, icon: Icon, label }) {
  return (
    <button onClick={onClick}
      className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all whitespace-nowrap
        ${active ? 'bg-hpe-green/20 text-hpe-green border border-hpe-green/30'
                 : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'}`}>
      <Icon className="w-3.5 h-3.5" /><span>{label}</span>
    </button>
  );
}

// ─── Result Tabs ───────────────────────────────────────────────────────────
function OverviewTab({ result }) {
  return (
    <div className="space-y-3">
      <div className="bg-hpe-bg border border-hpe-border rounded-xl p-5 flex items-center justify-between">
        <div>
          <p className="text-slate-400 text-xs font-mono uppercase tracking-widest mb-1">Net New Lead Score</p>
          <div className="text-3xl font-black text-white">{result.lead_score}<span className="text-lg text-slate-500">/100</span></div>
          <p className={`text-xs font-semibold mt-1 ${result.lead_score >= 70 ? 'text-hpe-green' : result.lead_score >= 40 ? 'text-orange-400' : 'text-hpe-green'}`}>
            {result.priority}
          </p>
        </div>
        <CircularScore score={result.lead_score} />
      </div>
      <div className="flex flex-wrap gap-2">
        <span className={`px-2.5 py-1 rounded-full text-xs font-mono font-semibold border uppercase
          ${result.data_quality==='HIGH' ? 'text-hpe-green bg-hpe-green/10 border-hpe-green/30'
          : result.data_quality==='MEDIUM' ? 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
          : 'text-red-400 bg-red-500/10 border-red-500/30'}`}>
          {result.data_quality} Quality
        </span>
        {result.tech_keywords && result.tech_keywords.split(' ').slice(0,5).map(kw => (
          <span key={kw} className="px-2 py-0.5 bg-slate-800 text-slate-400 text-xs rounded border border-hpe-border">{kw}</span>
        ))}
      </div>
      {result.data_warning && (
        <div className="flex items-start space-x-2 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl text-yellow-300 text-xs">
          <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" /><p>{result.data_warning}</p>
        </div>
      )}
      {result.recent_news?.length > 0 && (
        <div className="bg-hpe-bg border border-hpe-border rounded-xl p-4">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest mb-3 flex items-center space-x-1.5">
            <Globe className="w-3.5 h-3.5 text-hpe-green" /><span>Recent News</span>
          </p>
          <div className="space-y-2">
            {result.recent_news.map((n,i) => (
              <a key={i} href={n.url} target="_blank" rel="noreferrer"
                className="flex items-start space-x-2 p-2.5 rounded-lg bg-slate-800/40 hover:bg-slate-700/40 transition-colors group">
                <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-hpe-green shrink-0 mt-0.5 transition-colors" />
                <div>
                  <p className="text-slate-200 text-xs font-medium leading-snug">{n.title}</p>
                  <p className="text-slate-500 text-xs mt-0.5">{n.source}</p>
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
  const hasAny   = Object.values(sections).some(Boolean);
  return (
    <div className="space-y-3">
      {SECTION_META.map(({ tag, label, icon: Icon, color }) =>
        sections[tag] ? (
          <div key={tag} className="bg-hpe-bg border border-hpe-border rounded-xl p-4">
            <p className={`flex items-center space-x-1.5 text-xs font-semibold uppercase tracking-widest mb-2 ${ICON_COLOR[color]}`}>
              <Icon className="w-3.5 h-3.5" /><span>{label}</span>
            </p>
            <p className="text-slate-300 text-xs leading-relaxed">{sections[tag]}</p>
          </div>
        ) : null
      )}
      {!hasAny && (
        <div className="bg-hpe-bg border border-hpe-border rounded-xl p-4">
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
          ${result.audit_passed ? 'text-hpe-green bg-hpe-green/10 border-hpe-green/30'
                                : 'text-red-400 bg-red-500/10 border-red-500/30'}`}>
          {result.audit_passed ? <CheckCircle className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
          <span>{result.audit_passed ? 'Audit Passed' : 'Audit Failed'}</span>
        </span>
        <span className="text-xs text-slate-500 font-mono">{result.word_count} words</span>
      </div>
      <div className="bg-hpe-bg border border-hpe-border rounded-xl p-4">
        <p className="text-slate-300 text-xs leading-relaxed whitespace-pre-wrap">{result.sales_speech}</p>
      </div>
      {result.audit_notes && <p className="text-xs text-slate-500 italic px-1">{result.audit_notes}</p>}
    </div>
  );
}

function ProductsTab({ result }) {
  if (!result.products?.length)
    return <div className="text-center text-slate-500 py-12 text-sm">No products matched for this account.</div>;
  return (
    <div className="space-y-3">
      {result.products.map((p,i) => (
        <div key={i} className="bg-hpe-bg border border-hpe-border rounded-xl p-4 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-0.5 h-full bg-hpe-green" />
          <div className="pl-3">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-hpe-green font-bold text-sm">{p.name}</h3>
              <ChevronRight className="w-4 h-4 text-slate-600 group-hover:text-hpe-green transition-colors" />
            </div>
            <p className="text-slate-300 text-xs mb-3">{p.description}</p>
            <div className="grid grid-cols-2 gap-2">
              {p.roi_pitch && (
                <div className="bg-hpe-green/10 border border-hpe-green/20 rounded-lg p-2">
                  <p className="text-xs text-hpe-green/70 font-mono uppercase mb-1">ROI</p>
                  <p className="text-emerald-300 text-xs">{p.roi_pitch}</p>
                </div>
              )}
              {p.pain_solved && (
                <div className="bg-slate-800/60 border border-slate-600/40 rounded-lg p-2">
                  <p className="text-xs text-slate-400 font-mono uppercase mb-1">Pain Solved</p>
                  <p className="text-slate-300 text-xs">{p.pain_solved}</p>
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
      <div className={`flex items-center space-x-3 p-4 rounded-xl border
        ${result.audit_passed ? 'bg-hpe-green/10 border-hpe-green/30 text-hpe-green'
                              : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
        {result.audit_passed ? <CheckCircle className="w-6 h-6 shrink-0" /> : <AlertTriangle className="w-6 h-6 shrink-0" />}
        <div>
          <p className="font-bold text-sm">{result.audit_passed ? 'Compliance Audit Passed' : 'Compliance Audit Failed'}</p>
          <p className="text-xs opacity-70">{result.audit_notes}</p>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-hpe-bg border border-hpe-border rounded-xl p-4 text-center">
          <p className="text-slate-400 text-xs font-mono uppercase mb-1">LLM Engine</p>
          <p className="text-slate-100 font-bold text-sm">Llama 3 — Local</p>
          <p className="text-slate-500 text-xs">Ollama @ 127.0.0.1</p>
        </div>
        <div className="bg-hpe-bg border border-hpe-border rounded-xl p-4 text-center">
          <p className="text-slate-400 text-xs font-mono uppercase mb-1">Data Quality</p>
          <p className="text-slate-100 font-bold text-sm">{result.data_quality}</p>
          <p className="text-slate-500 text-xs">{result.sources?.length ?? 0} sources</p>
        </div>
      </div>
      {result.sources?.length > 0 && (
        <div className="bg-hpe-bg border border-hpe-border rounded-xl p-4">
          <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest mb-3 flex items-center space-x-1.5">
            <Lock className="w-3.5 h-3.5 text-hpe-green" /><span>Sources Used</span>
          </p>
          <ul className="space-y-1.5">
            {result.sources.map((src,i) => (
              <li key={i}>
                <a href={src} target="_blank" rel="noreferrer"
                  className="flex items-center space-x-2 text-slate-400 hover:text-hpe-green text-xs transition-colors">
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
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">Company Name</label>
        <div className="relative">
          <Globe className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-500" />
          <input type="text" required name="company_name" value={formData.company_name}
            onChange={onChange} placeholder="e.g. Acme Corp"
            disabled={loading}
            className="w-full bg-hpe-bg border border-hpe-border rounded-lg pl-9 pr-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-hpe-green/40 placeholder:text-slate-600 transition-all disabled:opacity-50" />
        </div>
      </div>
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">Company URL</label>
        <input type="url" required name="company_url" value={formData.company_url}
          onChange={onChange} placeholder="https://example.com" disabled={loading}
          className="w-full bg-hpe-bg border border-hpe-border rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-hpe-green/40 placeholder:text-slate-600 transition-all disabled:opacity-50" />
      </div>
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">Industry</label>
        <select name="industry" value={formData.industry} onChange={onChange} disabled={loading}
          className="w-full bg-hpe-bg border border-hpe-border rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-hpe-green/40 transition-all disabled:opacity-50">
          {['Technology','Finance','Healthcare','Manufacturing','Retail','Energy','Telecommunications'].map(i => (
            <option key={i} value={i}>{i}</option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-xs text-slate-400 mb-1.5">
          Years Inactive: <span className="text-hpe-green font-semibold">{formData.years_inactive}</span>
        </label>
        <input type="range" min="0" max="10" name="years_inactive"
          value={formData.years_inactive} onChange={onChange} disabled={loading}
          className="w-full accent-hpe-green disabled:opacity-50" />
      </div>

      {/* Submit + Cancel */}
      <div className={`grid gap-2 ${loading ? 'grid-cols-2' : 'grid-cols-1'}`}>
        <button type="submit" disabled={loading}
          className="bg-hpe-green hover:bg-hpe-green-hover disabled:opacity-60 disabled:cursor-not-allowed text-slate-900 font-bold py-2.5 rounded-lg text-sm transition-all flex items-center justify-center space-x-2 shadow-[0_0_20px_rgba(16,185,129,0.3)] hover:shadow-[0_0_30px_rgba(16,185,129,0.5)]">
          {loading
            ? <><Loader2 className="w-4 h-4 animate-spin" /><span>Analyzing...</span></>
            : <><Search className="w-4 h-4" /><span>Execute Intelligence Agents</span></>}
        </button>
        {loading && (
          <button type="button" onClick={onCancel}
            className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30 font-bold py-2.5 rounded-lg text-sm transition-all flex items-center justify-center space-x-2">
            <XCircle className="w-4 h-4" /><span>Cancel</span>
          </button>
        )}
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-xs rounded-lg">⚠️ {error}</div>
      )}
      {compact && !loading && (
        <p className="text-slate-600 text-xs text-center">
          Agents will analyze public data and generate a detailed report.
        </p>
      )}
    </form>
  );
}

// ─── PAGES ─────────────────────────────────────────────────────────────────
function DashboardPage({ formData, onChange, onSubmit, onCancel, loading, error, result, activeTab, setActiveTab, history, onDelete, onView, prefs, resultsRef, onExport, isExporting }) {
  const TABS = [
    { id:'overview',     label:'Overview',      icon:Activity  },
    { id:'intelligence', label:'Intelligence',  icon:FileText  },
    { id:'speech',       label:'Sales Speech',  icon:Mic2      },
    { id:'products',     label:'Products',      icon:Package   },
    { id:'audit',        label:'Privacy Audit', icon:Lock      },
  ];
  const stats = {
    analyzed:      history.length,
    opportunities: history.filter(h => h.score >= 40).length,
    risks:         history.filter(h => h.score < 40).length,
  };
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">Welcome, <span className="text-hpe-green">{prefs?.name || 'Account Manager'}</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">AI-powered commercial intelligence — fully local</p>
      </div>
      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label:'Accounts Analyzed',    sub:'This month', value:stats.analyzed,      icon:Target,         pct:'+12%', pos:true  },
          { label:'Sales Opportunities',  sub:'Detected',   value:stats.opportunities, icon:TrendingUp,     pct:'+8%',  pos:true  },
          { label:'Risk Alerts',          sub:'Active',     value:stats.risks,         icon:AlertTriangle,  pct:`-${stats.risks}`, pos:false },
        ].map(({ label,sub,value,icon:Icon,pct,pos }) => (
          <div key={label} className="bg-hpe-panel border border-hpe-border rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <Icon className="w-4 h-4 text-hpe-green" />
                <div>
                  <p className="text-slate-300 text-xs font-medium">{label}</p>
                  <p className="text-slate-500 text-xs">{sub}</p>
                </div>
              </div>
              <span className={`text-xs font-mono font-semibold ${pos ? 'text-hpe-green' : 'text-red-400'}`}>{pct}</span>
            </div>
            <p className="text-3xl font-black text-white">{value}</p>
          </div>
        ))}
      </div>
      {/* Form + Results */}
      <div className="grid grid-cols-5 gap-5">
        <div className="col-span-2 bg-hpe-panel border border-hpe-border rounded-xl p-5 h-fit">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2 mb-5">
            <Search className="w-4 h-4 text-hpe-green" /><span>New Investigation</span>
          </h2>
          <InvestigationForm formData={formData} onChange={onChange} onSubmit={onSubmit}
            onCancel={onCancel} loading={loading} error={error} compact />
        </div>
        <div className="col-span-3 bg-hpe-panel border border-hpe-border rounded-xl p-5 relative">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <TrendingUp className="w-4 h-4 text-hpe-green" /><span>AI Results</span>
            </h2>
            {result && !loading && (
              <button onClick={onExport} disabled={isExporting}
                className="flex items-center space-x-1 text-xs px-3 py-1.5 rounded-md bg-hpe-bg border border-hpe-border text-slate-300 hover:text-hpe-green hover:border-hpe-green/50 transition-colors disabled:opacity-50">
                {isExporting ? <Loader2 className="w-3 h-3 animate-spin"/> : <Download className="w-3 h-3" />}
                <span>{isExporting ? 'Exporting...' : 'Export PDF'}</span>
              </button>
            )}
          </div>
          {loading ? (
            <div className="flex flex-col items-center justify-center min-h-[350px] space-y-4">
              <Activity className="w-10 h-10 text-hpe-green animate-pulse" />
              <div className="text-center">
                <p className="text-slate-200 text-sm font-medium">Orchestrating CrewAI Agents</p>
                <p className="text-slate-500 text-xs mt-1 animate-pulse">Llama 3 analyzing account intelligence locally...</p>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-3" ref={resultsRef}>
              <div className="flex items-center space-x-1 bg-hpe-bg border border-hpe-border rounded-lg p-1 overflow-x-auto">
                {TABS.map(t => (
                  <TabBtn key={t.id} active={activeTab===t.id} onClick={() => setActiveTab(t.id)} icon={t.icon} label={t.label} />
                ))}
              </div>
              <div className="max-h-[460px] overflow-y-auto pr-1 custom-scroll">
                {activeTab==='overview'     && <OverviewTab     result={result} />}
                {activeTab==='intelligence' && <IntelligenceTab result={result} />}
                {activeTab==='speech'       && <SpeechTab       result={result} />}
                {activeTab==='products'     && <ProductsTab     result={result} />}
                {activeTab==='audit'        && <AuditTab        result={result} />}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center min-h-[350px] space-y-3 opacity-40">
              <Shield className="w-14 h-14 text-slate-600" />
              <p className="text-slate-500 text-sm">Enter a target account to initialize the local engine.</p>
            </div>
          )}
        </div>
      </div>
      {/* History table */}
      {history.length > 0 && (
        <div className="bg-hpe-panel border border-hpe-border rounded-xl p-5">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2 mb-4">
            <History className="w-4 h-4 text-hpe-green" /><span>Investigation History</span>
          </h2>
          <HistoryTable history={history} onDelete={onDelete} onView={onView} />
        </div>
      )}
    </div>
  );
}

function NewInvestigationPage({ formData, onChange, onSubmit, onCancel, loading, error, result, activeTab, setActiveTab, resultsRef, onExport, isExporting }) {
  const TABS = [
    { id:'overview',     label:'Overview',      icon:Activity  },
    { id:'intelligence', label:'Intelligence',  icon:FileText  },
    { id:'speech',       label:'Sales Speech',  icon:Mic2      },
    { id:'products',     label:'Products',      icon:Package   },
    { id:'audit',        label:'Privacy Audit', icon:Lock      },
  ];
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-white">New <span className="text-hpe-green">Investigation</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">Run a full AI-powered analysis on a target account</p>
      </div>
      <div className="grid grid-cols-5 gap-5">
        {/* Form - bigger here */}
        <div className="col-span-2 bg-hpe-panel border border-hpe-border rounded-xl p-6 h-fit">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2 mb-5">
            <Target className="w-4 h-4 text-hpe-green" /><span>Target Account</span>
          </h2>
          <InvestigationForm formData={formData} onChange={onChange} onSubmit={onSubmit}
            onCancel={onCancel} loading={loading} error={error} compact={false} />
          <div className="mt-6 pt-5 border-t border-hpe-border space-y-2">
            <p className="text-xs text-slate-500 font-semibold uppercase tracking-widest">Pipeline</p>
            {['DuckDuckGo Web Scraping','RAG Portfolio Matching','CrewAI Dual Agent','Llama 3 — Ollama local','Lead Scoring Engine'].map((s,i) => (
              <div key={s} className="flex items-center space-x-2 text-xs text-slate-400">
                <div className="w-5 h-5 rounded-full bg-hpe-green/20 border border-hpe-green/30 flex items-center justify-center text-hpe-green font-bold text-xs shrink-0">{i+1}</div>
                <span>{s}</span>
              </div>
            ))}
          </div>
        </div>
        {/* Results - bigger tabs */}
        <div className="col-span-3 bg-hpe-panel border border-hpe-border rounded-xl p-5 relative">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
              <Activity className="w-4 h-4 text-hpe-green" /><span>Analysis Results</span>
            </h2>
            {result && !loading && (
              <button onClick={onExport} disabled={isExporting}
                className="flex items-center space-x-1 text-xs px-3 py-1.5 rounded-md bg-hpe-bg border border-hpe-border text-slate-300 hover:text-hpe-green hover:border-hpe-green/50 transition-colors disabled:opacity-50">
                {isExporting ? <Loader2 className="w-3 h-3 animate-spin"/> : <Download className="w-3 h-3" />}
                <span>{isExporting ? 'Exporting...' : 'Export PDF'}</span>
              </button>
            )}
          </div>
          {loading ? (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
              <Activity className="w-12 h-12 text-hpe-green animate-pulse" />
              <div className="text-center">
                <p className="text-slate-200 text-sm font-medium">Orchestrating CrewAI Agents</p>
                <p className="text-slate-500 text-xs mt-1 animate-pulse">Llama 3 analyzing account intelligence locally...</p>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-3" ref={resultsRef}>
              <div className="flex items-center space-x-1 bg-hpe-bg border border-hpe-border rounded-lg p-1 overflow-x-auto">
                {TABS.map(t => (
                  <TabBtn key={t.id} active={activeTab===t.id} onClick={() => setActiveTab(t.id)} icon={t.icon} label={t.label} />
                ))}
              </div>
              <div className="max-h-[500px] overflow-y-auto pr-1 custom-scroll">
                {activeTab==='overview'     && <OverviewTab     result={result} />}
                {activeTab==='intelligence' && <IntelligenceTab result={result} />}
                {activeTab==='speech'       && <SpeechTab       result={result} />}
                {activeTab==='products'     && <ProductsTab     result={result} />}
                {activeTab==='audit'        && <AuditTab        result={result} />}
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

function HistoryTable({ history, onDelete, onView }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="text-slate-500 border-b border-hpe-border">
            {['Company','Industry','Lead Score','Status','Action'].map(col => (
              <th key={col} className="pb-2.5 text-left font-medium pr-4">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/40">
          {history.map((h,i) => (
            <tr key={i} className="hover:bg-slate-800/20 transition-colors group">
              <td className="py-3 pr-4 font-semibold text-slate-200">{h.company}</td>
              <td className="py-3 pr-4 text-slate-400">{h.industry}</td>
              <td className="py-3 pr-4">
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-slate-800 rounded-full h-1.5 w-16">
                    <div className="h-1.5 rounded-full bg-hpe-green transition-all" style={{ width:`${h.score}%` }} />
                  </div>
                  <span className="text-slate-300 font-mono">{h.score}</span>
                </div>
              </td>
              <td className="py-3 pr-4">
                <span className="px-2 py-0.5 bg-hpe-green/15 text-hpe-green border border-hpe-green/25 rounded-full inline-block">
                  {h.status}
                </span>
              </td>
              <td className="py-2 pr-4">
                <div className="flex items-center space-x-3">
                  <button onClick={() => onView(i)} className="flex py-1 px-2 items-center space-x-1.5 text-slate-400 focus:outline-none hover:text-hpe-green hover:bg-hpe-green/10 rounded transition-all">
                    <Eye className="w-4 h-4" /><span className="font-medium">View Report</span>
                  </button>
                  <button onClick={() => onDelete(i)}
                    title="Delete this entry"
                    className="flex p-1.5 items-center justify-center rounded text-slate-600 focus:outline-none hover:bg-red-500/10 hover:text-red-400 transition-all opacity-0 group-hover:opacity-100">
                    <Trash2 className="w-4 h-4" />
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
        <h1 className="text-xl font-bold text-white">Investigation <span className="text-hpe-green">History</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">{history.length} accounts analyzed in this session</p>
      </div>
      <div className="bg-hpe-panel border border-hpe-border rounded-xl p-5">
        {history.length > 0
          ? <HistoryTable history={history} onDelete={onDelete} onView={onView} />
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
  const [form, setForm]     = useState({ ...prefs });
  const [saved, setSaved]   = useState(false);

  const handleChange = (key, value) => setForm(prev => ({ ...prev, [key]: value }));

  const handleSave = () => {
    onSave(form);
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  return (
    <div className="space-y-5 max-w-2xl">
      <div>
        <h1 className="text-xl font-bold text-white">User <span className="text-hpe-green">Preferences</span></h1>
        <p className="text-slate-400 text-sm mt-0.5">Personalize your KORHEX.AI experience</p>
      </div>

      {/* Profile */}
      <div className="bg-hpe-panel border border-hpe-border rounded-xl p-5 space-y-4">
        <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
          <User className="w-3.5 h-3.5 text-hpe-green" /><span>Profile</span>
        </p>
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-full bg-hpe-green/20 border-2 border-hpe-green/40 flex items-center justify-center text-2xl font-black text-hpe-green">
            {(form.name || 'A').charAt(0).toUpperCase()}
          </div>
          <div className="flex-1">
            <label className="block text-xs text-slate-400 mb-1.5">Your Name</label>
            <input type="text" value={form.name} onChange={e => handleChange('name', e.target.value)}
              placeholder="e.g. Carlos Mendoza"
              className="w-full bg-hpe-bg border border-hpe-border rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-hpe-green/40 placeholder:text-slate-600 transition-all" />
          </div>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">Role</label>
          <select value={form.role} onChange={e => handleChange('role', e.target.value)}
            className="w-full bg-hpe-bg border border-hpe-border rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-hpe-green/40 transition-all">
            {['Account Manager','Sales Executive','Sales Engineer','Team Lead','Director'].map(r => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Investigation Defaults */}
      <div className="bg-hpe-panel border border-hpe-border rounded-xl p-5 space-y-4">
        <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
          <Target className="w-3.5 h-3.5 text-hpe-green" /><span>Investigation Defaults</span>
        </p>
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">Default Industry</label>
          <select value={form.defaultIndustry} onChange={e => handleChange('defaultIndustry', e.target.value)}
            className="w-full bg-hpe-bg border border-hpe-border rounded-lg px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:ring-2 focus:ring-hpe-green/40 transition-all">
            {['Technology','Finance','Healthcare','Manufacturing','Retail','Energy','Telecommunications'].map(i => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
          <p className="text-xs text-slate-500 mt-1.5">Pre-selects this industry every time you open a new investigation.</p>
        </div>
        <div>
          <label className="block text-xs text-slate-400 mb-1.5">
            Default Years Inactive: <span className="text-hpe-green font-semibold">{form.defaultYears}</span>
          </label>
          <input type="range" min="0" max="10" value={form.defaultYears}
            onChange={e => handleChange('defaultYears', parseInt(e.target.value))}
            className="w-full accent-hpe-green" />
          <p className="text-xs text-slate-500 mt-1.5">Slider will start here on every new investigation.</p>
        </div>
      </div>

      {/* Report Preferences */}
      <div className="bg-hpe-panel border border-hpe-border rounded-xl p-5 space-y-4">
        <p className="text-xs font-semibold text-slate-300 uppercase tracking-widest flex items-center space-x-2">
          <Languages className="w-3.5 h-3.5 text-hpe-green" /><span>Report Preferences</span>
        </p>
        <div>
          <label className="block text-xs text-slate-400 mb-2">Report Language</label>
          <div className="flex space-x-2">
            {['English','Spanish'].map(lang => (
              <button key={lang} type="button"
                onClick={() => handleChange('reportLang', lang)}
                className={`flex-1 py-2 rounded-lg text-sm font-medium border transition-all
                  ${form.reportLang === lang
                    ? 'bg-hpe-green/20 text-hpe-green border-hpe-green/40'
                    : 'bg-hpe-bg text-slate-400 border-hpe-border hover:border-slate-500'}`}>
                {lang}
              </button>
            ))}
          </div>
          <p className="text-xs text-slate-500 mt-1.5">Language used by Llama 3 to write the intelligence report and sales speech.</p>
        </div>
        <div className="flex items-center justify-between py-0.5">
          <div>
            <p className="text-slate-200 text-sm">Show Pipeline Steps</p>
            <p className="text-slate-500 text-xs">Display the 5-step agent pipeline on New Investigation page</p>
          </div>
          <button type="button" onClick={() => handleChange('showPipeline', !form.showPipeline)}
            className={`w-11 h-6 rounded-full transition-all relative ${
              form.showPipeline ? 'bg-hpe-green' : 'bg-slate-700'}`}>
            <span className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-all ${
              form.showPipeline ? 'left-5.5 translate-x-0.5' : 'left-0.5'}`} />
          </button>
        </div>
      </div>

      {/* Save Button */}
      <button onClick={handleSave}
        className={`flex items-center space-x-2 px-5 py-3 rounded-xl font-semibold text-sm transition-all ${
          saved
            ? 'bg-hpe-green/20 text-hpe-green border border-hpe-green/40'
            : 'bg-hpe-green hover:bg-hpe-green-hover text-slate-900 shadow-[0_0_20px_rgba(16,185,129,0.3)]'}`}>
        <Save className="w-4 h-4" />
        <span>{saved ? 'Preferences Saved!' : 'Save Preferences'}</span>
      </button>
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
  });
  const abortControllerRef = useRef(null);
  const resultsRef = useRef(null);
  const [isExporting, setIsExporting] = useState(false);

  const [formData, setFormData] = useState({
    company_name:'', company_url:'', industry: prefs.defaultIndustry, years_inactive: prefs.defaultYears
  });

  // Sync form defaults when prefs change
  useEffect(() => {
    setFormData(prev => ({ ...prev, industry: prefs.defaultIndustry, years_inactive: prefs.defaultYears }));
  }, [prefs.defaultIndustry, prefs.defaultYears]);

  const [loading,    setLoading]    = useState(false);
  const [result,     setResult]     = useState(null);
  const [error,      setError]      = useState('');
  const [activeTab,  setActiveTab]  = useState('overview');
  const [history,    setHistory]    = useState([]);
  const [activePage, setActivePage] = useState('dashboard');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    // Cancel any previous in-flight request
    if (abortControllerRef.current) abortControllerRef.current.abort();
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true); setError(''); setResult(null); setActiveTab('overview');
    try {
      const res = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        signal: controller.signal,
        headers: { 'Content-Type':'application/json', 'Authorization':'Bearer DUMMY_JWT' },
        body: JSON.stringify({
          ...formData,
          years_inactive: parseInt(formData.years_inactive, 10),
          report_language: prefs.reportLang === 'Spanish' ? 'es' : 'en'
        })
      });
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail?.[0]?.msg || errData.detail || 'Server error.');
      }
      const data = await res.json();
      setResult(data);
      setHistory(prev => [{
        company: data.company_name, industry: formData.industry,
        score: data.lead_score, priority: data.priority,
        status: 'Completed', timestamp: new Date().toLocaleTimeString(),
        fullData: data, fullFormData: formData
      }, ...prev.slice(0, 9)]);
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('Analysis cancelled.');
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
    { id:'dashboard', label:'Dashboard',         icon:LayoutDashboard },
    { id:'nueva',     label:'New Investigation', icon:Search          },
    { id:'historial', label:'History',           icon:History         },
    { id:'config',    label:'Preferences',        icon:Settings        },
  ];

  return (
    <div className="flex h-screen bg-hpe-bg text-slate-100 font-sans overflow-hidden">

      {/* SIDEBAR */}
      <aside className="w-52 shrink-0 bg-hpe-sidebar border-r border-hpe-border flex flex-col">
        <div className="p-5 border-b border-hpe-border">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg bg-hpe-green/20 border border-hpe-green/40 flex items-center justify-center">
              <Shield className="w-4 h-4 text-hpe-green" />
            </div>
            <span className="font-bold text-base tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-hpe-green to-teal-300">
              KORHEX.AI
            </span>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-0.5">
          {NAV.map(({ id, label, icon: Icon }) => (
            <button key={id} onClick={() => setActivePage(id)}
              className={`w-full flex items-center space-x-2.5 px-3 py-2.5 rounded-lg text-sm transition-all
                ${activePage === id
                  ? 'bg-hpe-green/15 text-hpe-green border border-hpe-green/25'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
              <Icon className="w-4 h-4 shrink-0" />
              <span>{label}</span>
            </button>
          ))}
        </nav>
        <div className="p-3 border-t border-hpe-border">
          <div className="flex items-center space-x-2 px-3 py-2.5 rounded-lg bg-hpe-green/10 border border-hpe-green/20">
            <Shield className="w-4 h-4 text-hpe-green shrink-0" />
            <div>
              <p className="text-hpe-green text-xs font-semibold">Zero Data Leakage</p>
              <p className="text-slate-500 text-xs">Local Mode Active</p>
            </div>
          </div>
        </div>
      </aside>

      {/* MAIN */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 max-w-6xl">
          {activePage === 'dashboard' && (
            <DashboardPage
              formData={formData} onChange={handleInputChange}
              onSubmit={handleAnalyze} onCancel={handleCancel} loading={loading} error={error}
              result={result} activeTab={activeTab} setActiveTab={setActiveTab}
              history={history} onDelete={handleDeleteHistory} onView={handleViewReport} prefs={prefs}
              resultsRef={resultsRef} onExport={handleExportPDF} isExporting={isExporting}
            />
          )}
          {activePage === 'nueva' && (
            <NewInvestigationPage
              formData={formData} onChange={handleInputChange}
              onSubmit={handleAnalyze} onCancel={handleCancel} loading={loading} error={error}
              result={result} activeTab={activeTab} setActiveTab={setActiveTab}
              resultsRef={resultsRef} onExport={handleExportPDF} isExporting={isExporting}
            />
          )}
          {activePage === 'historial' && <HistoryPage history={history} onDelete={handleDeleteHistory} onView={handleViewReport} />}
          {activePage === 'config'    && <UserPreferencesPage prefs={prefs} onSave={setPrefs} />}
        </div>
      </div>
    </div>
  );
}
