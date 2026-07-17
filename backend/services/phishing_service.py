import re
from typing import Dict, Any, List

# Patterns matching social engineering tactics
URGENCY_KEYWORDS = {
    "urgente", "inmediatamente", "suspender", "bloqueada", "desactivada", "alerta",
    "atencion", "ultimo aviso", "plazo", "24 horas", "48 horas", "inmediato", "ahora mismo",
    "evitar", "multa", "penalidad", "accion requerida"
}

AUTHORITY_KEYWORDS = {
    "banco", "bank", "sat", "dian", "correo", "correos", "fedex", "dhl", "ups", "postal",
    "netflix", "spotify", "paypal", "apple", "support", "soporte", "gobierno", "seguridad",
    "policia", "hacienda", "visa", "mastercard", "bancolombia", "bbva", "santander"
}

FINANCIAL_KEYWORDS = {
    "premio", "ganador", "sorteo", "dinero", "reembolso", "transferencia", "deposito",
    "regalo", "gratis", "ganaste", "millones", "dolares", "pesos", "tarjeta", "efectivo"
}

class PhishingService:
    """
    Heuristic service for analyzing social engineering patterns in text.
    """

    @classmethod
    def analyze_text(cls, text: str) -> Dict[str, Any]:
        """
        Analyze a text string for social engineering and phishing signals.
        """
        if not text:
            return {
                "is_phishing": False,
                "confidence_score": 0.0,
                "urgency_detected": False,
                "authority_theft_detected": False,
                "financial_bait_detected": False,
                "phishing_techniques": [],
                "explanation": "No hay texto para analizar."
            }

        text_lower = text.lower()
        findings = []
        techniques = []
        risk_score = 0.0

        # 1. Check Urgency
        matched_urgency = [word for word in URGENCY_KEYWORDS if word in text_lower]
        urgency_detected = len(matched_urgency) > 0
        if urgency_detected:
            techniques.append("Urgencia artificial / Presión de tiempo")
            findings.append(f"Se detectó un tono de urgencia con palabras clave: {', '.join(matched_urgency)}.")
            risk_score += 30.0 + min(len(matched_urgency) * 5.0, 15.0)

        # 2. Check Authority Impersonation
        matched_authority = [word for word in AUTHORITY_KEYWORDS if word in text_lower]
        authority_theft_detected = len(matched_authority) > 0
        if authority_theft_detected:
            techniques.append("Suplantación de identidad / Autoridad")
            findings.append(f"Se mencionan entidades o servicios de confianza: {', '.join(matched_authority)}.")
            risk_score += 25.0 + min(len(matched_authority) * 5.0, 15.0)

        # 3. Check Financial Bait
        matched_financial = [word for word in FINANCIAL_KEYWORDS if word in text_lower]
        financial_bait_detected = len(matched_financial) > 0
        if financial_bait_detected:
            techniques.append("Cebo financiero / Oferta engañosa")
            findings.append(f"Se detectó lenguaje asociado a recompensas financieras o premios: {', '.join(matched_financial)}.")
            risk_score += 35.0 + min(len(matched_financial) * 5.0, 15.0)

        # 4. Check for hidden or raw URL-like patterns (e.g. "banco-login.com" without http)
        raw_url_pattern = r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,6}(?:/[^\s]*)?\b'
        raw_urls = re.findall(raw_url_pattern, text)
        # Filter out common punctuation mistakes or typical words
        cleaned_raw_urls = []
        for url in raw_urls:
            domain_part = url.split('/')[0].lower()
            # Make sure it's not a common floating number or standard word with dot
            if not re.match(r'^\d+\.\d+$', domain_part) and domain_part.count('.') == 1:
                cleaned_raw_urls.append(url)

        if cleaned_raw_urls:
            techniques.append("Enlaces sospechosos en texto plano")
            findings.append(f"Se encontraron posibles direcciones web o enlaces escritos en texto plano: {', '.join(cleaned_raw_urls)}.")
            risk_score += 20.0

        # Cap risk score at 100
        risk_score = min(risk_score, 100.0)
        is_phishing = risk_score >= 40.0

        # Construct basic explanation
        if is_phishing:
            explanation = (
                f"El texto presenta un alto índice de sospecha debido a la combinación de "
                f"{', '.join(techniques).lower()}. Las técnicas de ingeniería social intentan "
                "manipular las emociones del usuario (miedo, urgencia o avaricia) para que tome "
                "una decisión apresurada."
            )
        else:
            explanation = "El texto analizado no muestra patrones evidentes de ingeniería social o manipulación."

        return {
            "is_phishing": is_phishing,
            "confidence_score": risk_score,
            "urgency_detected": urgency_detected,
            "authority_theft_detected": authority_theft_detected,
            "financial_bait_detected": financial_bait_detected,
            "phishing_techniques": techniques,
            "findings": findings,
            "explanation": explanation
        }
