import { getRiskMeta, scoreToOffset } from '../utils/riskUtils'

/**
 * Circular SVG gauge showing the risk score (0–100)
 * @param {number} score
 * @param {string} level – LOW | MEDIUM | HIGH | CRITICAL
 * @param {number} size – svg size in px
 */
export default function RiskGauge({ score = 0, level = 'LOW', size = 140 }) {
  const { color, label } = getRiskMeta(level)
  const radius = 52
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (Math.min(score, 100) / 100) * circumference
  const cx = size / 2
  const cy = size / 2

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: size, height: size }}>
        {/* Glow ring */}
        <div
          className="absolute inset-0 rounded-full opacity-20 blur-xl"
          style={{ background: color }}
        />

        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="rotate-[-90deg]">
          {/* Track */}
          <circle
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={10}
          />
          {/* Progress */}
          <circle
            cx={cx} cy={cy} r={radius}
            fill="none"
            stroke={color}
            strokeWidth={10}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-bold text-cg-text" style={{ color }}>
            {Math.round(score)}
          </span>
          <span className="text-xs text-cg-text-muted font-medium">/ 100</span>
        </div>
      </div>

      <div
        className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border"
        style={{
          color,
          borderColor: `${color}40`,
          background: `${color}15`,
        }}
      >
        {label}
      </div>
    </div>
  )
}
