import import React, { useState } from 'react';
import { Search, Loader2, ShieldCheck, Activity } from 'lucide-react';

export default function App() {
  const [formData, setFormData] = useState({ 
    company_name: '', company_url: '', industry: 'Technology', years_inactive: 0 
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Consumimos la API de FastAPI
      const response = await fetch('http://localhost:8000/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer DUMMY_JWT_TOKEN_HERE'
        },
        body: JSON.stringify({
          ...formData,
          years_inactive: parseInt(formData.years_inactive, 10)
        })
      });

      if (!response.ok) {
        const errData = await response.json();
        // Controlamos si la validación Pydantic (Anti-Prompt Injection) saltó
        throw new Error(errData.detail?.[0]?.msg || errData.detail || 'Error en validación o servidor.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans selection:bg-emerald-500/30">
      
      {/* ── HEADER ── */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-10 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ShieldCheck className="text-emerald-400 w-8 h-8" />
            <h1 className="text-2xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-teal-200">
              KORHEX.AI
            </h1>
          </div>
          <span className="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-xs font-mono uppercase tracking-widest border border-emerald-500/20 rounded-full">
            Zero Data Leakage Environment
          </span>
        </div>
      </header>

      {/* ── CONTENIDO PRINCIPAL ── */}
      <main className="max-w-7xl mx-auto p-6 lg:p-12 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* PANEL IZQUIERDO: FORMULARIO */}
        <div className="lg:col-span-1 bg-slate-800/40 border border-slate-700 rounded-2xl p-6 shadow-xl relative overflow-hidden">
          <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-emerald-400 to-teal-500"></div>
          
          <h2 className="text-xl font-semibold mb-6 flex items-center space-x-2">
            <Search className="w-5 h-5 text-emerald-400" />
            <span>Target Account</span>
          </h2>

          <form onSubmit={handleAnalyze} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Company URL</label>
              <input 
                type="url" required name="company_url"
                value={formData.company_url} onChange={handleInputChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all placeholder:text-slate-600"
                placeholder="https://example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Company Name</label>
              <input 
                type="text" required name="company_name"
                value={formData.company_name} onChange={handleInputChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all placeholder:text-slate-600"
                placeholder="e.g. Acme Corp"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Industry</label>
              <select 
                name="industry" value={formData.industry} onChange={handleInputChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
              >
                {['Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail', 'Energy'].map(ind => (
                  <option key={ind} value={ind}>{ind}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Years Inactive</label>
              <input 
                type="number" min="0" name="years_inactive"
                value={formData.years_inactive} onChange={handleInputChange}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
              />
            </div>
            
            <button 
              type="submit" disabled={loading}
              className="w-full mt-4 bg-emerald-500 hover:bg-emerald-400 text-slate-900 font-bold py-3 rounded-lg transition-all shadow-[0_0_15px_rgba(16,185,129,0.3)] hover:shadow-[0_0_25px_rgba(16,185,129,0.5)] flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Intercepting Signals...</span>
                </>
              ) : (
                <span>Execute Analysis</span>
              )}
            </button>
          </form>

          {error && (
            <div className="mt-5 p-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm rounded-lg font-medium">
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* PANEL DERECHO: VISUALIZADOR DE RESULTADOS ASÍNCRONOS */}
        <div className="lg:col-span-2">
          {loading ? (
            <div className="h-full flex flex-col items-center justify-center space-y-4 min-h-[400px] border border-slate-800/50 rounded-2xl bg-slate-800/20">
              <Activity className="w-12 h-12 text-emerald-400 animate-pulse" />
              <div className="space-y-1 text-center">
                <h3 className="text-lg font-medium text-slate-200">Orchestrating CrewAI Agents</h3>
                <p className="text-slate-400 text-sm animate-pulse">Llama 3 is analyzing web intelligence and extracting insights...</p>
              </div>
            </div>
          ) : result ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Tarjetas de Métricas */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-800/40 border border-slate-700 rounded-2xl p-6 relative overflow-hidden">
                  <p className="text-slate-400 text-sm mb-1 uppercase tracking-wide font-medium">Target Company</p>
                  <h3 className="text-2xl font-bold text-slate-100">{result.company_name}</h3>
                </div>
                <div className="bg-slate-800/40 border border-emerald-500/30 rounded-2xl p-6 relative overflow-hidden group">
                  <div className="absolute inset-0 bg-emerald-500/5 group-hover:bg-emerald-500/10 transition-colors"></div>
                  <p className="text-emerald-400/80 text-sm mb-1 font-mono uppercase font-semibold">Net New Lead Score</p>
                  <h3 className="text-4xl font-black text-emerald-400 drop-shadow-[0_0_12px_rgba(52,211,153,0.4)]">
                    {result.lead_score}<span className="text-2xl text-emerald-400/50">/100</span>
                  </h3>
                </div>
              </div>
              
              {/* Reporte Llama 3 */}
              <div className="bg-slate-800/40 border border-slate-700 rounded-2xl p-6 shadow-lg">
                <h3 className="text-lg font-medium mb-4 flex items-center space-x-2 text-slate-200 border-b border-slate-700/50 pb-3">
                  <ShieldCheck className="w-5 h-5 text-emerald-500" />
                  <span>Automated Intelligence Report</span>
                </h3>
                <div className="prose prose-invert prose-emerald max-w-none text-slate-300 leading-relaxed font-light mt-4">
                  <p>{result.intelligence_report}</p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center space-y-4 min-h-[400px] border border-dashed border-slate-700 rounded-2xl bg-slate-800/10 opacity-60">
              <ShieldCheck className="w-16 h-16 text-slate-600" />
              <p className="text-slate-500 font-medium">Waiting for target input to initialize Local Engine.</p>
            </div>
          )}
        </div>
        
      </main>
    </div>
  );
}
