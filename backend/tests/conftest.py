import pytest
import tempfile
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import app
from src.models.user import db, User
from src.models.task import Task

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    # Create a temporary database
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

@pytest.fixture
def auth_headers(client):
    """Create a test user and return auth headers."""
    # Create test user
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    # Register user
    response = client.post('/api/auth/register', json=user_data)
    assert response.status_code == 201
    
    data = response.get_json()
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def test_user(client):
    """Create and return a test user."""
    user = User(
        username='testuser2',
        email='test2@example.com',
        first_name='Test2',
        last_name='User2'
    )
    user.set_password('testpass123')
    
    db.session.add(user)
    db.session.commit()
    
    return user

@pytest.fixture
def test_task(client, test_user):
    """Create and return a test task."""
    from src.models.task import TaskStatus, TaskPriority
    
    task = Task(
        title='Test Task',
        description='This is a test task',
        status=TaskStatus.PENDING,
        priority=TaskPriority.MEDIUM,
        created_by=test_user.id
    )
    
    db.session.add(task)
    db.session.commit()
    
    return task

