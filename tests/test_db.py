import pytest
from sqlalchemy import inspect


def test_roi_record_has_indexes(db_models):
    """Verify ROIRecord has proper indexes for query performance"""
    import db.models as models

    inspector = inspect(models.engine)
    indexes = inspector.get_indexes('roi_records')
    index_names = [idx['name'] for idx in indexes]

    assert 'idx_session_frame' in index_names, "Missing composite index on session_id + frame_id"
    assert any('timestamp' in idx['name'] or 'session_id' in str(idx.get('column_names', []))
            for idx in indexes), "Missing timestamp or session_id index"


def test_roi_record_columns(db_models):
    """Verify ROIRecord has all required columns"""
    import db.models as models

    inspector = inspect(models.engine)
    columns = inspector.get_columns('roi_records')
    column_names = [col['name'] for col in columns]

    required = ['id', 'session_id', 'frame_id', 'bbox_x', 'bbox_y', 'bbox_w', 'bbox_h', 'confidence', 'timestamp']
    for col in required:
        assert col in column_names, f"Missing column: {col}"


def test_save_roi_returns_id(db_models):
    """Verify save_roi returns record ID"""
    from db.models import save_roi
    
    bbox = {'x': 10, 'y': 20, 'w': 100, 'h': 100, 'confidence': 0.95}
    record_id = save_roi("test-session", 1, bbox)
    
    assert record_id is not None
    assert isinstance(record_id, int)


def test_get_latest_roi(db_models):
    """Verify get_latest_roi returns most recent record"""
    from db.models import save_roi, get_latest_roi
    
    bbox1 = {'x': 10, 'y': 20, 'w': 100, 'h': 100, 'confidence': 0.95}
    bbox2 = {'x': 30, 'y': 40, 'w': 80, 'h': 80, 'confidence': 0.90}
    
    save_roi("test-session", 1, bbox1)
    save_roi("test-session", 2, bbox2)
    
    latest = get_latest_roi("test-session")
    assert latest is not None
    assert latest.frame_id == 2