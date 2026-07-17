/**
 * Mock data for Dashboard charts and statistics
 * Realistic cybersecurity operations data
 */

export const MOCK_STATS = {
  totalAnalyses: 18742,
  threatsDetected: 9431,
  usersProtected: 5280,
  domainsAnalyzed: 23190,
}

export const MOCK_RISK_DISTRIBUTION = [
  { name: 'Crítico', value: 18, fill: '#FF4D4D' },
  { name: 'Alto', value: 27, fill: '#FF8C00' },
  { name: 'Medio', value: 31, fill: '#FFC857' },
  { name: 'Bajo', value: 24, fill: '#00D26A' },
]

export const MOCK_TREND_DATA = [
  { date: 'Ene', threats: 320, analyses: 640, safe: 320 },
  { date: 'Feb', threats: 450, analyses: 820, safe: 370 },
  { date: 'Mar', threats: 380, analyses: 750, safe: 370 },
  { date: 'Abr', threats: 520, analyses: 940, safe: 420 },
  { date: 'May', threats: 610, analyses: 1100, safe: 490 },
  { date: 'Jun', threats: 480, analyses: 980, safe: 500 },
  { date: 'Jul', threats: 720, analyses: 1350, safe: 630 },
  { date: 'Ago', threats: 650, analyses: 1200, safe: 550 },
  { date: 'Sep', threats: 800, analyses: 1480, safe: 680 },
  { date: 'Oct', threats: 940, analyses: 1700, safe: 760 },
  { date: 'Nov', threats: 870, analyses: 1580, safe: 710 },
  { date: 'Dic', threats: 1050, analyses: 1920, safe: 870 },
]

export const MOCK_BAR_DATA = [
  { day: 'Lun', phishing: 42, malware: 18, spam: 63 },
  { day: 'Mar', phishing: 67, malware: 24, spam: 48 },
  { day: 'Mié', phishing: 53, malware: 31, spam: 72 },
  { day: 'Jue', phishing: 89, malware: 19, spam: 55 },
  { day: 'Vie', phishing: 74, malware: 42, spam: 81 },
  { day: 'Sáb', phishing: 28, malware: 12, spam: 34 },
  { day: 'Dom', phishing: 19, malware: 8, spam: 22 },
]

export const MOCK_HISTORY = [
  {
    id: 1,
    content: 'https://banco-login-seguro.xyz/verificar',
    risk_level: 'CRITICAL',
    risk_score: 94.5,
    source: 'web',
    created_at: new Date(Date.now() - 120000).toISOString(),
  },
  {
    id: 2,
    content: 'Urgente: su cuenta ha sido suspendida. Haga clic aquí.',
    risk_level: 'HIGH',
    risk_score: 78.2,
    source: 'telegram',
    created_at: new Date(Date.now() - 3600000).toISOString(),
  },
  {
    id: 3,
    content: 'Hola, te envío el informe de la reunión de ayer.',
    risk_level: 'LOW',
    risk_score: 4.1,
    source: 'web',
    created_at: new Date(Date.now() - 7200000).toISOString(),
  },
  {
    id: 4,
    content: 'http://paypal-verify-account.top/login',
    risk_level: 'CRITICAL',
    risk_score: 97.8,
    source: 'whatsapp',
    created_at: new Date(Date.now() - 86400000).toISOString(),
  },
  {
    id: 5,
    content: 'Oferta exclusiva: gana $5000 respondiendo esta encuesta.',
    risk_level: 'MEDIUM',
    risk_score: 47.3,
    source: 'web',
    created_at: new Date(Date.now() - 172800000).toISOString(),
  },
]
