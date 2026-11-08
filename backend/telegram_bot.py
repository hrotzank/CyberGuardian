import os
import sys
import asyncio
import logging
import html
import hashlib
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import httpx

# Asegurar importación de backend desde la raíz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.agents.orchestrator import Orchestrator
from backend.services.url_service import URLService
from backend.services.report_service import ReportService
from backend.services.virustotal_service import VirusTotalService
from backend.database.connection import SessionLocal

load_dotenv()

logger = logging.getLogger("cyberguardian.telegram_bot")

# Nivel de riesgo traducido y con emojis
RISK_EMOJIS = {
    "CRITICAL": "🔴 CRÍTICO",
    "HIGH": "🟠 ALTO",
    "MEDIUM": "🟡 MEDIO",
    "LOW": "🟢 BAJO"
}

DANGEROUS_EXTENSIONS = {
    ".exe", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".wsf", 
    ".msi", ".jar", ".iso", ".dll", ".hta", ".apk", ".elf"
}


class CyberGuardianTelegramBot:
    """
    Bot asíncrono y desacoplado de Telegram para CyberGuardian.
    Integra VirusTotal v3, xAI/Groq con respaldo híbrido automático
    al motor heurístico local ante cualquier fallo de red o API externa.
    """

    def __init__(self, token: Optional[str] = None):
        self.token = (token or os.getenv("TELEGRAM_BOT_TOKEN", "")).strip()
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.orchestrator = Orchestrator()
        self.vt_service = VirusTotalService()
        self.is_running = False
        self._stop_event = asyncio.Event()

    @property
    def is_configured(self) -> bool:
        return bool(self.token)

    async def analyze_content(
        self, 
        content: str, 
        file_hash: Optional[str] = None, 
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Flujo de análisis híbrido con failover completo:
        1. Escaneo de URLs y Hashes con VirusTotal.
        2. Análisis de Inteligencia Artificial (xAI / Groq).
        3. Fallback inmediato al motor heurístico local si la IA o VirusTotal fallan (403, timeout, etc.).
        4. Síntesis y combinación de hallazgos.
        """
        urls = URLService.extract_urls(content)
        extracted_hashes = self.vt_service.extract_hashes(content)
        
        # Incorporar hash directo de archivo si existe
        all_hashes = [h["hash"] for h in extracted_hashes]
        if file_hash and file_hash.lower() not in all_hashes:
            all_hashes.append(file_hash.lower())

        vt_results: List[Dict[str, Any]] = []
        vt_available = False

        # --- 1. Consulta a VirusTotal (URLs y Hashes) ---
        if urls or all_hashes:
            logger.info(f"Objetivos detectados para VirusTotal: {len(urls)} URLs, {len(all_hashes)} Hashes.")
            
            # Consultar URLs en VT
            for u in urls[:3]:  # Límite preventivo de 3 URLs
                try:
                    vt_res = await self.vt_service.check_url_async(u)
                    vt_results.append(vt_res)
                    if vt_res.get("available") and vt_res.get("status") != "forbidden":
                        vt_available = True
                except Exception as vt_err:
                    logger.warning(f"Fallo al consultar VirusTotal para URL '{u}': {vt_err}")
                    vt_results.append({
                        "available": False,
                        "target": u,
                        "target_type": "url",
                        "status": "error",
                        "error": str(vt_err),
                        "findings": ["VirusTotal: No disponible temporalmente (Modo de respaldo local activado)."]
                    })

            # Consultar Hashes en VT
            for h in all_hashes[:3]:  # Límite preventivo de 3 hashes
                try:
                    vt_res = await self.vt_service.check_file_hash_async(h)
                    vt_results.append(vt_res)
                    if vt_res.get("available") and vt_res.get("status") != "forbidden":
                        vt_available = True
                except Exception as vt_err:
                    logger.warning(f"Fallo al consultar VirusTotal para hash '{h}': {vt_err}")
                    vt_results.append({
                        "available": False,
                        "target": h,
                        "target_type": "hash",
                        "status": "error",
                        "error": str(vt_err),
                        "findings": ["VirusTotal: No disponible temporalmente para este hash."]
                    })

        # --- 2. Análisis con IA u Orquestador (con Failover a Heurística) ---
        ai_result: Dict[str, Any] = {}
        engine_used = "Motor Heurístico Local (Respaldo CyberGuardian)"
        
        # Intentar persistencia en DB local si está disponible
        db = None
        try:
            db = SessionLocal()
        except Exception as db_err:
            logger.debug(f"DB local no disponible en sesión bot: {db_err}")

        try:
            # Invocar orquestador de manera asíncrona sin bloquear el event loop
            logger.info("Enviando contenido a Orchestrator...")
            ai_result = await asyncio.to_thread(
                self.orchestrator.analyze, 
                content=content or f"Archivo analizado: {file_name or 'desconocido'} (Hash: {file_hash})", 
                source="telegram", 
                db=db
            )
            
            # Identificar qué motor resolvió la respuesta
            if self.orchestrator.api_key:
                provider_label = "xAI (Grok)" if self.orchestrator.provider == "xai" else "Groq"
                engine_used = f"{provider_label} + VirusTotal" if vt_available else f"{provider_label} (Modo Heurístico Respaldo)"
            else:
                engine_used = "Motor Heurístico Local + VirusTotal" if vt_available else "Motor Heurístico Local"

        except Exception as ai_err:
            logger.error(f"Error en Orchestrator ({ai_err}). Activando respaldo heurístico local directo.")
            try:
                ai_result = await asyncio.to_thread(
                    self.orchestrator._run_heuristics, 
                    content=content, 
                    source="telegram", 
                    db=db
                )
                engine_used = "Motor Heurístico Local (Failover Directo)"
            except Exception as heur_err:
                logger.critical(f"Fallo crítico en motor heurístico: {heur_err}")
                ai_result = {
                    "risk_score": 50.0,
                    "risk_level": "MEDIUM",
                    "findings": [f"Se activó modo de emergencia por excepción: {str(heur_err)}"],
                    "recommendations": ["No abras enlaces ni descargues archivos adjuntos."],
                    "educational_explanation": "El sistema operó en modo de contingencia mínima."
                }
        finally:
            if db:
                try:
                    db.close()
                except Exception:
                    pass

        # --- 3. Integración Híbrida: VirusTotal + IA / Heurística ---
        findings = list(ai_result.get("findings", []))
        recommendations = list(ai_result.get("recommendations", []))
        final_score = float(ai_result.get("risk_score", 0.0))

        # Si se analizó un archivo con extensión peligrosa
        if file_name:
            ext = os.path.splitext(file_name)[1].lower()
            if ext in DANGEROUS_EXTENSIONS:
                findings.insert(0, f"Extensión de archivo de alto riesgo detectada: '{ext}' (potencial ejecutable/script malicioso).")
                final_score = max(final_score, 85.0)
                recommendations.insert(0, "¡CUIDADO! Nunca ejecutes archivos con extensiones ejecutables recibidos por mensajería.")

        # Añadir y consolidar métricas de VirusTotal
        vt_malicious_detected = False
        for vt in vt_results:
            if not vt.get("available"):
                # Aviso no bloqueante de indisponibilidad
                findings.append(f"Aviso VirusTotal ({vt.get('target', '')}): No disponible (403/timeout). Respaldo heurístico activo.")
                continue

            target_val = vt.get("target", "")
            mal = vt.get("malicious", 0)
            susp = vt.get("suspicious", 0)
            tot = vt.get("total_engines", 0)
            vt_score = vt.get("risk_score", 0.0)

            if mal > 0 or susp > 0:
                vt_malicious_detected = True
                findings.insert(0, f"VirusTotal [{target_val}]: {mal + susp}/{tot} motores de seguridad alertaron amenaza ({mal} maliciosos, {susp} sospechosos).")
                final_score = max(final_score, vt_score)
            elif tot > 0:
                findings.append(f"VirusTotal [{target_val}]: 0/{tot} detecciones (Limpio en motores de reputación).")

        # Recalcular nivel de riesgo consolidado
        final_score = min(max(round(final_score, 1), 0.0), 100.0)
        final_level = ReportService.map_risk_level(final_score)

        return {
            "risk_score": final_score,
            "risk_level": final_level,
            "findings": findings,
            "recommendations": recommendations,
            "educational_explanation": ai_result.get("educational_explanation", "Sin explicación disponible."),
            "engine_used": engine_used,
            "vt_results": vt_results
        }

    def format_telegram_response(self, analysis: Dict[str, Any]) -> str:
        """
        Diseña las respuestas del bot usando formato HTML limpio para Telegram:
        - 🛡️ Nivel de Riesgo
        - 📊 Puntuación de Seguridad
        - 🔍 Detalles de Análisis (VirusTotal + Reglas Heurísticas)
        - ⚠️ Recomendación
        - 📖 Explicación educativa
        """
        risk_level = analysis.get("risk_level", "LOW")
        risk_score = analysis.get("risk_score", 0.0)
        risk_badge = RISK_EMOJIS.get(risk_level, f"⚪ {risk_level}")
        engine = html.escape(analysis.get("engine_used", "CyberGuardian Core"))
        explanation = html.escape(analysis.get("educational_explanation", ""))

        # Sección de Hallazgos y Detalles
        findings = analysis.get("findings", [])
        findings_html = ""
        if findings:
            items = "\n".join([f"  • {html.escape(str(f))}" for f in findings[:6]])
            findings_html = f"\n\n<b>🔍 Detalles de Análisis:</b>\n{items}"

        # Sección de Recomendaciones
        recommendations = analysis.get("recommendations", [])
        recs_html = ""
        if recommendations:
            recs_items = "\n".join([f"  • {html.escape(str(r))}" for r in recommendations[:3]])
            recs_html = f"\n\n<b>⚠️ Recomendaciones:</b>\n{recs_items}"

        # Construcción del mensaje completo
        response = (
            f"🛡️ <b>REPORTE DE CIBERSEGURIDAD</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ <b>Nivel de Riesgo:</b> {risk_badge}\n"
            f"📊 <b>Puntuación de Seguridad:</b> <code>{risk_score} / 100</code>\n"
            f"⚙️ <b>Motor Activo:</b> <i>{engine}</i>"
            f"{findings_html}"
            f"{recs_html}\n\n"
            f"📖 <b>Explicación:</b>\n{explanation}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔒 <i>CyberGuardian SOC • Detección en Tiempo Real</i>"
        )
        return response

    async def _send_api_request(self, method: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Envía peticiones asíncronas a la API de Telegram con timeout."""
        url = f"{self.base_url}/{method}"
        try:
            async with httpx.AsyncClient(timeout=35.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    return res.json()
                logger.error(f"Error devuelto por Telegram API ({method}): HTTP {res.status_code} - {res.text}")
                return None
        except Exception as e:
            logger.error(f"Excepción en llamada a Telegram API ({method}): {e}")
            return None

    async def send_message(self, chat_id: int, text: str, parse_mode: str = "HTML") -> Optional[int]:
        """Envía un mensaje de texto al chat indicado y retorna su message_id."""
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        res = await self._send_api_request("sendMessage", payload)
        if res and res.get("ok"):
            return res.get("result", {}).get("message_id")
        return None

    async def edit_message(self, chat_id: int, message_id: int, text: str, parse_mode: str = "HTML") -> bool:
        """Edita un mensaje existente en Telegram."""
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        res = await self._send_api_request("editMessageText", payload)
        return bool(res and res.get("ok"))

    async def send_chat_action(self, chat_id: int, action: str = "typing"):
        """Envía un indicador de acción (ej: 'typing') para feedback visual."""
        await self._send_api_request("sendChatAction", {"chat_id": chat_id, "action": action})

    async def handle_start(self, chat_id: int):
        """Manejador para comando /start."""
        welcome = (
            "🛡️ <b>¡Bienvenido a CyberGuardian Bot!</b>\n\n"
            "Soy tu asistente de inteligencia de amenazas y prevención de phishing.\n\n"
            "<b>¿Qué puedes enviarme?</b>\n"
            "• 🔗 <b>URLs o enlaces:</b> Escaneo estructural y reputación en VirusTotal.\n"
            "• 📧 <b>Mensajes o correos:</b> Detección de ingeniería social con IA y reglas heurísticas.\n"
            "• 🏷️ <b>Hashes de archivos:</b> Verificación de malware (MD5, SHA-1, SHA-256).\n"
            "• 📁 <b>Documentos y archivos:</b> Análisis de extensión y hash en VirusTotal.\n\n"
            "Envía tu mensaje o enlace para comenzar."
        )
        await self.send_message(chat_id, welcome)

    async def handle_help(self, chat_id: int):
        """Manejador para comando /help."""
        help_msg = (
            "ℹ️ <b>Guía de Uso de CyberGuardian Bot</b>\n\n"
            "1. Copia y pega cualquier enlace o texto sospechoso directamente en este chat.\n"
            "2. El bot consultará VirusTotal y los motores de IA configurados.\n"
            "3. En caso de corte o bloqueo de APIs externas, el motor heurístico local responderá de inmediato.\n\n"
            "<i>Desarrollado para protección y concientización ciudadana.</i>"
        )
        await self.send_message(chat_id, help_msg)

    async def process_update(self, update: Dict[str, Any]):
        """Procesa una actualización individual recibida desde Telegram."""
        message = update.get("message")
        if not message:
            return

        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        document = message.get("document")
        photo = message.get("photo")

        if not chat_id:
            return

        # Comandos básicos
        if text.startswith("/start"):
            await self.handle_start(chat_id)
            return
        elif text.startswith("/help"):
            await self.handle_help(chat_id)
            return

        # Enviar indicador de procesamiento
        await self.send_chat_action(chat_id, "typing")
        processing_msg_id = await self.send_message(
            chat_id, 
            "🔍 <i>Analizando contenido con VirusTotal e Inteligencia Artificial...</i>"
        )

        content_to_analyze = text
        file_hash = None
        file_name = None

        # Si el usuario envió un documento adjunto
        if document:
            file_name = document.get("file_name", "archivo_adjunto")
            file_id = document.get("file_id")
            caption = message.get("caption", "")
            content_to_analyze = f"{caption} [Archivo: {file_name}]".strip()
            
            # Obtener hash del archivo si es posible mediante Telegram API
            try:
                file_info = await self._send_api_request("getFile", {"file_id": file_id})
                if file_info and file_info.get("ok"):
                    file_path = file_info.get("result", {}).get("file_path")
                    if file_path:
                        download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
                        async with httpx.AsyncClient(timeout=20.0) as client:
                            file_bytes = await client.get(download_url)
                            if file_bytes.status_code == 200:
                                file_hash = hashlib.sha256(file_bytes.content).hexdigest()
                                logger.info(f"Hash SHA-256 generado para {file_name}: {file_hash}")
            except Exception as dl_err:
                logger.warning(f"No fue posible descargar archivo para hash: {dl_err}")

        # Ejecutar análisis híbrido tolerante a fallos
        try:
            report_data = await self.analyze_content(
                content=content_to_analyze, 
                file_hash=file_hash, 
                file_name=file_name
            )
            response_html = self.format_telegram_response(report_data)

            if processing_msg_id:
                await self.edit_message(chat_id, processing_msg_id, response_html)
            else:
                await self.send_message(chat_id, response_html)

        except Exception as proc_err:
            logger.error(f"Error no controlado al procesar mensaje: {proc_err}", exc_info=True)
            error_fallback = (
                "⚠️ <b>Aviso de Seguridad CyberGuardian</b>\n\n"
                "Ocurrió una interrupción al contactar servicios externos. Se activó la regla preventiva:\n"
                "• Por precaución, <b>no abras enlaces</b> ni ingreses datos personales en este mensaje."
            )
            if processing_msg_id:
                await self.edit_message(chat_id, processing_msg_id, error_fallback)
            else:
                await self.send_message(chat_id, error_fallback)

    async def start_polling(self):
        """
        Ciclo asíncrono continuo de long-polling con Telegram API.
        No bloquea el hilo principal y admite detención limpia vía stop().
        """
        if not self.is_configured:
            logger.error("TELEGRAM_BOT_TOKEN no configurado en variables de entorno. El bot no puede iniciar.")
            return

        self.is_running = True
        self._stop_event.clear()
        offset = 0
        logger.info("🤖 CyberGuardian Telegram Bot iniciado en modo asíncrono (Long-Polling)...")

        async with httpx.AsyncClient(timeout=40.0) as client:
            while self.is_running and not self._stop_event.is_set():
                try:
                    url = f"{self.base_url}/getUpdates"
                    params = {"offset": offset, "timeout": 20}
                    response = await client.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        updates = data.get("result", [])
                        for update in updates:
                            update_id = update.get("update_id")
                            offset = max(offset, update_id + 1)
                            # Procesar cada update en una corrutina independiente para máxima concurrencia
                            asyncio.create_task(self.process_update(update))
                    elif response.status_code == 401:
                        logger.error("TELEGRAM_BOT_TOKEN inválido o revocado (HTTP 401 Unauthorized). Deteniendo sondeo del bot.")
                        break
                    elif response.status_code == 404:
                        logger.error("Endpoint del bot no encontrado (HTTP 404). Verifique TELEGRAM_BOT_TOKEN. Deteniendo sondeo.")
                        break
                    elif response.status_code == 409:
                        logger.warning("Conflicto con otra instancia de Telegram Bot (HTTP 409). Reintentando en 5s...")
                        await asyncio.sleep(5)
                    else:
                        logger.warning(f"getUpdates devolvió HTTP {response.status_code}. Pausa de 3s...")
                        await asyncio.sleep(3)

                except asyncio.CancelledError:
                    break
                except httpx.TimeoutException:
                    continue  # Timeout normal de long polling, continuar bucle
                except Exception as e:
                    logger.error(f"Error en ciclo de polling de Telegram: {e}")
                    await asyncio.sleep(3)

        self.is_running = False
        logger.info("Bot de Telegram detenido correctamente.")

    def stop(self):
        """Señaliza la detención limpia del bot."""
        self.is_running = False
        self._stop_event.set()


# Instancia singleton del bot para importación desacoplada
bot_instance = CyberGuardianTelegramBot()


async def run_telegram_bot():
    """Función de entrada para ejecutar el bot de Telegram de forma asíncrona."""
    bot = CyberGuardianTelegramBot()
    await bot.start_polling()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    try:
        asyncio.run(run_telegram_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot detenido por el usuario.")
