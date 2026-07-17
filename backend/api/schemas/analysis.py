from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, timezone
import json

class AnalysisRequest(BaseModel):
    """
    Pydantic schema representing the user's scan request.
    """
    content: str = Field(
        ...,
        description="The URL or text content to analyze.",
        min_length=1,
        examples=["https://suspicious-bank-login.xyz/auth", "Urgente: actualice sus datos en 24 horas."]
    )
    source: Optional[str] = Field(
        "web",
        description="The source channel of the request (e.g. web, telegram, whatsapp).",
        examples=["telegram"]
    )

class AnalysisResponse(BaseModel):
    """
    Pydantic schema representing the complete threat analysis report returned to the client.
    """
    id: Optional[int] = Field(None, description="The ID of the saved record in the database.")
    risk_score: float = Field(..., description="Calculated risk score from 0.0 (safe) to 100.0 (dangerous).", ge=0.0, le=100.0)
    risk_level: str = Field(..., description="Qualitative risk level: LOW, MEDIUM, HIGH, CRITICAL.")
    findings: List[str] = Field(..., description="List of threat indicators or signs of phishing found.")
    recommendations: List[str] = Field(..., description="Actionable safety tips to protect the user.")
    educational_explanation: str = Field(..., description="Accessible explanation raising user awareness.")
    created_at: Optional[datetime] = Field(None, description="Timestamp of when the analysis was created.")

    model_config = {
        "from_attributes": True
    }

class HealthResponse(BaseModel):
    """
    Pydantic schema representing API and database health status.
    """
    status: str = Field(..., examples=["ok"])
    database: str = Field(..., examples=["connected"])
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AnalysisHistoryItem(BaseModel):
    """
    Pydantic schema for items returned by the GET /api/history endpoint.
    """
    id: int
    risk_score: float
    risk_level: str
    created_at: datetime
    findings: Optional[List[str]] = None
    source: Optional[str] = "web"

    @field_validator("findings", mode="before")
    @classmethod
    def parse_findings(cls, v):
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [v]
            except Exception:
                return [v]
        return v

    model_config = {
        "from_attributes": True
    }

