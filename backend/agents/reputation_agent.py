from pydantic import BaseModel, Field
from typing import List, Dict, Any

try:
    from crewai import Agent, Task
except Exception:
    Agent = Any  # type: ignore
    Task = Any  # type: ignore

class ReputationAgentOutput(BaseModel):
    """
    Structured output returned by the ReputationAgent task.
    """
    domains_evaluated: List[str] = Field(..., description="List of domains that were checked for reputation.")
    is_blacklisted: bool = Field(..., description="True if any domain is actively blacklisted in threat databases.")
    reputation_level: str = Field(..., description="Overall reputation level (e.g. whitelist, blacklist, unknown, suspicious).")
    reputation_risk_score: float = Field(..., description="Risk score from 0.0 (safe / whitelist) to 100.0 (blacklist) based on historical threat feeds.", ge=0.0, le=100.0)
    findings: List[str] = Field(..., description="Specific warning signals regarding domain reputation.")
    details: str = Field(..., description="Explanation of why this domain has this reputation status.")

def get_reputation_agent(llm) -> Agent:
    """
    Factory function to create a CrewAI Agent for domain reputation audits.
    """
    return Agent(
        role="Analista de Reputación e Inteligencia de Amenazas",
        goal="Verificar la reputación de los dominios y el contenido sospechoso en listas negras y bases de datos de amenazas conocidas.",
        backstory=(
            "Eres un experto en inteligencia de amenazas (Threat Intelligence). Tienes un conocimiento "
            "profundo sobre registros de dominios, bases de datos de spam y listas de phishing reportadas. "
            "Tu labor es auditar la identidad y reputación histórica de los servidores y dominios involucrados, "
            "identificando de inmediato si un sitio web ya ha sido catalogado como fraudulento por otros sistemas de seguridad."
        ),
        llm=llm,
        verbose=True
    )

def get_reputation_task(agent: Agent, content: str, url_findings: str) -> Task:
    """
    Factory function to create a CrewAI Task for auditing domain reputations based on URL findings.
    """
    return Task(
        description=(
            f"Determina la reputación de los dominios identificados en el siguiente análisis previo:\n"
            f"---\n"
            f"Contenido original: {content}\n"
            f"Análisis de URLs: {url_findings}\n"
            f"---\n"
            f"Pasos del análisis:\n"
            f"1. Extrae los dominios de los enlaces identificados.\n"
            f"2. Evalúa si pertenecen a servicios públicos legítimos (Google, Apple, Microsoft, etc.) o si son desconocidos.\n"
            f"3. Verifica si simulan marcas conocidas mediante nombres similares o TLDs raros.\n"
            f"4. Proporciona un veredicto estructurado sobre si están reportados o se consideran sospechosos de fraude."
        ),
        expected_output="Análisis de reputación estructurado detallando dominios evaluados, estatus de lista negra y riesgo reputacional.",
        agent=agent,
        output_pydantic=ReputationAgentOutput
    )
