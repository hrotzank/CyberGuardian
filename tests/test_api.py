import sys
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup path for testing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app
from backend.database.connection import Base, get_db

# Create a temporary file database configuration specifically for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_temp.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Recreate all schemas in the test database, ensuring models are loaded
from backend.models.analysis import AnalysisRecord
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    """
    Override function injecting test database session.
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Bind dependency overrides
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_health_check_endpoint():
    """
    Verify GET /api/health returns HTTP 200 and indicates database connection.
    """
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
    assert "timestamp" in data

def test_analyze_endpoint_safe():
    """
    Verify POST /api/analyze handles safe messages with a LOW risk response.
    """
    payload = {
        "content": "Hola, este es un mensaje normal para saludar. Espero que todo esté bien.",
        "source": "web"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["risk_score"] < 30.0
    assert data["risk_level"] == "LOW"
    assert len(data["findings"]) > 0
    assert len(data["recommendations"]) > 0
    assert "educational_explanation" in data

def test_analyze_endpoint_phishing():
    """
    Verify POST /api/analyze correctly detects a critical risk phishing scenario.
    """
    payload = {
        "content": "Urgente: Banco informa que su cuenta fue desactivada. Ingrese a http://suspicious-bank-login.xyz para activarla inmediatamente.",
        "source": "whatsapp"
    }
    response = client.post("/api/analyze", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["risk_score"] >= 86.0
    assert data["risk_level"] == "CRITICAL"
    # Ensure warnings are listed
    assert len(data["findings"]) > 0
    assert any("lista negra" in f or "TLD" in f or "urgencia" in f or "suplantar" in f for f in data["findings"])
    # Ensure safety advice is present
    assert len(data["recommendations"]) > 0
    assert any("Banco" in r or "Urgencia" in r or "ingreses" in r for r in data["recommendations"])

def test_get_history_endpoint():
    """
    Verify GET /api/history returns a list of history items, which includes recent runs.
    """
    response = client.get("/api/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first_item = data[0]
    assert "id" in first_item
    assert "risk_score" in first_item
    assert "risk_level" in first_item
    assert "created_at" in first_item
    assert "findings" in first_item
    assert "source" in first_item
