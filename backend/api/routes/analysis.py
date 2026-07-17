from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import logging

from backend.database.connection import get_db
from backend.api.schemas.analysis import AnalysisRequest, AnalysisResponse, HealthResponse, AnalysisHistoryItem
from backend.database.repository import AnalysisRepository
from backend.agents.orchestrator import Orchestrator

router = APIRouter()
logger = logging.getLogger("cyberguardian")
orchestrator = Orchestrator()

@router.post("/analyze", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
def analyze_content(request: AnalysisRequest, db: Session = Depends(get_db)):
    """
    Escanea el texto/URL, coordina los agentes de seguridad y 
    delega la persistencia al orquestador.
    """
    try:
        logger.info(f"Procesando solicitud de análisis desde '{request.source}'...")
        
        # El orquestador ahora recibe la sesión 'db'. 
        # Si la recibe, él mismo se encarga de guardar el historial en la DB.
        result = orchestrator.analyze(
            content=request.content, 
            source=request.source or "web", 
            db=db
        )
        
        # Como el orquestador ya guardó el registro, simplemente devolvemos el resultado
        # Nota: Asegúrate que 'result' tenga la estructura que espera tu AnalysisResponse
        return result
        
    except Exception as e:
        logger.error(f"Error en el endpoint de análisis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error durante el análisis de amenazas: {str(e)}"
        )

@router.get("/history", response_model=List[AnalysisHistoryItem])
def get_analysis_history(db: Session = Depends(get_db)):
    """
    Obtiene el historial de los análisis guardados en cyberguardian.db.
    Retorna los registros ordenados por fecha descendente, limitado a 100.
    """
    try:
        logger.info("Obteniendo historial de análisis para el Dashboard...")
        repo = AnalysisRepository(db)
        records = repo.get_recent_records(limit=100)
        return records
    except Exception as e:
        logger.error(f"Error al obtener el historial de análisis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al consultar el historial de análisis: {str(e)}"
        )

@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    """
    Verifica el estado de la API y la conectividad a la base de datos.
    """
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error(f"Error en verificación de salud de la BD: {str(e)}")
        db_status = "disconnected"
        
    return HealthResponse(
        status="ok",
        database=db_status
    )