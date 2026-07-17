import { useState, useEffect } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, Menu, X, ChevronRight } from 'lucide-react'

const NAV_LINKS = [
  { to: '/',          label: 'Inicio' },
  { to: '/analyze',   label: 'Analizar' },
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/about',     label: 'Acerca de' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  // Close mobile menu on route change
  useEffect(() => { setMobileOpen(false) }, [location])

  // Scrolled state for frosted-glass effect
  useEffect(() => {
    const handler = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])

  return (
    <>
      <motion.header
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? 'bg-cg-bg/90 backdrop-blur-md border-b border-cg-border-subtle shadow-lg'
            : 'bg-transparent'
        }`}
      >
        <div className="cg-container">
          <div className="flex items-center justify-between h-16 lg:h-18">

            {/* ─── Logo ─── */}
            <NavLink to="/" className="flex items-center gap-2.5 group">
              <div className="relative w-9 h-9">
                <div className="absolute inset-0 bg-cg-blue rounded-lg opacity-20 group-hover:opacity-40 transition-opacity blur-sm" />
                <div className="relative w-9 h-9 bg-cg-panel border border-cg-blue/30 rounded-lg flex items-center justify-center">
                  <Shield className="w-5 h-5 text-cg-blue" strokeWidth={1.8} />
                </div>
              </div>
              <span className="text-lg font-bold tracking-tight">
                <span className="text-gradient-blue">Cyber</span>
                <span className="text-cg-text">Guardian</span>
              </span>
            </NavLink>

            {/* ─── Desktop Nav ─── */}
            <nav className="hidden md:flex items-center gap-1">
              {NAV_LINKS.map((link) => (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.to === '/'}
                  className={({ isActive }) =>
                    `relative px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive
                        ? 'text-cg-blue bg-cg-blue/8'
                        : 'text-cg-text-muted hover:text-cg-text hover:bg-white/4'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {link.label}
                      {isActive && (
                        <motion.span
                          layoutId="nav-indicator"
                          className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-cg-blue rounded-full"
                        />
                      )}
                    </>
                  )}
                </NavLink>
              ))}
            </nav>

            {/* ─── Desktop CTA ─── */}
            <div className="hidden md:flex items-center gap-3">
              <NavLink to="/analyze" className="cg-btn-primary text-xs px-4 py-2">
                <ChevronRight className="w-3.5 h-3.5" />
                Analizar Ahora
              </NavLink>
            </div>

            {/* ─── Mobile Hamburger ─── */}
            <button
              onClick={() => setMobileOpen((v) => !v)}
              className="md:hidden w-9 h-9 flex items-center justify-center rounded-lg text-cg-text-muted hover:text-cg-text hover:bg-cg-panel-light transition-all"
              aria-label="Menú"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </motion.header>

      {/* ─── Mobile Menu Overlay ─── */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            key="mobile-menu"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-x-0 top-16 z-40 md:hidden bg-cg-bg/97 backdrop-blur-md border-b border-cg-border-subtle"
          >
            <nav className="cg-container py-4 flex flex-col gap-1">
              {NAV_LINKS.map((link, i) => (
                <motion.div
                  key={link.to}
                  initial={{ opacity: 0, x: -16 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                >
                  <NavLink
                    to={link.to}
                    end={link.to === '/'}
                    className={({ isActive }) =>
                      `flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                        isActive
                          ? 'text-cg-blue bg-cg-blue/10 border border-cg-blue/20'
                          : 'text-cg-text-muted hover:text-cg-text hover:bg-cg-panel'
                      }`
                    }
                  >
                    {link.label}
                    <ChevronRight className="w-4 h-4 opacity-40" />
                  </NavLink>
                </motion.div>
              ))}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.35 }}
                className="pt-2"
              >
                <NavLink to="/analyze" className="cg-btn-primary w-full justify-center">
                  Analizar Ahora
                </NavLink>
              </motion.div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Spacer for fixed header */}
      <div className="h-16 lg:h-18" />
    </>
  )
}
