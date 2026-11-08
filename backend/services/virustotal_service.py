import os
import re
import base64
import logging
from typing import Dict, Any, List, Optional, Tuple
import httpx

logger = logging.getLogger("cyberguardian.virustotal")

# Regex para detección de hashes comunes
MD5_REGEX = re.compile(r'\b[a-fA-F0-9]{32}\b')
SHA1_REGEX = re.compile(r'\b[a-fA-F0-9]{40}\b')
SHA256_REGEX = re.compile(r'\b[a-fA-F0-9]{64}\b')


class VirusTotalService:
    """
    Servicio de integración con la API v3 de VirusTotal para análisis
    de reputación de URLs y hashes de archivos sospechosos.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = (api_key or os.getenv("VIRUSTOTAL_API_KEY", "")).strip()
        self.base_url = "https://www.virustotal.com/api/v3"
        self.timeout = 15.0

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    @staticmethod
    def extract_hashes(text: str) -> List[Dict[str, str]]:
        """
        Extrae hashes MD5, SHA-1 y SHA-256 presentes en un texto o mensaje.
        """
        if not text:
            return []

        results = []
        seen = set()

        # SHA-256 primero (longitud 64)
        for h in SHA256_REGEX.findall(text):
            h_lower = h.lower()
            if h_lower not in seen:
                seen.add(h_lower)
                results.append({"hash": h_lower, "type": "SHA-256"})

        # SHA-1 (longitud 40)
        for h in SHA1_REGEX.findall(text):
            h_lower = h.lower()
            if h_lower not in seen:
                seen.add(h_lower)
                results.append({"hash": h_lower, "type": "SHA-1"})

        # MD5 (longitud 32)
        for h in MD5_REGEX.findall(text):
            h_lower = h.lower()
            if h_lower not in seen:
                seen.add(h_lower)
                results.append({"hash": h_lower, "type": "MD5"})

        return results

    @staticmethod
    def calculate_risk(stats: Dict[str, int]) -> Tuple[float, str]:
        """
        Calcula la puntuación de riesgo (0.0 a 100.0) y nivel a partir
        de last_analysis_stats de VirusTotal.
        """
        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        undetected = stats.get("undetected", 0)
        total = malicious + suspicious + harmless + undetected

        if total == 0:
            return 0.0, "LOW"

        if malicious >= 3:
            # Riesgo crítico: 3 o más motores marcaron malicioso
            score = min(80.0 + (malicious * 2.0), 100.0)
            level = "CRITICAL"
        elif malicious >= 1 or suspicious >= 2:
            # Riesgo alto
            score = min(60.0 + (malicious * 10.0) + (suspicious * 5.0), 85.0)
            level = "HIGH"
        elif suspicious == 1:
            # Riesgo medio
            score = 35.0
            level = "MEDIUM"
        else:
            # Riesgo bajo (limpio o sin detecciones)
            score = 5.0
            level = "LOW"

        return round(score, 1), level

    def _headers(self) -> Dict[str, str]:
        return {
            "x-apikey": self.api_key,
            "accept": "application/json"
        }

    @staticmethod
    def url_to_id(url: str) -> str:
        """Genera el identificador base64 URL-safe sin padding para la API v3."""
        return base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    def _parse_vt_data(self, data: Dict[str, Any], target: str, target_type: str) -> Dict[str, Any]:
        """Estructura la información relevante de la respuesta v3 de VirusTotal."""
        attributes = data.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats", {})
        results = attributes.get("last_analysis_results", {})

        malicious = stats.get("malicious", 0)
        suspicious = stats.get("suspicious", 0)
        harmless = stats.get("harmless", 0)
        undetected = stats.get("undetected", 0)
        total_engines = malicious + suspicious + harmless + undetected

        risk_score, risk_level = self.calculate_risk(stats)

        # Extraer nombres de motores destacados que detectaron amenaza
        flagged_engines = []
        for engine, res in results.items():
            cat = res.get("category")
            if cat in ("malicious", "suspicious"):
                res_detail = res.get("result") or cat
                flagged_engines.append(f"{engine} ({res_detail})")

        findings = []
        if total_engines > 0:
            if malicious > 0 or suspicious > 0:
                findings.append(
                    f"VirusTotal: {malicious + suspicious}/{total_engines} motores de seguridad detectaron amenaza "
                    f"({malicious} maliciosos, {suspicious} sospechosos)."
                )
                if flagged_engines:
                    findings.append(f"Motores con detección: {', '.join(flagged_engines[:5])}.")
            else:
                findings.append(
                    f"VirusTotal: 0/{total_engines} detecciones. Ningún motor de seguridad catalogó el elemento como malicioso."
                )
        else:
            findings.append("VirusTotal: Sin historial de análisis previo disponible para este elemento.")

        return {
            "available": True,
            "status": "malicious" if (malicious > 0 or suspicious > 0) else "clean",
            "target": target,
            "target_type": target_type,
            "malicious": malicious,
            "suspicious": suspicious,
            "harmless": harmless,
            "undetected": undetected,
            "total_engines": total_engines,
            "detection_ratio": f"{malicious + suspicious}/{total_engines}" if total_engines > 0 else "0/0",
            "risk_score": risk_score,
            "risk_level": risk_level,
            "flagged_engines": flagged_engines,
            "findings": findings,
            "reputation": attributes.get("reputation", 0)
        }

    async def check_url_async(self, url: str) -> Dict[str, Any]:
        """
        Consulta asíncrona de la reputación de una URL en VirusTotal.
        Maneja errores HTTP (403, 404, 429, timeouts) de manera tolerante.
        """
        if not self.is_configured:
            logger.warning("VIRUSTOTAL_API_KEY no configurada. Omitiendo consulta externa a VirusTotal.")
            return {
                "available": False,
                "status": "unconfigured",
                "target": url,
                "target_type": "url",
                "risk_score": 0.0,
                "risk_level": "LOW",
                "findings": ["VirusTotal: No configurado (sin VIRUSTOTAL_API_KEY)."],
                "error": "VIRUSTOTAL_API_KEY no encontrada"
            }

        url_id = self.url_to_id(url)
        endpoint = f"{self.base_url}/urls/{url_id}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, headers=self._headers())

            if response.status_code == 200:
                return self._parse_vt_data(response.json(), target=url, target_type="url")
            elif response.status_code == 404:
                logger.info(f"URL no indexada en VirusTotal (HTTP 404): {url}")
                return {
                    "available": True,
                    "status": "not_found",
                    "target": url,
                    "target_type": "url",
                    "malicious": 0,
                    "suspicious": 0,
                    "total_engines": 0,
                    "detection_ratio": "0/0",
                    "risk_score": 10.0,
                    "risk_level": "LOW",
                    "findings": ["VirusTotal: La URL no tiene historial de análisis previo indexado."],
                    "flagged_engines": []
                }
            elif response.status_code == 403:
                logger.warning(f"VirusTotal HTTP 403 (Acceso denegado/geobloqueo o cuota agotada) para {url}")
                return {
                    "available": False,
                    "status": "forbidden",
                    "target": url,
                    "target_type": "url",
                    "risk_score": 0.0,
                    "risk_level": "LOW",
                    "findings": ["VirusTotal: Servicio no disponible temporalmente (HTTP 403 / Restricción de acceso)."],
                    "error": "HTTP 403 Forbidden / Geoblock / Quota"
                }
            else:
                logger.warning(f"Respuesta inesperada de VirusTotal (HTTP {response.status_code}) para {url}")
                return {
                    "available": False,
                    "status": "http_error",
                    "target": url,
                    "target_type": "url",
                    "risk_score": 0.0,
                    "risk_level": "LOW",
                    "findings": [f"VirusTotal: Error HTTP {response.status_code} al consultar reputación."],
                    "error": f"HTTP {response.status_code}"
                }

        except httpx.TimeoutException:
            logger.warning(f"Timeout al comunicarse con VirusTotal para {url}")
            return {
                "available": False,
                "status": "timeout",
                "target": url,
                "target_type": "url",
                "risk_score": 0.0,
                "risk_level": "LOW",
                "findings": ["VirusTotal: Tiempo de espera agotado al consultar la API."],
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Error de red o excepción al consultar VirusTotal: {e}")
            return {
                "available": False,
                "status": "error",
                "target": url,
                "target_type": "url",
                "risk_score": 0.0,
                "risk_level": "LOW",
                "findings": [f"VirusTotal: No fue posible contactar el servicio ({str(e)})."],
                "error": str(e)
            }

    async def check_file_hash_async(self, file_hash: str) -> Dict[str, Any]:
        """
        Consulta asíncrona de la reputación de un hash de archivo en VirusTotal.
        """
        if not self.is_configured:
            logger.warning("VIRUSTOTAL_API_KEY no configurada. Omitiendo consulta de hash en VirusTotal.")
            return {
                "available": False,
                "status": "unconfigured",
                "target": file_hash,
                "target_type": "hash",
                "risk_score": 0.0,
                "risk_level": "LOW",
                "findings": ["VirusTotal: No configurado (sin VIRUSTOTAL_API_KEY)."],
                "error": "VIRUSTOTAL_API_KEY no encontrada"
            }

        endpoint = f"{self.base_url}/files/{file_hash}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(endpoint, headers=self._headers())

            if response.status_code == 200:
                return self._parse_vt_data(response.json(), target=file_hash, target_type="hash")
            elif response.status_code == 404:
                logger.info(f"Hash no indexado en VirusTotal (HTTP 404): {file_hash}")
                return {
                    "available": True,
                    "status": "not_found",
                    "target": file_hash,
                    "target_type": "hash",
                    "malicious": 0,
                    "suspicious": 0,
                    "total_engines": 0,
                    "detection_ratio": "0/0",
                    "risk_score": 10.0,
                    "risk_level": "LOW",
                    "findings": ["VirusTotal: El hash del archivo no se encuentra catalogado en la base de datos."],
                    "flagged_engines": []
                }
            elif response.status_code == 403:
                logger.warning(f"VirusTotal HTTP 403 para hash {file_hash}")
                return {
                    "available": False,
                    "status": "forbidden",
                    "target": file_hash,
                    "target_type": "hash",
                    "risk_score": 0.0,
                    "risk_level": "LOW",
                    "findings": ["VirusTotal: Servicio no disponible temporalmente (HTTP 403)."],
                    "error": "HTTP 403 Forbidden"
                }
            else:
                return {
                    "available": False,
                    "status": "http_error",
                    "target": file_hash,
                    "target_type": "hash",
                    "risk_score": 0.0,
                    "risk_level": "LOW",
                    "findings": [f"VirusTotal: Error HTTP {response.status_code} al consultar hash."],
                    "error": f"HTTP {response.status_code}"
                }

        except httpx.TimeoutException:
            logger.warning(f"Timeout al comunicarse con VirusTotal para hash {file_hash}")
            return {
                "available": False,
                "status": "timeout",
                "target": file_hash,
                "target_type": "hash",
                "risk_score": 0.0,
                "risk_level": "LOW",
                "findings": ["VirusTotal: Tiempo de espera agotado al consultar hash."],
                "error": "Timeout"
            }
        except Exception as e:
            logger.error(f"Error al consultar hash en VirusTotal: {e}")
            return {
                "available": False,
                "status": "error",
                "target": file_hash,
                "target_type": "hash",
                "risk_score": 0.0,
                "risk_level": "LOW",
                "findings": [f"VirusTotal: No fue posible consultar el hash ({str(e)})."],
                "error": str(e)
            }
