import { useState, useEffect } from 'react';
import { Outlet, Link } from 'react-router-dom';
import { Menu, X, Shield, Activity, BarChart2, Info } from 'lucide-react';

export default function MainLayout() {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Efecto para detectar scroll y cambiar el estilo del Navbar
  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 50);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-[#0A0F1C] text-[#F5F7FA] font-sans transition-colors duration-300">
      {/* Navbar con efecto Glassmorphism Sticky */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 border-b ${isScrolled ? 'bg-[#0A0F1C]/90 backdrop-blur-lg border-[#00AEEF]/30 py-3' : 'bg-transparent border-transparent py-5'}`}>
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Shield className="text-[#00AEEF]" size={28} />
            <span className="text-xl font-black tracking-tighter text-[#F5F7FA]">CyberGuardian</span>
          </div>

          {/* Menú Desktop */}
          <div className="hidden md:flex gap-8 font-medium text-sm text-gray-400">
            <Link to="/" className="hover:text-[#00AEEF] transition-colors flex items-center gap-2"><Activity size={16}/>Inicio</Link>
            <Link to="/analyze" className="hover:text-[#00AEEF] transition-colors flex items-center gap-2"><Shield size={16}/>Analizar</Link>
            <Link to="/dashboard" className="hover:text-[#00AEEF] transition-colors flex items-center gap-2"><BarChart2 size={16}/>Dashboard</Link>
            <Link to="/about" className="hover:text-[#00AEEF] transition-colors flex items-center gap-2"><Info size={16}/>Info</Link>
          </div>

          {/* Botón Hamburguesa */}
          <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Menú Mobile */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed top-20 left-0 w-full bg-[#131B2E] p-6 z-40 border-b border-[#00AEEF]/20">
          <div className="flex flex-col gap-4">
            <Link to="/" onClick={() => setMobileMenuOpen(false)}>Inicio</Link>
            <Link to="/analyze" onClick={() => setMobileMenuOpen(false)}>Analizar</Link>
            <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)}>Dashboard</Link>
          </div>
        </div>
      )}

      <main className="pt-24 pb-12 px-6">
        <Outlet />
      </main>
    </div>
  );
}