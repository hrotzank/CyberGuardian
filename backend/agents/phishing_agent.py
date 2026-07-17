from pydantic import BaseModel, Field
from typing import List, Any

try:
    from crewai import Agent, Task
except Exception:
    Agent = Any  # type: ignore
    Task = Any  # type: ignore

class PhishingAgentOutput(BaseModel):
    """
    Structured output returned by the PhishingAgent task.
    """
    is_phishing: bool = Field(..., description="True if the text content shows signs of phishing/social engineering.")
    confidence_score: float = Field(..., description="Phishing probability score from 0.0 (completely legitimate) to 100.0 (certain phishing).", ge=0.0, le=100.0)
    urgency_detected: bool = Field(..., description="True if language pressuring the user to act quickly is detected.")
    identity_theft_detected: bool = Field(..., description="True if the message attempts to impersonate an organization or trusted entity.")
    phishing_techniques: List[str] = Field(..., description="Social engineering techniques identified (e.g., sense of urgency, fear, authority, financial bait).")
    findings: List[str] = Field(..., description="Specific text indicators or warnings found during semantic analysis.")
    text_explanation: str = Field(..., description="Detailed semantic breakdown explaining the social engineering patterns found.")

def get_phishing_agent(llm) -> Agent:
    """
    Factory function to create a CrewAI Agent for semantic phishing detection.
    """
    return Agent(
        role="Analista de Phishing e Ingeniería Social",
        goal="Analizar el texto de un mensaje para detectar patrones de ingeniería social, urgencia artificial, amenazas o suplantación de identidad.",
        backstory=(
            "Eres un analista de ciberseguridad especializado en psicología del fraude. Tu habilidad es identificar "
            "técnicas de manipulación en mensajes de texto, correos o alertas de mensajería. Detectas el uso de "
            "presión psicológica, como falsas emergencias (bloqueo de cuentas, multas), ofertas financieras sospechosas, "
            "o el uso de marcas conocidas para generar una falsa sensación de confianza."
        ),
        llm=llm,
        verbose=True
    )

def get_phishing_task(agent: Agent, content: str) -> Task:
    """
    Factory function to create a CrewAI Task for analyzing phishing patterns in a message.
    """
    return Task(
        description=(
            f"Analiza semánticamente el siguiente contenido para evaluar si es un intento de phishing o ingeniería social:\n"
            f"---\n"
            f"{content}\n"
            f"---\n"
            f"Pasos del análisis:\n"
            f"1. Evalúa el tono general (¿genera miedo, codicia o urgencia?).\n"
            f"2. Identifica si intenta hacerse pasar por un banco, red social, servicio postal o entidad pública.\n"
            f"3. Revisa si solicita información sensible (claves, datos personales, números de tarjeta).\n"
            f"4. Clasifica las técnicas específicas utilizadas.\n"
            f"5. Calcula un nivel de sospecha (confidence_score) y justifica la respuesta."
        ),
        expected_output="Análisis semántico estructurado que indica probabilidad de phishing, técnicas usadas y desglose de sospechas.",
        agent=agent,
        output_pydantic=PhishingAgentOutput
    )
