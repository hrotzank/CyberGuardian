import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <h1 className="text-9xl font-black text-[#FF4D4D] mb-4 drop-shadow-[0_0_20px_rgba(255,77,77,0.5)]">404</h1>
      <h2 className="text-2xl font-bold text-gray-300 mb-8">Brecha detectada: La página no existe.</h2>
      <Link to="/" className="text-[#00AEEF] hover:text-[#F5F7FA] underline transition-colors">
        Volver al Centro de Mando
      </Link>
    </div>
  );
}