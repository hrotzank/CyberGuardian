..33333

54
from pydantic import BaseModel, Field
from typing import List, Any

try:
    from crewai import Agent, Task
except Exception:
    Agent = Any  # type: ignore
    Task = Any  # type: ignore

class EducationAgentOutput(BaseModel):
    """
    Structured output returned by the EducationAgent task.
    """
    explanation: str = Field(..., description="A simple, human-friendly explanation explaining why this message is dangerous.")
    key_lessons: List[str] = Field(..., description="Key warning signs or red flags found in this specific message that users should learn to spot.")
    safety_tips: List[str] = Field(..., description="Actionable safety practices to prevent falling victim to similar attacks in the future.")

def get_education_agent(llm) -> Agent:
    """
    Factory function to create a CrewAI Agent for cybersecurity awareness.
    """
    return Agent(
        role="Educador y Concientizador de Ciberseguridad",
        goal="Traducir los hallazgos técnicos en explicaciones sencillas y educativas que ayuden a los ciudadanos a entender el peligro y evitar caer en trampas similares.",
        backstory=(
            "Eres un pedagogo de ciberseguridad dedicado a la alfabetización digital y concientización ciudadana. "
            "Tu misión es derribar la jerga técnica compleja para explicar, con un lenguaje empático, directo y comprensible, "
            "cómo funcionan las estafas digitales. Ayudas a los usuarios a entender el 'por qué' un mensaje es peligroso, "
            "enseñándoles a identificar las trampas emocionales (urgencia, codicia) y técnicas de los atacantes."
        ),
        llm=llm,
        verbose=True
    )

def get_education_task(agent: Agent, content: str, combined_findings: str) -> Task:
    """
    Factory function to create a CrewAI Task for explaining phishing threats in a plain, educational manner.
    """
    return Task(
        description=(
            f"Elabora una explicación educativa basada en el contenido original y en los hallazgos técnicos recopilados hasta el momento:\n"
            f"---\n"
            f"Contenido original: {content}\n"
            f"Hallazgos técnicos previos: {combined_findings}\n"
            f"---\n"
            f"Pautas de redacción:\n"
            f"1. Sé empático y claro, evita tecnicismos innecesarios o complicados.\n"
            f"2. Explica qué técnicas de manipulación se usaron en este caso.\n"
            f"3. Extrae lecciones clave de los errores en la URL o el texto que el usuario puede notar a simple vista.\n"
            f"4. Proporciona consejos prácticos de prevención."
        ),
        expected_output="Explicación educativa y lecciones de seguridad explicadas de manera sencilla.",
        agent=agent,
        output_pydantic=EducationAgentOutput
    )
