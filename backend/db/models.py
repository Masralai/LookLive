import os
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Index, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/looklive")

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ROIRecord(Base):
    __tablename__ = "roi_records"
    __table_args__ = (
        Index('idx_session_frame', 'session_id', 'frame_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False, index=True)
    frame_id = Column(Integer, nullable=False, index=True)
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_w = Column(Integer)
    bbox_h = Column(Integer)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_roi(session_id: str, frame_id: int, bbox: dict):
    db = SessionLocal()
    try:
        record = ROIRecord(
            session_id=session_id,
            frame_id=frame_id,
            bbox_x=bbox.get('x'),
            bbox_y=bbox.get('y'),
            bbox_w=bbox.get('w'),
            bbox_h=bbox.get('h'),
            confidence=bbox.get('confidence')
        )
        db.add(record)
        db.commit()
        return record.id
    finally:
        db.close()

def get_latest_roi(session_id: str = None):
    db = SessionLocal()
    try:
        query = db.query(ROIRecord).order_by(ROIRecord.id.desc())
        if session_id:
            query = query.filter(ROIRecord.session_id == session_id)
        return query.first()
    finally:
        db.close()
