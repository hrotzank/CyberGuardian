import re
from urllib.parse import urlparse
from typing import List, Dict, Any

# Common phishing keywords in URLs
PHISHING_KEYWORDS = {
    "login", "signin", "verify", "verificar", "banco", "bank", "secure", "safe", 
    "account", "cuenta", "update", "actualizar", "soporte", "support", "billing", 
    "paypal", "netflix", "visa", "mastercard", "apple", "google", "microsoft",
    "recuperar", "unlock", "bloqueada", "suspension", "reclamar", "premio", "free"
}

# High risk TLDs commonly used for malicious pages
SUSPICIOUS_TLDS = {
    "xyz", "top", "click", "club", "gq", "cf", "ml", "tk", "ga", "download", 
    "work", "date", "faith", "science", "party", "loan", "win", "bid", "vip"
}

# Regular expression to extract URLs from text
URL_REGEX = re.compile(
    r'https?://[^\s/$.?#].[^\s]*',
    re.IGNORECASE
)

class URLService:
    """
    Service to extract and structurally analyze URLs for security risks.
    """

    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract all URLs from a given text.
        """
        if not text:
            return []
        return [match.strip() for match in URL_REGEX.findall(text)] 

    @staticmethod
    def extract_domain(url: str) -> str:
        """
        Extract the domain name from a URL.
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.split(":")[0] if ":" in parsed.netloc else parsed.netloc
            return domain
        except Exception:
            return ""

    @staticmethod
    def analyze_url(url: str) -> Dict[str, Any]:
        """
        Perform structural analysis on a single URL and return security indicators.
        """
        findings = []
        risk_score = 0.0

        try:
            parsed = urlparse(url)
            domain = parsed.netloc.split(":")[0] if ":" in parsed.netloc else parsed.netloc
            path = parsed.path
            query = parsed.query
        except Exception as e:
            return {
                "url": url,
                "domain": "",
                "is_valid": False,
                "findings": [f"URL inválida o con formato incorrecto: {str(e)}"],
                "risk_score": 50.0
            }

        if not parsed.scheme or not parsed.netloc:
            return {
                "url": url,
                "domain": "",
                "is_valid": False,
                "findings": ["Estructura de URL incompleta (falta protocolo o dominio)."],
                "risk_score": 40.0
            }

        # 1. Check Protocol (HTTPS vs HTTP)
        is_https = parsed.scheme.lower() == "https"
        if not is_https:
            findings.append("La URL utiliza HTTP en lugar de HTTPS (conexión no cifrada).")
            risk_score += 25.0

        # 2. Check if host is an IP address (often used in phishing to hide domains)
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        is_ip = bool(re.match(ip_pattern, domain))
        if is_ip:
            findings.append("El host es una dirección IP directa, no un nombre de dominio (oculta la identidad).")
            risk_score += 40.0

        # 3. Check Subdomains (phishing often uses deep subdomains like login.paypal.com.suspicious.com)
        # Split by dots, ignoring empty elements
        subdomain_parts = [part for part in domain.split('.') if part]
        subdomain_count = len(subdomain_parts)
        if subdomain_count > 3 and not is_ip:
            findings.append(f"El dominio contiene demasiados subdominios ({subdomain_count}), lo que es común en fraudes.")
            risk_score += 15.0

        # 4. Check for Suspicious TLD
        tld = subdomain_parts[-1].lower() if subdomain_parts else ""
        if tld in SUSPICIOUS_TLDS:
            findings.append(f"El dominio utiliza un TLD de alto riesgo o bajo costo: '.{tld}'.")
            risk_score += 25.0

        # 5. Check for Phishing Keywords in domain, path, or query
        full_path_query = (domain + path + query).lower()
        matched_keywords = []
        for word in PHISHING_KEYWORDS:
            # Match keywords as sub-words
            if word in full_path_query:
                # If the domain is actually a legitimate site (e.g. apple.com), keywords might trigger false positives.
                # So we weight keyword occurrence depending on where it appears.
                matched_keywords.append(word)

        if matched_keywords:
            findings.append(f"La URL contiene palabras clave típicamente asociadas a phishing: {', '.join(matched_keywords)}.")
            risk_score += min(len(matched_keywords) * 15.0, 45.0)

        # 6. Check for typosquatting / homographs indicators (e.g. double dashes, numbers in brand names)
        if "-" in domain:
            # Phishing domains often use dashes to mimic brand names (e.g., netflix-login.com)
            findings.append("El dominio utiliza guiones (-), comúnmente empleado para suplantar marcas.")
            risk_score += 10.0

        # Cap structural risk score at 100.0
        risk_score = min(risk_score, 100.0)

        return {
            "url": url,
            "domain": domain,
            "is_valid": True,
            "is_https": is_https,
            "is_ip": is_ip,
            "subdomain_count": subdomain_count,
            "tld": tld,
            "matched_keywords": matched_keywords,
            "findings": findings,
            "risk_score": risk_score
        }
