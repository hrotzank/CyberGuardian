from pydantic import BaseModel, Field
from typing import List, Any

try:
    from crewai import Agent, Task
except Exception:
    Agent = Any  # type: ignore
    Task = Any  # type: ignore

class URLAgentOutput(BaseModel):
    """
    Structured output returned by the URLAgent task.
    """
    has_urls: bool = Field(..., description="True if any URLs were found in the text, False otherwise.")
    urls_analyzed: List[str] = Field(..., description="List of all URLs extracted and analyzed.")
    suspicious_indicators: List[str] = Field(..., description="Specific warning signs detected in the URL structures.")
    structural_risk_score: float = Field(..., description="Risk score from 0.0 (perfectly safe) to 100.0 (highly dangerous) based on URL structure.", ge=0.0, le=100.0)

def get_url_agent(llm) -> Agent:
    """
    Factory function to create a CrewAI Agent for URL structural analysis.
    """
    return Agent(
        role="Especialista en Análisis de Enlaces y URLs",
        goal="Extraer y analizar todas las URLs en un mensaje para verificar su estructura, dominios engañosos y configuraciones sospechosas.",
        backstory=(
            "Eres un analista de seguridad web experto en diseccionar URLs. Identificas subdominios "
            "engañosos, caracteres homógrafos (ataques IDN), acortadores de URL y redirecciones sospechosas. "
            "Tu especialidad es determinar si un enlace imita la estructura de marcas legítimas o si "
            "oculta su destino para engañar al usuario."
        ),
        llm=llm,
        verbose=True
    )

def get_url_task(agent: Agent, content: str) -> Task:
    """
    Factory function to create a CrewAI Task for analyzing URLs in a message.
    """
    return Task(
        description=(
            f"Analiza detalladamente el siguiente contenido para extraer y evaluar cualquier enlace o dirección web (URL):\n"
            f"---\n"
            f"{content}\n"
            f"---\n"
            f"Pasos del análisis:\n"
            f"1. Identifica y extrae todas las URLs.\n"
            f"2. Verifica si el protocolo es inseguro (HTTP vs HTTPS).\n"
            f"3. Revisa si se emplean IPs directas en lugar de nombres de dominio.\n"
            f"4. Evalúa la complejidad del dominio (número de subdominios, uso de guiones para imitar marcas).\n"
            f"5. Detecta TLDs sospechosos (ej. .xyz, .top, .club, .ru).\n"
            f"6. Identifica palabras clave típicas de fraude (ej. login, verificar, cuenta, actualizar) en la URL."
        ),
        expected_output="Análisis estructurado con URLs analizadas, indicadores sospechosos y puntaje de riesgo estructural.",
        agent=agent,
        output_pydantic=URLAgentOutput
    )
