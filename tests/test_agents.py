import pytest
from backend.services.url_service import URLService
from backend.services.reputation_service import ReputationService
from backend.services.phishing_service import PhishingService
from backend.services.report_service import ReportService
from backend.agents.orchestrator import Orchestrator

def test_url_extraction():
    text = "Hola, revisa este enlace: https://suspicious-bank-login.xyz/auth?user=test y también http://example.com"
    urls = URLService.extract_urls(text)
    assert len(urls) == 2
    assert "https://suspicious-bank-login.xyz/auth?user=test" in urls
    assert "http://example.com" in urls

def test_url_heuristics():
    # Dangerous TLD and keyword
    url = "https://verificar-banco.xyz/login"
    analysis = URLService.analyze_url(url)
    assert analysis["is_valid"] is True
    assert "xyz" in analysis["tld"]
    assert "login" in analysis["matched_keywords"]
    assert analysis["risk_score"] > 30.0

    # Safe HTTPS URL
    url_safe = "https://example.com"
    analysis_safe = URLService.analyze_url(url_safe)
    assert analysis_safe["risk_score"] < 10.0

def test_reputation_whitelist_blacklist():
    # Whitelist
    rep_safe = ReputationService.check_domain_reputation("google.com")
    assert rep_safe["status"] == "safe"
    assert rep_safe["risk_score"] == 0.0

    # Blacklist
    rep_malicious = ReputationService.check_domain_reputation("suspicious-bank-login.xyz")
    assert rep_malicious["status"] == "malicious"
    assert rep_malicious["risk_score"] == 95.0

def test_phishing_text_heuristics():
    # High urgency financial bait text
    text = "URGENTE: Su cuenta ha sido bloqueada. Ganaste un premio de 1000 USD, ingresa inmediatamente."
    analysis = PhishingService.analyze_text(text)
    assert analysis["is_phishing"] is True
    assert analysis["urgency_detected"] is True
    assert analysis["financial_bait_detected"] is True
    assert len(analysis["phishing_techniques"]) >= 2
    assert analysis["confidence_score"] > 50.0

def test_report_compilation():
    url_analyses = [URLService.analyze_url("https://banco-seguro-login.xyz/verificar")]
    rep_analyses = [ReputationService.check_domain_reputation("banco-seguro-login.xyz")]
    phishing_analysis = PhishingService.analyze_text("Urgente suplantacion de banco")

    report = ReportService.compile_heuristic_report(
        content="Mensaje urgente de banco-seguro-login.xyz",
        url_analysis=url_analyses,
        reputation_analysis=rep_analyses,
        phishing_analysis=phishing_analysis
    )

    assert report["risk_level"] == "CRITICAL"
    assert report["risk_score"] >= 86.0
    assert len(report["findings"]) > 0
    assert len(report["recommendations"]) > 0
    assert "HTTPS" in "".join(report["recommendations"]) or "banco" in "".join(report["findings"])

def test_orchestrator_heuristic_fallback():
    # Ensure orchestrator can run in heuristic fallback mode without LLM config
    orch = Orchestrator()
    result = orch.analyze("Mensaje sospechoso de urgencia del banco de http://suspicious-bank-login.xyz")
    assert "risk_score" in result
    assert "risk_level" in result
    assert "findings" in result
    assert "recommendations" in result
    assert "educational_explanation" in result
    assert result["risk_score"] > 50.0
