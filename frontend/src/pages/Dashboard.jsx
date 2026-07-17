import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import { 
  ShieldAlert, 
  ShieldCheck, 
  Activity, 
  AlertTriangle, 
  Loader2, 
  Clock, 
  Terminal, 
  ArrowRight,
  Database
} from 'lucide-react';
import axios from 'axios';
import { Link } from 'react-router-dom';

// Datos simulados para telemetría estilo Splunk/CrowdStrike (respaldo visual)
const threatData = [
  { time: '00:00', safe: 120, warning: 15, critical: 2 },
  { time: '04:00', safe: 85, warning: 22, critical: 5 },
  { time: '08:00', safe: 250, warning: 45, critical: 12 },
  { time: '12:00', safe: 380, warning: 80, critical: 25 },
  { time: '16:00', safe: 310, warning: 65, critical: 18 },
  { time: '20:00', safe: 190, warning: 30, critical: 8 },
  { time: '24:00', safe: 140, warning: 20, critical: 3 },
];

const vectorData = [
  { name: 'Phishing Email', value: 45 },
  { name: 'Malicious URL', value: 30 },
  { name: 'Social Engineering', value: 15 },
  { name: 'Suspicious File', value: 10 },
];

const COLORS = ['#00AEEF', '#FF4D4D', '#FFC857', '#00D26A'];

export default function Dashboard() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        // Consumir GET /api/history de forma directa
        const response = await axios.get('http://localhost:8000/api/history');
        setHistory(response.data);
      } catch (err) {
        console.error('Failed to load history:', err);
        let msg = 'Error al conectar con la base de datos de telemetría.';
        if (err.message && err.message.includes('Network Error')) {
          msg = 'Servidor de telemetría inalcanzable. Verifique que el backend FastAPI esté ejecutándose en http://localhost:8000.';
        }
        setError(msg);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  // Configuración de animaciones de Framer Motion
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  // Procesar métricas en tiempo real basadas en el historial
  const totalAnalyses = history.length;
  
  const averageRisk = totalAnalyses > 0 
    ? (history.reduce((sum, item) => sum + item.risk_score, 0) / totalAnalyses).toFixed(1) 
    : 0;

  const lowCount = history.filter(item => item.risk_level === 'LOW').length;
  const mediumCount = history.filter(item => item.risk_level === 'MEDIUM').length;
  const highCount = history.filter(item => item.risk_level === 'HIGH').length;
  const criticalCount = history.filter(item => item.risk_level === 'CRITICAL').length;

  const lastFiveAnalyses = history.slice(0, 5);

  const getRiskColor = (level) => {
    switch (level?.toUpperCase()) {
      case 'CRITICAL': return 'text-[#FF4D4D] bg-[#FF4D4D]/10 border-[#FF4D4D]/25';
      case 'HIGH': return 'text-[#FF4D4D] bg-[#FF4D4D]/10 border-[#FF4D4D]/25';
      case 'MEDIUM': return 'text-[#FFC857] bg-[#FFC857]/10 border-[#FFC857]/25';
      case 'LOW': return 'text-[#00D26A] bg-[#00D26A]/10 border-[#00D26A]/25';
      default: return 'text-gray-400 bg-gray-800/20 border-gray-700/30';
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 md:p-8 space-y-8">
      {/* Cabecera del SOC */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 border-b border-gray-800 pb-4">
        <div>
          <h2 className="text-3xl font-black tracking-tight text-[#F5F7FA] flex items-center gap-2">
            <Terminal className="text-[#00AEEF]" size={28} /> SOC Telemetry & Historial
          </h2>
          <p className="text-gray-400 text-sm mt-1">
            Monitoreo en tiempo real de amenazas y vectores analizados.
          </p>
        </div>
        <div className="flex items-center gap-2 bg-[#131B2E] border border-gray-800 px-3 py-1.5 rounded-full">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#00D26A] opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#00D26A]"></span>
          </span>
          <span className="text-[10px] text-[#00D26A] font-mono tracking-widest uppercase font-bold">SYSTEM ACTIVE</span>
        </div>
      </div>

      {/* Manejo de Estados de Carga y Error */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="text-[#00AEEF] animate-spin" size={40} />
          <p className="text-gray-400 text-sm font-mono">Cargando base de datos del SOC...</p>
        </div>
      ) : error ? (
        <div className="bg-[#FF4D4D]/10 border border-[#FF4D4D]/30 p-6 rounded-xl space-y-3 max-w-xl mx-auto shadow-2xl">
          <div className="flex items-center gap-2 text-[#FF4D4D] font-bold">
            <ShieldAlert size={20} />
            <span>Fallo de Conexión</span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">{error}</p>
          <div className="text-[10px] text-gray-500 font-mono">
            Asegúrese de levantar su backend FastAPI con `python backend/main.py`
          </div>
        </div>
      ) : totalAnalyses === 0 ? (
        /* Estado Vacío Elegante (Sin registros en db) */
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="backdrop-blur-md bg-[#131B2E]/40 border border-white/5 rounded-2xl p-10 md:p-16 text-center max-w-2xl mx-auto space-y-6 shadow-2xl relative overflow-hidden"
        >
          {/* Fondo Decorativo */}
          <div className="absolute inset-0 bg-gradient-to-b from-[#00AEEF]/5 to-transparent pointer-events-none" />
          
          <div className="p-4 bg-[#00AEEF]/10 rounded-full w-fit mx-auto border border-[#00AEEF]/20">
            <Database className="text-[#00AEEF]" size={40} />
          </div>
          
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-[#F5F7FA]">Historial del SOC Vacío</h3>
            <p className="text-sm text-gray-400 max-w-md mx-auto leading-relaxed">
              No se han encontrado registros en la base de datos local. La telemetría en tiempo real comenzará a poblarse una vez que realice su primer escaneo de seguridad.
            </p>
          </div>

          <div className="p-4 bg-[#1A2338]/50 rounded-xl border border-white/5 max-w-sm mx-auto text-xs text-gray-400 leading-relaxed">
            💡 <span className="font-semibold text-gray-300">Tip de Seguridad:</span> Pruebe copiando una URL sospechosa o mensaje de texto de prueba en nuestro módulo de análisis para activar las firmas heurísticas.
          </div>

          <Link 
            to="/analyze" 
            className="inline-flex items-center gap-2 bg-[#00AEEF] hover:bg-[#008CBE] text-[#0A0F1C] font-bold py-3 px-6 rounded-xl transition-all shadow-[0_0_15px_rgba(0,174,239,0.35)] cursor-pointer"
          >
            Realizar Primer Escaneo <ArrowRight size={16} />
          </Link>
        </motion.div>
      ) : (
        /* Estado Exitoso: Mostrar Estadísticas y Tabla */
        <div className="space-y-8">
          {/* Grid de 6 Tarjetas KPI Reales */}
          <motion.div 
            variants={containerVariants}
            initial="hidden"
            animate="show"
            className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4"
          >
            {[
              { title: 'Total Análisis', value: totalAnalyses, icon: Activity, color: 'text-[#00AEEF]', bg: 'bg-[#00AEEF]/5', border: 'border-[#00AEEF]/20' },
              { title: 'Riesgo Promedio', value: `${averageRisk}%`, icon: ShieldAlert, color: 'text-[#FFC857]', bg: 'bg-[#FFC857]/5', border: 'border-[#FFC857]/20' },
              { title: 'Riesgo Bajo', value: lowCount, icon: ShieldCheck, color: 'text-[#00D26A]', bg: 'bg-[#00D26A]/5', border: 'border-[#00D26A]/20' },
              { title: 'Riesgo Medio', value: mediumCount, icon: AlertTriangle, color: 'text-[#FFC857]', bg: 'bg-[#FFC857]/5', border: 'border-[#FFC857]/20' },
              { title: 'Riesgo Alto', value: highCount, icon: ShieldAlert, color: 'text-[#FF4D4D]', bg: 'bg-[#FF4D4D]/5', border: 'border-[#FF4D4D]/20' },
              { title: 'Riesgo Crítico', value: criticalCount, icon: AlertTriangle, color: 'text-[#FF4D4D] animate-pulse', bg: 'bg-[#FF4D4D]/10', border: 'border-[#FF4D4D]/30' }
            ].map((kpi, index) => (
              <motion.div 
                key={index} 
                variants={itemVariants}
                className={`backdrop-blur-md bg-[#131B2E]/60 p-4 rounded-xl border ${kpi.border} ${kpi.bg} shadow-md flex flex-col justify-between`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">{kpi.title}</span>
                  <kpi.icon className={kpi.color} size={16} />
                </div>
                <h4 className="text-2xl font-black text-white">{kpi.value}</h4>
              </motion.div>
            ))}
          </motion.div>

          {/* Tabla de los Últimos 5 Análisis */}
          <motion.div 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="backdrop-blur-md bg-[#131B2E]/60 border border-white/5 rounded-2xl p-6 shadow-xl space-y-4"
          >
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-widest flex items-center gap-2">
              <Clock size={16} className="text-[#00AEEF]"/> Historial de Últimos Escaneos
            </h3>
            
            <div className="overflow-x-auto w-full">
              <table className="w-full text-left border-collapse min-w-[600px]">
                <thead>
                  <tr className="border-b border-gray-800 text-[10px] text-gray-500 uppercase tracking-wider font-bold">
                    <th className="pb-3 pl-2">ID</th>
                    <th className="pb-3">Fecha</th>
                    <th className="pb-3">Canal</th>
                    <th className="pb-3">Nivel Riesgo</th>
                    <th className="pb-3">Puntaje</th>
                    <th className="pb-3 pr-2">Primer Hallazgo</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800/40 text-xs">
                  {lastFiveAnalyses.map((record) => {
                    const parsedFindings = parseList(record.findings);
                    const firstFinding = parsedFindings.length > 0 ? parsedFindings[0] : 'Sin hallazgos';
                    return (
                      <tr key={record.id} className="hover:bg-[#1A2540]/30 transition-colors">
                        <td className="py-3.5 pl-2 font-mono text-gray-500">#{record.id}</td>
                        <td className="py-3.5 text-gray-300">
                          {new Date(record.created_at).toLocaleString('es-CO', {
                            day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit'
                          })}
                        </td>
                        <td className="py-3.5">
                          <span className="bg-[#131B2E] border border-white/5 text-gray-400 font-mono text-[9px] px-2 py-0.5 rounded uppercase">
                            {record.source || 'web'}
                          </span>
                        </td>
                        <td className="py-3.5">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getRiskColor(record.risk_level)}`}>
                            {record.risk_level === 'LOW' && 'BAJO'}
                            {record.risk_level === 'MEDIUM' && 'MEDIO'}
                            {record.risk_level === 'HIGH' && 'ALTO'}
                            {record.risk_level === 'CRITICAL' && 'CRÍTICO'}
                          </span>
                        </td>
                        <td className="py-3.5 font-bold font-mono text-gray-200">
                          {record.risk_score.toFixed(1)}%
                        </td>
                        <td className="py-3.5 pr-2 text-gray-400 truncate max-w-xs">
                          {firstFinding}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      )}

      {/* Sección de Gráficos de Respaldo (mock data) */}
      <motion.div 
        variants={containerVariants}
        initial="hidden"
        animate="show"
        className="grid grid-cols-1 lg:grid-cols-3 gap-6"
      >
        {/* Gráfico Principal */}
        <motion.div variants={itemVariants} className="lg:col-span-2 backdrop-blur-md bg-[#131B2E]/60 p-6 rounded-lg border border-white/5 shadow-xl">
          <h3 className="text-sm font-semibold text-gray-300 mb-6 uppercase tracking-widest flex items-center gap-2">
            <Activity size={16} className="text-[#00AEEF]"/> Volumen de Tráfico Analizado (24h)
          </h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={threatData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF4D4D" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#FF4D4D" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorWarning" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FFC857" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#FFC857" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="time" stroke="#4B5563" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#4B5563" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0A0F1C', borderColor: '#1F2937', borderRadius: '8px' }}
                  itemStyle={{ fontSize: '14px', fontWeight: 'bold' }}
                />
                <Area type="monotone" dataKey="critical" stroke="#FF4D4D" fillOpacity={1} fill="url(#colorCritical)" />
                <Area type="monotone" dataKey="warning" stroke="#FFC857" fillOpacity={1} fill="url(#colorWarning)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Gráfico Secundario */}
        <motion.div variants={itemVariants} className="backdrop-blur-md bg-[#131B2E]/60 p-6 rounded-lg border border-white/5 shadow-xl">
          <h3 className="text-sm font-semibold text-gray-300 mb-6 uppercase tracking-widest flex items-center gap-2">
            <ShieldAlert size={16} className="text-[#FF4D4D]"/> Vectores de Amenaza
          </h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={vectorData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {vectorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0A0F1C', borderColor: '#1F2937', borderRadius: '8px', color: '#F5F7FA' }}
                  itemStyle={{ color: '#F5F7FA' }}
                />
                <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '12px', color: '#9CA3AF' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

// Función defensiva para prevenir fallos al renderizar arrays
function parseList(list) {
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
}