import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Terminal, 
  ShieldCheck, 
  Cpu, 
  AlertTriangle, 
  Loader2, 
  CheckCircle2, 
  XCircle, 
  ChevronDown, 
  ChevronUp, 
  HelpCircle,
  FileCode,
  ShieldAlert
} from 'lucide-react';
import axios from 'axios';
import RiskGauge from '../components/RiskGauge';

const LOADING_STEPS = [
  'Analizando contenido...',
  'Evaluando URLs...',
  'Detectando ingeniería social...',
  'Generando recomendaciones...',
];

export default function Analyze() {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [showRaw, setShowRaw] = useState(false);

  // Cycle through loading messages
  useEffect(() => {
    let interval;
    if (loading) {
      setLoadingStep(0);
      interval = setInterval(() => {
        setLoadingStep((prev) => (prev < LOADING_STEPS.length - 1 ? prev + 1 : prev));
      }, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [loading]);

  // Función defensiva para prevenir fallos al renderizar arrays
  const parseList = (list) => {
    if (!list) return [];
    if (Array.isArray(list)) return list;
    if (typeof list === 'string') {
      try {
        const parsed = JSON.parse(list);
        if (Array.isArray(parsed)) return parsed;
        return [list];
      } catch (e) {
        console.warn('Failed to parse list from string:', list, e);
        return [list];
      }
    }
    return [];
  };

  const handleScan = async (e) => {
    e.preventDefault();
    if (!content.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Conexión nativa al endpoint absoluto del backend en el puerto 8000
      const response = await axios.post('http://localhost:8000/api/analyze', { content });
      setResult(response.data);
    } catch (err) {
      console.error('Analysis failed:', err);
      
      // Personalización de mensajes basados en errores comunes
      let errorMessage = 'Ocurrió un error inesperado al analizar el contenido.';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err.message && err.message.includes('Network Error')) {
        errorMessage = 'No se pudo conectar con el servidor. Verifique que el backend FastAPI esté ejecutándose en http://localhost:8000.';
      } else if (err.code === 'ECONNABORTED') {
        errorMessage = 'La solicitud tardó demasiado y superó el tiempo de espera máximo.';
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto p-4 md:p-8 space-y-8 min-h-screen">
      {/* Title Header */}
      <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h2 className="text-4xl font-extrabold text-cg-text mb-2 flex items-center gap-3">
          <Terminal className="text-cg-blue animate-pulse" /> Centro de Análisis de Amenazas
        </h2>
        <p className="text-cg-text-muted text-sm">
          Ingrese un texto, mensaje sospechoso o URL para que nuestra IA multiagente y reglas heurísticas escaneen en tiempo real vectores de phishing.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Input & Form Panel */}
        <div className="lg:col-span-2 space-y-6">
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="cg-card-glow p-6"
          >
            <form onSubmit={handleScan} className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="text-xs font-bold text-cg-text-muted uppercase tracking-widest block">
                  Vector de Entrada
                </label>
                {content.length > 0 && (
                  <span className="text-xs text-cg-text-muted font-mono">
                    {content.length} caracteres
                  </span>
                )}
              </div>

              <textarea 
                value={content}
                onChange={(e) => setContent(e.target.value)}
                disabled={loading}
                className="w-full h-64 bg-cg-bg text-cg-blue border border-cg-border-subtle rounded-xl p-4 focus:outline-none focus:border-cg-blue focus:ring-1 focus:ring-cg-blue/30 font-mono text-sm resize-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                placeholder="> Ingrese URL o texto del mensaje a analizar aquí... (Ej: '¡Ganaste un premio! Haz clic aquí http://link.xyz')"
              />
              
              <button 
                type="submit"
                disabled={loading || !content.trim()}
                className="w-full cg-btn-primary items-center justify-center py-3.5 gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 size={18} className="animate-spin text-cg-bg" />
                    <span>{LOADING_STEPS[loadingStep]}</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck size={18} />
                    <span>Iniciar Análisis de Seguridad</span>
                  </>
                )}
              </button>
            </form>
          </motion.div>

          {/* Inline Loading / Processing status */}
          <AnimatePresence>
            {loading && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="cg-card p-6 border-l-4 border-cg-blue flex items-center gap-4"
              >
                <div className="p-3 bg-cg-blue/10 rounded-xl">
                  <Cpu className="text-cg-blue animate-spin" size={24} />
                </div>
                <div className="space-y-1 flex-1">
                  <h4 className="text-sm font-semibold text-cg-text">Procesando solicitud</h4>
                  <p className="text-xs text-cg-text-muted">
                    Nuestros agentes de ciberseguridad están analizando los patrones y evaluando reputaciones.
                  </p>
                  <div className="flex gap-1.5 pt-2">
                    {LOADING_STEPS.map((step, idx) => (
                      <div 
                        key={idx}
                        className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                          idx <= loadingStep ? 'bg-cg-blue' : 'bg-cg-border-subtle'
                        }`}
                      />
                    ))}
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Alert Box */}
          <AnimatePresence>
            {error && (
              <motion.div 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="bg-cg-red/10 border border-cg-red/35 p-5 rounded-xl flex items-start gap-3"
              >
                <XCircle className="text-cg-red shrink-0 mt-0.5" size={20} />
                <div className="space-y-1">
                  <h4 className="text-sm font-bold text-cg-red">Fallo en la comunicación</h4>
                  <p className="text-xs text-cg-text/90 leading-relaxed">{error}</p>
                  <div className="pt-2 text-[10px] text-cg-text-muted">
                    Intente levantar el backend ejecutando <code className="bg-[#0A0F1C] px-1 py-0.5 rounded text-cg-red">python backend/main.py</code> en su terminal.
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results Panel */}
          <AnimatePresence>
            {result && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.4 }}
                className="space-y-6"
              >
                {/* Result Summary & Gauge */}
                <div className="cg-card p-6 grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
                  <div className="flex justify-center md:border-r border-cg-border-subtle pr-0 md:pr-6">
                    <RiskGauge score={result.risk_score} level={result.risk_level} />
                  </div>
                  
                  <div className="md:col-span-2 space-y-3">
                    <h3 className="text-lg font-bold text-cg-text flex items-center gap-2">
                      <ShieldAlert className="text-cg-blue" size={20} />
                      Evaluación General del Sistema
                    </h3>
                    <p className="text-sm text-cg-text-muted leading-relaxed">
                      El motor heurístico e inteligencia artificial de CyberGuardian han arrojado un nivel de riesgo{' '}
                      <span className="font-bold text-cg-text">
                        {result.risk_level === 'LOW' && 'Bajo'}
                        {result.risk_level === 'MEDIUM' && 'Medio'}
                        {result.risk_level === 'HIGH' && 'Alto'}
                        {result.risk_level === 'CRITICAL' && 'Crítico'}
                      </span>{' '}
                      con un puntaje de{' '}
                      <span className="font-bold text-cg-text">{result.risk_score} / 100</span>.
                    </p>
                    <div className="text-xs text-cg-text-muted font-mono flex items-center gap-2">
                      <span>Ref ID: #{result.id || 'N/A'}</span>
                      <span>•</span>
                      <span>Registrado: {result.created_at ? new Date(result.created_at).toLocaleString() : 'Reciente'}</span>
                    </div>
                  </div>
                </div>

                {/* Educational Explanation */}
                <div className="cg-card p-6 space-y-3">
                  <h4 className="text-sm font-bold text-cg-text uppercase tracking-wider flex items-center gap-2">
                    <HelpCircle size={16} className="text-cg-blue" />
                    Explicación de Seguridad
                  </h4>
                  <p className="text-sm text-cg-text/90 leading-relaxed font-sans">
                    {result.educational_explanation}
                  </p>
                </div>

                {/* Findings & Recommendations Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Findings */}
                  <div className="cg-card p-6 space-y-4">
                    <h4 className="text-sm font-bold text-cg-text uppercase tracking-wider flex items-center gap-2">
                      <AlertTriangle size={16} className="text-cg-yellow" />
                      Hallazgos Detectados ({parseList(result.findings).length})
                    </h4>
                    <ul className="space-y-2.5">
                      {parseList(result.findings).map((finding, idx) => (
                        <li key={idx} className="text-xs text-cg-text/90 leading-relaxed flex items-start gap-2">
                          <span className="text-cg-yellow select-none text-[10px] mt-0.5">⚠️</span>
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommendations */}
                  <div className="cg-card p-6 space-y-4">
                    <h4 className="text-sm font-bold text-cg-text uppercase tracking-wider flex items-center gap-2">
                      <CheckCircle2 size={16} className="text-cg-green" />
                      Recomendaciones ({parseList(result.recommendations).length})
                    </h4>
                    <ul className="space-y-2.5">
                      {parseList(result.recommendations).map((recommendation, idx) => (
                        <li key={idx} className="text-xs text-cg-text/90 leading-relaxed flex items-start gap-2">
                          <span className="text-cg-green select-none text-[10px] mt-0.5">✓</span>
                          <span>{recommendation}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Expandable Raw JSON API Response */}
                <div className="cg-card overflow-hidden">
                  <button 
                    type="button"
                    onClick={() => setShowRaw(!showRaw)}
                    className="w-full px-6 py-4 flex justify-between items-center text-sm font-bold text-cg-text-muted hover:text-cg-text transition-colors bg-cg-panel border-b border-cg-border-subtle cursor-pointer"
                  >
                    <span className="flex items-center gap-2">
                      <FileCode size={16} className="text-cg-blue" />
                      Respuesta Completa de la API (JSON)
                    </span>
                    {showRaw ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                  </button>
                  <AnimatePresence>
                    {showRaw && (
                      <motion.div 
                        initial={{ height: 0 }}
                        animate={{ height: 'auto' }}
                        exit={{ height: 0 }}
                        className="overflow-x-auto bg-[#070b14] p-4 border-t border-cg-border-subtle"
                      >
                        <pre className="font-mono text-xs text-cg-blue/90 leading-relaxed text-left">
                          {JSON.stringify(result, null, 2)}
                        </pre>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Info & Side Panel */}
        <div className="space-y-6">
          {/* Active Agents Info */}
          <div className="cg-card p-6 space-y-4">
            <h3 className="text-sm font-bold text-cg-text mb-4 flex items-center gap-2">
              <Cpu size={16} className="text-cg-green"/> 
              Estado de Agentes AI
            </h3>
            <div className="space-y-3">
              {[
                { name: 'PhishGuard AI', status: 'Online', desc: 'Detector de intenciones y urgencias' },
                { name: 'URL Scanner', status: 'Online', desc: 'Análisis de enlaces y DNS' },
                { name: 'Threat Reporter', status: loading ? 'Busy' : 'Online', desc: 'Sintetizador de reportes' }
              ].map((agent, i) => (
                <div key={i} className="bg-cg-bg/60 p-3 rounded-xl border border-cg-border-subtle space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-cg-text">{agent.name}</span>
                    <span className={`font-mono text-[10px] px-1.5 py-0.5 rounded ${
                      agent.status === 'Online' 
                        ? 'bg-cg-green/10 text-cg-green' 
                        : agent.status === 'Busy' 
                        ? 'bg-cg-yellow/10 text-cg-yellow animate-pulse' 
                        : 'bg-cg-text-muted/10 text-cg-text-muted'
                    }`}>
                      {agent.status}
                    </span>
                  </div>
                  <p className="text-[10px] text-cg-text-muted">{agent.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Quick instructions / tips */}
          <div className="cg-card p-6 space-y-3">
            <h3 className="text-sm font-bold text-cg-text flex items-center gap-2">
              <ShieldCheck size={16} className="text-cg-blue" />
              ¿Qué se analiza?
            </h3>
            <ul className="space-y-2 text-xs text-cg-text-muted">
              <li>• Enlaces HTTP vs HTTPS y certificados SSL.</li>
              <li>• Nombres de dominio sospechosos y marcas suplantadas.</li>
              <li>• Coincidencia en listas negras y de reputación.</li>
              <li>• Palabras clave de urgencia, premios falsos e ingeniería social.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}