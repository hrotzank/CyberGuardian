import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-6 text-center">
      <div className="max-w-3xl">
        <h1 className="text-5xl md:text-6xl font-extrabold mb-6 tracking-tight">
          Inteligencia Artificial para <span className="text-[#00AEEF]">Ciberseguridad</span>
        </h1>
        <p className="text-lg text-gray-400 mb-10 leading-relaxed">
          Analiza URLs, correos y mensajes sospechosos en segundos utilizando múltiples agentes de IA entrenados en inteligencia de amenazas.
        </p>
        <button 
          onClick={() => navigate('/analyze')}
          className="bg-[#00AEEF] hover:bg-[#008CBE] text-[#0A0F1C] font-bold py-3 px-8 rounded-lg shadow-[0_0_15px_rgba(0,174,239,0.4)] transition-all duration-300 transform hover:scale-105 cursor-pointer"
        >
          Comenzar Análisis
        </button>
      </div>
    </div>
  );
}