from sqlalchemy.orm import Session

class AnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_record(self, data: dict):
        """Crea y guarda un nuevo registro de análisis."""
        from backend.models.analysis import AnalysisRecord
        record = AnalysisRecord(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_record_by_id(self, record_id: int):
        """Obtiene un registro por su ID."""
        from backend.models.analysis import AnalysisRecord
        return self.db.query(AnalysisRecord).filter(AnalysisRecord.id == record_id).first()

    def get_recent_records(self, limit: int = 10):
        """Obtiene los últimos análisis realizados."""
        from backend.models.analysis import AnalysisRecord
        return self.db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(limit).all()