from typing import Dict, Any, List

# A curated local whitelist to prevent false positives on major trusted domains
TRUSTED_WHITELIST = {
    "google.com", "gmail.com", "microsoft.com", "outlook.com", "apple.com", 
    "icloud.com", "facebook.com", "instagram.com", "whatsapp.com", "telegram.org",
    "github.com", "linkedin.com", "twitter.com", "x.com", "amazon.com", 
    "netflix.com", "youtube.com", "wikipedia.org", "fastapi.tiangolo.com",
    "python.org", "pypi.org", "sqlite.org", "crew.ai"
}

# A curated list of known dummy/simulation malicious domains for testing
KNOWN_BLACKLIST = {
    "suspicious-bank-login.xyz", "banco-seguro-login.xyz", "verificar-cuenta-ahora.net",
    "soporte-netflix-update.club", "paypal-secure-check.top", "giftcard-gratis.click",
    "actualiza-tus-datos-ya.ru", "secure-login-portal.work", "facebook-recovery-tool.download"
}

class ReputationService:
    """
    Service to assess the reputation of domain names against whitelists, 
    blacklists, and known intelligence feeds.
    """

    @classmethod
    def check_domain_reputation(cls, domain: str) -> Dict[str, Any]:
        """
        Check the reputation of a domain name. 
        Supports resolving subdomains to check the root domain as well.
        """
        if not domain:
            return {
                "domain": "",
                "status": "unknown",
                "risk_score": 0.0,
                "findings": [],
                "is_whitelisted": False,
                "is_blacklisted": False
            }

        domain_lower = domain.lower()
        findings = []
        risk_score = 0.0
        status = "unknown"
        is_whitelisted = False
        is_blacklisted = False

        # 1. Helper to extract root domain (e.g. login.paypal.com -> paypal.com)
        parts = domain_lower.split('.')
        possible_domains = []
        # Generate domain and parent domains: [login.paypal.com, paypal.com]
        for i in range(len(parts)):
            sub_d = ".".join(parts[i:])
            if sub_d:
                possible_domains.append(sub_d)

        # 2. Check Whitelist
        for d in possible_domains:
            if d in TRUSTED_WHITELIST:
                is_whitelisted = True
                status = "safe"
                findings.append(f"El dominio '{d}' está en la lista blanca de dominios confiables.")
                return {
                    "domain": domain,
                    "status": "safe",
                    "risk_score": 0.0,
                    "findings": findings,
                    "is_whitelisted": True,
                    "is_blacklisted": False
                }

        # 3. Check Blacklist
        for d in possible_domains:
            if d in KNOWN_BLACKLIST:
                is_blacklisted = True
                status = "malicious"
                risk_score = 95.0
                findings.append(f"El dominio '{d}' se encuentra reportado activamente en la lista negra de CyberGuardian.")
                break

        if is_blacklisted:
            return {
                "domain": domain,
                "status": "malicious",
                "risk_score": risk_score,
                "findings": findings,
                "is_whitelisted": False,
                "is_blacklisted": True
            }

        # 4. Default Unknown reputation
        findings.append("El dominio no está listado en la base de datos de reputación local.")
        return {
            "domain": domain,
            "status": "unknown",
            "risk_score": 10.0,  # Small default risk score for unknown domains
            "findings": findings,
            "is_whitelisted": False,
            "is_blacklisted": False
        }
