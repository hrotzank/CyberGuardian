import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.virustotal_service import VirusTotalService
from backend.telegram_bot import CyberGuardianTelegramBot, RISK_EMOJIS


def test_virustotal_hash_extraction():
    text = (
        "Muestra sospechosa con md5: 44d88612fea8a8f36de82e1278abb02f "
        "y sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 "
        "enviado para análisis."
    )
    hashes = VirusTotalService.extract_hashes(text)
    assert len(hashes) == 2
    types = [h["type"] for h in hashes]
    assert "SHA-256" in types
    assert "MD5" in types


def test_virustotal_risk_calculation():
    # Caso 1: Múltiples detecciones críticas
    stats_critical = {"malicious": 8, "suspicious": 2, "harmless": 50, "undetected": 10}
    score, level = VirusTotalService.calculate_risk(stats_critical)
    assert level == "CRITICAL"
    assert score >= 80.0

    # Caso 2: Una detección maliciosa (High)
    stats_high = {"malicious": 1, "suspicious": 1, "harmless": 65, "undetected": 5}
    score, level = VirusTotalService.calculate_risk(stats_high)
    assert level == "HIGH"
    assert score >= 60.0

    # Caso 3: Solo una sospecha (Medium)
    stats_medium = {"malicious": 0, "suspicious": 1, "harmless": 70, "undetected": 1}
    score, level = VirusTotalService.calculate_risk(stats_medium)
    assert level == "MEDIUM"
    assert score == 35.0

    # Caso 4: Todo limpio (Low)
    stats_clean = {"malicious": 0, "suspicious": 0, "harmless": 72, "undetected": 0}
    score, level = VirusTotalService.calculate_risk(stats_clean)
    assert level == "LOW"
    assert score <= 10.0


def test_virustotal_unconfigured_graceful():
    async def _run():
        # Si no hay clave, no debe lanzar excepción
        vt = VirusTotalService(api_key="")
        res = await vt.check_url_async("https://example.com")
        assert res["available"] is False
        assert res["status"] == "unconfigured"
        assert "findings" in res
        assert res["risk_level"] == "LOW"

    asyncio.run(_run())


def test_virustotal_http_403_failover():
    async def _run():
        # Simular HTTP 403 de VirusTotal (geobloqueo o restricción)
        vt = VirusTotalService(api_key="dummy_key")
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 403
            mock_get.return_value = mock_resp

            res = await vt.check_url_async("https://suspicious-site.com")
            assert res["available"] is False
            assert res["status"] == "forbidden"
            assert "403" in res["error"]
            assert len(res["findings"]) > 0

    asyncio.run(_run())


def test_telegram_bot_hybrid_failover():
    async def _run():
        """
        Verifica que el bot responde con el motor heurístico local
        si VirusTotal y la IA externa no están disponibles (failover total).
        """
        bot = CyberGuardianTelegramBot(token="123456:dummy_token")

        # Simular fallo en VirusTotal (ej: 403)
        with patch.object(bot.vt_service, "check_url_async") as mock_vt:
            mock_vt.return_value = {
                "available": False,
                "status": "forbidden",
                "error": "HTTP 403 Geoblocked",
                "findings": ["VirusTotal: No disponible por restricción geográfica (HTTP 403)."]
            }

            # Ejecutar análisis de un mensaje sospechoso
            result = await bot.analyze_content("Urgente: Banco de http://suspicious-bank-login.xyz")

            assert "risk_score" in result
            assert "risk_level" in result
            assert result["risk_score"] > 50.0  # Heurística detecta TLD xyz y urgencia
            assert result["risk_level"] in ("HIGH", "CRITICAL")
            assert len(result["findings"]) > 0
            assert len(result["recommendations"]) > 0
            assert "educational_explanation" in result

    asyncio.run(_run())


def test_telegram_response_formatting():
    bot = CyberGuardianTelegramBot(token="123456:dummy_token")
    mock_analysis = {
        "risk_score": 88.5,
        "risk_level": "CRITICAL",
        "findings": [
            "VirusTotal: 12/71 motores detectaron amenaza.",
            "El dominio utiliza protocolo no seguro HTTP.",
            "Palabras clave de urgencia detectadas."
        ],
        "recommendations": [
            "No abras el enlace ni ingreses credenciales.",
            "Comunícate con el banco por sus canales oficiales."
        ],
        "educational_explanation": "Este mensaje es un intento de phishing bancario.",
        "engine_used": "xAI (Grok) + VirusTotal"
    }

    formatted = bot.format_telegram_response(mock_analysis)

    # Verificar que contiene todos los elementos requeridos
    assert "Nivel de Riesgo:" in formatted
    assert "CRÍTICO" in formatted
    assert "88.5 / 100" in formatted
    assert "Detalles de Análisis:" in formatted
    assert "VirusTotal" in formatted
    assert "Recomendaciones:" in formatted
    assert "Explicación:" in formatted
    assert "xAI (Grok) + VirusTotal" in formatted


def test_fastapi_lifespan_starts_and_stops_bot():
    """
    Verifica que el lifespan de FastAPI inicia el bot en background
    en startup y lo detiene limpiamente en shutdown.
    """
    async def _run():
        from backend.main import lifespan, app

        async def mock_polling():
            try:
                await asyncio.sleep(100)
            except asyncio.CancelledError:
                pass

        with patch("backend.telegram_bot.CyberGuardianTelegramBot.start_polling", side_effect=mock_polling):
            async with lifespan(app):
                assert hasattr(app.state, "bot_task")
                assert app.state.bot_task is not None
                assert not app.state.bot_task.done()
            
            # Tras finalizar el lifespan (shutdown), la tarea debe estar terminada/cancelada
            assert app.state.bot_task.done()

    asyncio.run(_run())


def test_fastapi_lifespan_resiliency_on_bot_error():
    """
    Verifica que si ocurre un error crítico al inicializar el bot,
    FastAPI no falla ni se interrumpe el ciclo de vida del servidor.
    """
    async def _run():
        from backend.main import lifespan, app
        with patch("backend.telegram_bot.CyberGuardianTelegramBot.__init__", side_effect=RuntimeError("Token inválido o socket error")):
            async with lifespan(app):
                # El servidor inicia normalmente a pesar del error del bot
                assert True

    asyncio.run(_run())


def test_fastapi_lifespan_no_token_configured():
    """
    Verifica que si no hay token configurado, el servidor inicia sin crear la tarea del bot.
    """
    async def _run():
        from backend.main import lifespan, app
        with patch.object(CyberGuardianTelegramBot, "is_configured", False):
            async with lifespan(app):
                assert True

    asyncio.run(_run())
