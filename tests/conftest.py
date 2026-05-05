import pytest
import os
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def db_models():
    """Initialize test database"""
    from db.models import init_db, engine, Base
    
    # Use test database
    os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/looklive_test'
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)