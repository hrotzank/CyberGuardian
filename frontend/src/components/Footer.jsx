import { NavLink } from 'react-router-dom'
import { Shield, Github, ExternalLink, Twitter } from 'lucide-react'

const QUICK_LINKS = [
  { to: '/', label: 'Inicio' },
  { to: '/analyze', label: 'Analizar' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/about', label: 'Acerca de' },
]

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="border-t border-cg-border-subtle bg-cg-panel/30 mt-20">
      <div className="cg-container py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">

          {/* ─── Brand ─── */}
          <div className="col-span-1">
            <NavLink to="/" className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 bg-cg-panel border border-cg-blue/30 rounded-lg flex items-center justify-center">
                <Shield className="w-4 h-4 text-cg-blue" strokeWidth={1.8} />
              </div>
              <span className="text-base font-bold">
                <span className="text-gradient-blue">Cyber</span>
                <span className="text-cg-text">Guardian</span>
              </span>
            </NavLink>
            <p className="text-cg-text-muted text-sm leading-relaxed max-w-xs">
              Plataforma anti-phishing y de concientización ciudadana con análisis multiagente de inteligencia artificial. Protegiendo a los usuarios de amenazas digitales.
            </p>

            <div className="flex items-center gap-3 mt-6">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-lg bg-cg-panel border border-cg-border-subtle flex items-center justify-center text-cg-text-muted hover:text-cg-blue hover:border-cg-border transition-all"
                aria-label="GitHub"
              >
                <Github className="w-4 h-4" />
              </a>
              <a
                href="https://twitter.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-lg bg-cg-panel border border-cg-border-subtle flex items-center justify-center text-cg-text-muted hover:text-cg-blue hover:border-cg-border transition-all"
                aria-label="Twitter"
              >
                <Twitter className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* ─── Quick Links ─── */}
          <div>
            <h3 className="text-xs font-semibold text-cg-text-muted uppercase tracking-widest mb-4">
              Navegación
            </h3>
            <ul className="space-y-2.5">
              {QUICK_LINKS.map((link) => (
                <li key={link.to}>
                  <NavLink
                    to={link.to}
                    className="text-sm text-cg-text-muted hover:text-cg-blue transition-colors flex items-center gap-1.5 group"
                  >
                    <span className="w-1 h-1 rounded-full bg-cg-blue/40 group-hover:bg-cg-blue transition-colors" />
                    {link.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>

          {/* ─── Technologies ─── */}
          <div>
            <h3 className="text-xs font-semibold text-cg-text-muted uppercase tracking-widest mb-4">
              Tecnologías
            </h3>
            <div className="flex flex-wrap gap-2">
              {['FastAPI', 'CrewAI', 'React', 'Gemini AI', 'SQLite', 'Python 3.14'].map((tech) => (
                <span
                  key={tech}
                  className="px-2.5 py-1 text-xs rounded-md bg-cg-panel border border-cg-border-subtle text-cg-text-muted"
                >
                  {tech}
                </span>
              ))}
            </div>
            <div className="mt-6">
              <p className="text-xs text-cg-text-muted mb-2">Estado del Sistema</p>
              <div className="flex items-center gap-2">
                <span className="cg-dot-live" />
                <span className="text-xs text-cg-green font-medium">Todos los sistemas operativos</span>
              </div>
            </div>
          </div>
        </div>

        {/* ─── Bottom Bar ─── */}
        <div className="cg-accent-line mt-10 mb-6" />
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-cg-text-muted">
          <p>© {year} CyberGuardian. Todos los derechos reservados.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              Construido con
              <span className="text-cg-red mx-0.5">♥</span>
              para la seguridad ciudadana
            </span>
          </div>
        </div>
      </div>
    </footer>
  )
}
