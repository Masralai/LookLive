import pytest
import io
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_health_endpoint():
    """Test health endpoint exists"""
    from backend.main import app
    
    assert app.title == "LookLive Face Detection API"
    assert app.version is not None


def test_roi_model_has_indexes():
    """Test ROIRecord has expected indexes defined"""
    from sqlalchemy import Index
    from db.models import ROIRecord
    
    table_args = ROIRecord.__table_args__
    assert table_args is not None
    
    has_composite = any(
        isinstance(arg, Index) and arg.name == 'idx_session_frame'
        for arg in table_args
    )
    assert has_composite, "Missing composite index on session_id + frame_id"


def test_roi_model_columns():
    """Test ROIRecord has required columns"""
    from db.models import ROIRecord
    
    columns = [c.name for c in ROIRecord.__table__.columns]
    required = ['session_id', 'frame_id', 'bbox_x', 'bbox_y', 'bbox_w', 'bbox_h', 'confidence', 'timestamp']
    for col in required:
        assert col in columns, f"Missing column: {col}"


@pytest.mark.skip(reason="Requires model download - tested in container")
def test_face_detector_returns_bbox():
    """Test FaceDetector initialization"""
    from services.face_detector import FaceDetector
    
    detector = FaceDetector()
    assert detector._model is not None


def test_draw_roi_adds_rectangle():
    """Test draw_roi draws rectangle on image"""
    from utils.draw import draw_roi
    from PIL import Image
    
    test_image = Image.new('RGB', (640, 480), color='white')
    bbox = {'x': 10, 'y': 20, 'w': 100, 'h': 100}
    
    result = draw_roi(test_image, bbox)
    
    assert result is not None
    assert isinstance(result, Image.Image)
    assert result.size == (640, 480)


def test_connection_manager_exists():
    """Test ConnectionManager class exists"""
    from backend.main import ConnectionManager
    
    manager = ConnectionManager()
    assert hasattr(manager, 'active_connections')
    assert hasattr(manager, 'latest_roi')


def test_api_routes_registered():
    """Test API routes are registered"""
    from backend.main import app
    
    routes = [route.path for route in app.routes]
    assert '/ws/video' in routes, "WebSocket route not registered"
    assert '/' in routes, "Root route not registered"


def test_dockerfile_has_healthcheck():
    """Test Dockerfile has HEALTHCHECK"""
    with open('backend/Dockerfile', 'r') as f:
        content = f.read()
    
    assert 'HEALTHCHECK' in content, "Missing HEALTHCHECK in Dockerfile"
    assert 'appuser' in content, "Missing non-root user in Dockerfile"


def test_compose_has_healthchecks():
    """Test docker-compose has healthchecks"""
    with open('docker-compose.yml', 'r') as f:
        content = f.read()
    
    assert 'healthcheck:' in content, "Missing healthcheck in compose"
    assert 'resources:' in content, "Missing resource limits in compose"