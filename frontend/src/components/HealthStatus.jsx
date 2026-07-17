import { motion } from 'framer-motion'
import { Wifi, WifiOff, RefreshCw, Clock } from 'lucide-react'
import { useHealthCheck } from '../hooks/useHealthCheck'

/**
 * System health status widget consumed from GET /api/health
 * @param {string} variant – 'compact' | 'full'
 */
export default function HealthStatus({ variant = 'full' }) {
  const { health, loading, isOnline, lastChecked, refetch } = useHealthCheck(30000)

  if (variant === 'compact') {
    return (
      <div className="flex items-center gap-2">
        {loading ? (
          <span className="w-2 h-2 rounded-full bg-cg-yellow animate-pulse" />
        ) : isOnline ? (
          <span className="cg-dot-live" />
        ) : (
          <span className="w-2 h-2 rounded-full bg-cg-red" />
        )}
        <span className={`text-xs font-medium ${isOnline ? 'text-cg-green' : 'text-cg-red'}`}>
          {loading ? 'Verificando…' : isOnline ? 'Sistema Online' : 'Sistema Offline'}
        </span>
      </div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="cg-card p-5 border border-cg-border-subtle"
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
            loading ? 'bg-cg-yellow/10' : isOnline ? 'bg-cg-green/10' : 'bg-cg-red/10'
          }`}>
            {loading ? (
              <RefreshCw className="w-4 h-4 text-cg-yellow animate-spin" />
            ) : isOnline ? (
              <Wifi className="w-4 h-4 text-cg-green" />
            ) : (
              <WifiOff className="w-4 h-4 text-cg-red" />
            )}
          </div>
          <div>
            <p className="text-xs text-cg-text-muted font-medium uppercase tracking-wide">Estado del Sistema</p>
            <p className={`text-sm font-bold ${
              loading ? 'text-cg-yellow' : isOnline ? 'text-cg-green' : 'text-cg-red'
            }`}>
              {loading ? 'Verificando…' : isOnline ? 'Operativo' : 'Fuera de línea'}
            </p>
          </div>
        </div>

        <button
          onClick={refetch}
          className="w-7 h-7 rounded-lg bg-cg-panel-light hover:bg-cg-border-subtle flex items-center justify-center text-cg-text-muted hover:text-cg-blue transition-all"
          title="Actualizar"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-2.5">
        <StatusRow label="API Backend" value={isOnline ? 'Conectado' : 'Desconectado'} ok={isOnline} loading={loading} />
        <StatusRow label="Base de Datos" value={health?.database === 'connected' ? 'Conectada' : 'Desconectada'} ok={health?.database === 'connected'} loading={loading} />
      </div>

      {lastChecked && (
        <div className="flex items-center gap-1.5 mt-4 text-cg-text-muted">
          <Clock className="w-3 h-3" />
          <span className="text-xs">
            Verificado: {lastChecked.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
          </span>
        </div>
      )}
    </motion.div>
  )
}

function StatusRow({ label, value, ok, loading }) {
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-cg-border-subtle last:border-0">
      <span className="text-xs text-cg-text-muted">{label}</span>
      <div className="flex items-center gap-1.5">
        {loading ? (
          <span className="w-1.5 h-1.5 rounded-full bg-cg-yellow animate-pulse" />
        ) : (
          <span className={`w-1.5 h-1.5 rounded-full ${ok ? 'bg-cg-green' : 'bg-cg-red'}`} />
        )}
        <span className={`text-xs font-medium ${ok ? 'text-cg-green' : 'text-cg-text-muted'}`}>
          {value}
        </span>
      </div>
    </div>
  )
}
