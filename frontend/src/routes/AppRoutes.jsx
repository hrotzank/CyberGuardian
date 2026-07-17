import { Routes, Route } from 'react-router-dom'
import MainLayout from '../layouts/MainLayout.jsx'
import Home from '../pages/Home.jsx'
import Analyze from '../pages/Analyze.jsx'
import Dashboard from '../pages/Dashboard.jsx'
import About from '../pages/About.jsx'
// Si no tienes una página NotFound creada, puedes borrar la línea de abajo y su ruta
import NotFound from '../pages/NotFound.jsx'

export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/about" element={<About />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}