from typing import List, Dict, Any, Tuple

class ReportService:
    """
    Service to compile and synthesize findings from multiple agents into a
    unified security report.
    """

    @staticmethod
    def map_risk_level(score: float) -> str:
        """
        Map a numerical risk score (0-100) to a qualitative risk level.
        """
        if score < 30.0:
            return "LOW"
        elif score < 60.0:
            return "MEDIUM"
        elif score < 86.0:
            return "HIGH"
        else:
            return "CRITICAL"

    @staticmethod
    def calculate_weighted_score(
        url_scores: List[float], 
        reputation_scores: List[float], 
        phishing_score: float
    ) -> float:
        """
        Calculate a weighted risk score based on components.
        - Reputation scores are critical (weight: 45%)
        - Phishing text analysis (weight: 35%)
        - URL structural heuristics (weight: 20%)
        """
        max_reputation = max(reputation_scores) if reputation_scores else 0.0
        max_url = max(url_scores) if url_scores else 0.0

        # If a domain is actively blacklisted (reputation score close to 95+), raise score directly
        if max_reputation >= 90.0:
            return max(max_reputation, phishing_score)

        weighted = (max_reputation * 0.45) + (phishing_score * 0.35) + (max_url * 0.20)
        return min(round(weighted, 1), 100.0)

    @classmethod
    def compile_heuristic_report(
        cls, 
        content: str, 
        url_analysis: List[Dict[str, Any]], 
        reputation_analysis: List[Dict[str, Any]], 
        phishing_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize heuristic checks into a structured response.
        Used as a primary fallback when CrewAI/LLM is disabled or fails.
        """
        findings = []
        recommendations = []

        url_scores = [item["risk_score"] for item in url_analysis]
        reputation_scores = [item["risk_score"] for item in reputation_analysis]
        phishing_score = phishing_analysis["confidence_score"]

        # Aggregate findings
        for item in url_analysis:
            findings.extend(item["findings"])
        for item in reputation_analysis:
            findings.extend(item["findings"])
        findings.extend(phishing_analysis["findings"])

        # Deduplicate and clean findings
        findings = list(dict.fromkeys(findings))
        if not findings:
            findings.append("No se detectaron indicadores evidentes de amenazas en el análisis estructural.")

        # Calculate final score and level
        risk_score = cls.calculate_weighted_score(url_scores, reputation_scores, phishing_score)
        risk_level = cls.map_risk_level(risk_score)

        # Generate recommendations based on findings
        any_http = any(not item.get("is_https", True) for item in url_analysis)
        any_blacklisted = any(item.get("is_blacklisted", False) for item in reputation_analysis)
        any_typo = any("-" in item.get("domain", "") for item in url_analysis)

        if any_blacklisted:
            recommendations.append("¡PELIGRO! El enlace está explícitamente reportado como malicioso. No hagas clic en él bajo ninguna circunstancia.")
        if any_http:
            recommendations.append("No ingreses credenciales, contraseñas ni datos bancarios en páginas web que no utilicen HTTPS.")
        if any_typo:
            recommendations.append("Verifica el nombre del dominio letra por letra. Los atacantes suelen usar dominios muy similares a las marcas oficiales (typosquatting) para engañarte.")
        if phishing_analysis.get("urgency_detected"):
            recommendations.append("Tómate tu tiempo. Las entidades legítimas y los bancos nunca te presionarán para actuar con urgencia bajo la amenaza de bloquear tus cuentas.")
        if phishing_analysis.get("financial_bait_detected"):
            recommendations.append("Desconfía de premios, subsidios o promociones de sorteos en los que no has participado voluntariamente.")
        if phishing_analysis.get("authority_theft_detected"):
            recommendations.append("Si tienes dudas de la veracidad del mensaje, contacta al canal oficial de soporte de la entidad suplantada por fuera de los medios provistos en este mensaje.")

        # Default general recommendations
        recommendations.append("No compartas ni reenvíes este mensaje a tus familiares o grupos de chat para evitar propagar el riesgo.")
        recommendations.append("Reporta el número o remitente como spam y elimina permanentemente el mensaje.")

        # Educational explanation
        if risk_score >= 60.0:
            educational_explanation = (
                "Este contenido presenta un nivel de riesgo crítico de phishing. El phishing es un engaño diseñado por cibercriminales "
                "que usan la manipulación psicológica (ingeniería social) y páginas web duplicadas para robar tus contraseñas, "
                "datos personales o dinero. En este caso específico, se han identificado patrones claros de manipulación o enlaces fraudulentos."
            )
        elif risk_score >= 30.0:
            educational_explanation = (
                "Se detectaron algunos elementos sospechosos que requieren precaución. Las campañas de fraude digital suelen mezclar enlaces "
                "nuevos o no catalogados con textos persuasivos. Te recomendamos no interactuar con el enlace y contrastar el mensaje directamente."
            )
        else:
            educational_explanation = (
                "El análisis indica que el riesgo es bajo. Sin embargo, recuerda que la ciberseguridad es una práctica constante: "
                "siempre verifica los remitentes oficiales y nunca compartas códigos de autenticación ni contraseñas."
            )

        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "findings": findings,
            "recommendations": recommendations,
            "educational_explanation": educational_explanation
        }
