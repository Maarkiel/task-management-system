import pytest
import json

def test_register_success(client):
    """Test successful user registration."""
    user_data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User'
    }
    
    response = client.post('/api/auth/register', json=user_data)
    data = response.get_json()
    
    assert response.status_code == 201
    assert 'access_token' in data
    assert data['user']['username'] == 'newuser'
    assert data['user']['email'] == 'newuser@example.com'
    assert 'password' not in data['user']

def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    # First registration
    response1 = client.post('/api/auth/register', json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same username
    user_data['email'] = 'different@example.com'
    response2 = client.post('/api/auth/register', json=user_data)
    data = response2.get_json()
    
    assert response2.status_code == 400
    assert 'Username already exists' in data['error']

def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    user_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }
    
    # First registration
    response1 = client.post('/api/auth/register', json=user_data)
    assert response1.status_code == 201
    
    # Second registration with same email
    user_data['username'] = 'differentuser'
    response2 = client.post('/api/auth/register', json=user_data)
    data = response2.get_json()
    
    assert response2.status_code == 400
    assert 'Email already exists' in data['error']

def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    user_data = {
        'username': 'testuser'
        # Missing email and password
    }
    
    response = client.post('/api/auth/register', json=user_data)
    data = response.get_json()
    
    assert response.status_code == 400
    assert 'required' in data['error']

def test_login_success(client):
    """Test successful login."""
    # First register a user
    user_data = {
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'password123'
    }
    client.post('/api/auth/register', json=user_data)
    
    # Then login
    login_data = {
        'username': 'loginuser',
        'password': 'password123'
    }
    
    response = client.post('/api/auth/login', json=login_data)
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'access_token' in data
    assert data['user']['username'] == 'loginuser'

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    login_data = {
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }
    
    response = client.post('/api/auth/login', json=login_data)
    data = response.get_json()
    
    assert response.status_code == 401
    assert 'Invalid username or password' in data['error']

def test_login_missing_fields(client):
    """Test login with missing fields."""
    login_data = {
        'username': 'testuser'
        # Missing password
    }
    
    response = client.post('/api/auth/login', json=login_data)
    data = response.get_json()
    
    assert response.status_code == 400
    assert 'required' in data['error']

def test_get_current_user(client, auth_headers):
    """Test getting current user info."""
    response = client.get('/api/auth/me', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'user' in data
    assert data['user']['username'] == 'testuser'

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get('/api/auth/me')
    
    assert response.status_code == 401

def test_refresh_token(client, auth_headers):
    """Test token refresh."""
    response = client.post('/api/auth/refresh', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'access_token' in data
    assert 'user' in data

