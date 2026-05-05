from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/looklive")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ROIRecord(Base):
    __tablename__ = "roi_records"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), nullable=False)
    frame_id = Column(Integer, nullable=False)
    bbox_x = Column(Integer)
    bbox_y = Column(Integer)
    bbox_w = Column(Integer)
    bbox_h = Column(Integer)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

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