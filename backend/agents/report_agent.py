from pydantic import BaseModel, Field
from typing import List, Any

try:
    from crewai import Agent, Task
except Exception:
    Agent = Any  # type: ignore
    Task = Any  # type: ignore

class ReportAgentOutput(BaseModel):
    """
    Structured output returned by the ReportAgent task.
    Matches the required final schema of the application.
    """
    risk_score: float = Field(..., description="Calculated final risk score from 0.0 (safe) to 100.0 (highly dangerous).", ge=0.0, le=100.0)
    risk_level: str = Field(..., description="Qualitative risk level corresponding to the score: LOW, MEDIUM, HIGH, CRITICAL.")
    findings: List[str] = Field(..., description="Deduplicated and compiled list of threat indicators identified.")
    recommendations: List[str] = Field(..., description="Actionable safety recommendations for the user.")
    educational_explanation: str = Field(..., description="Human-friendly explanation that teaches the user how to avoid these risks.")

def get_report_agent(llm) -> Agent:
    """
    Factory function to create a CrewAI Agent for consolidating safety reports.
    """
    return Agent(
        role="Auditor y Consolidador de Reportes de Seguridad",
        goal="Consolidar todos los análisis previos (URL, Phishing, Reputación, Educación) y generar un reporte final estructurado con un nivel de riesgo preciso y recomendaciones claras.",
        backstory=(
            "Eres un auditor y oficial de seguridad senior. Tu trabajo consiste en revisar de manera objetiva "
            "toda la evidencia técnica y educativa generada por los demás agentes. Syntetizas los hallazgos, "
            "formulas recomendaciones específicas y ponderas matemáticamente el nivel de riesgo en una escala "
            "del 0 al 100, asignando el nivel de riesgo correcto (LOW, MEDIUM, HIGH, CRITICAL)."
        ),
        llm=llm,
        verbose=True
    )

def get_report_task(
    agent: Agent, 
    content: str, 
    url_findings: str, 
    phishing_findings: str, 
    reputation_findings: str, 
    education_findings: str
) -> Task:
    """
    Factory function to create a CrewAI Task for synthesizing all component findings.
    """
    return Task(
        description=(
            f"Consolida los análisis de ciberseguridad sobre el siguiente contenido:\n"
            f"---\n"
            f"Contenido original: {content}\n"
            f"---\n"
            f"Evidencia recolectada por los analistas:\n"
            f"1. Análisis de URLs estructurales: {url_findings}\n"
            f"2. Análisis de Phishing de texto: {phishing_findings}\n"
            f"3. Análisis de Reputación de dominios: {reputation_findings}\n"
            f"4. Explicación Educativa y concientización: {education_findings}\n"
            f"---\n"
            f"Requisitos del informe:\n"
            f"1. Consolida una lista clara y sin duplicados de los hallazgos encontrados (findings).\n"
            f"2. Genera recomendaciones útiles y viables de seguridad (recommendations).\n"
            f"3. Escribe una explicación concientizadora (educational_explanation) adaptada a la estafa analizada.\n"
            f"4. Calcula una puntuación de riesgo global (risk_score) y asocia su nivel de riesgo (risk_level):\n"
            f"   - 0.0 - 29.9 -> LOW\n"
            f"   - 30.0 - 59.9 -> MEDIUM\n"
            f"   - 60.0 - 85.0 -> HIGH\n"
            f"   - 86.0 - 100.0 -> CRITICAL"
        ),
        expected_output="Informe final de seguridad estructurado que cumple exactamente con el esquema Pydantic de salida.",
        agent=agent,
        output_pydantic=ReportAgentOutput
    )
