import pytest
import json
from datetime import datetime, timedelta

def test_get_tasks_empty(client, auth_headers):
    """Test getting tasks when none exist."""
    response = client.get('/api/tasks/', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['tasks'] == []
    assert data['count'] == 0

def test_create_task_success(client, auth_headers):
    """Test successful task creation."""
    task_data = {
        'title': 'Test Task',
        'description': 'This is a test task',
        'priority': 'high',
        'due_date': (datetime.utcnow() + timedelta(days=7)).isoformat()
    }
    
    response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 201
    assert data['task']['title'] == 'Test Task'
    assert data['task']['description'] == 'This is a test task'
    assert data['task']['priority'] == 'high'
    assert data['task']['status'] == 'pending'

def test_create_task_missing_title(client, auth_headers):
    """Test task creation without title."""
    task_data = {
        'description': 'This is a test task'
    }
    
    response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 400
    assert 'Title is required' in data['error']

def test_create_task_invalid_status(client, auth_headers):
    """Test task creation with invalid status."""
    task_data = {
        'title': 'Test Task',
        'status': 'invalid_status'
    }
    
    response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 400
    assert 'Invalid status value' in data['error']

def test_create_task_invalid_priority(client, auth_headers):
    """Test task creation with invalid priority."""
    task_data = {
        'title': 'Test Task',
        'priority': 'invalid_priority'
    }
    
    response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 400
    assert 'Invalid priority value' in data['error']

def test_get_task_success(client, auth_headers, test_task):
    """Test getting a specific task."""
    response = client.get(f'/api/tasks/{test_task.id}', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['task']['id'] == test_task.id
    assert data['task']['title'] == test_task.title

def test_get_task_not_found(client, auth_headers):
    """Test getting a non-existent task."""
    response = client.get('/api/tasks/999', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 404
    assert 'Task not found' in data['error']

def test_update_task_success(client, auth_headers):
    """Test successful task update."""
    # First create a task
    task_data = {
        'title': 'Original Task',
        'description': 'Original description'
    }
    
    create_response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    task_id = create_response.get_json()['task']['id']
    
    # Then update it
    update_data = {
        'title': 'Updated Task',
        'description': 'Updated description',
        'status': 'in_progress'
    }
    
    response = client.put(f'/api/tasks/{task_id}', json=update_data, headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['task']['title'] == 'Updated Task'
    assert data['task']['description'] == 'Updated description'
    assert data['task']['status'] == 'in_progress'

def test_update_task_empty_title(client, auth_headers):
    """Test updating task with empty title."""
    # First create a task
    task_data = {
        'title': 'Original Task'
    }
    
    create_response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    task_id = create_response.get_json()['task']['id']
    
    # Try to update with empty title
    update_data = {
        'title': ''
    }
    
    response = client.put(f'/api/tasks/{task_id}', json=update_data, headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 400
    assert 'Title cannot be empty' in data['error']

def test_delete_task_success(client, auth_headers):
    """Test successful task deletion."""
    # First create a task
    task_data = {
        'title': 'Task to Delete'
    }
    
    create_response = client.post('/api/tasks/', json=task_data, headers=auth_headers)
    task_id = create_response.get_json()['task']['id']
    
    # Then delete it
    response = client.delete(f'/api/tasks/{task_id}', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert 'Task deleted successfully' in data['message']
    
    # Verify it's deleted
    get_response = client.get(f'/api/tasks/{task_id}', headers=auth_headers)
    assert get_response.status_code == 404

def test_delete_task_not_found(client, auth_headers):
    """Test deleting a non-existent task."""
    response = client.delete('/api/tasks/999', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 404
    assert 'Task not found' in data['error']

def test_get_task_stats(client, auth_headers):
    """Test getting task statistics."""
    # Create some test tasks
    tasks = [
        {'title': 'Task 1', 'status': 'pending', 'priority': 'high'},
        {'title': 'Task 2', 'status': 'in_progress', 'priority': 'medium'},
        {'title': 'Task 3', 'status': 'completed', 'priority': 'low'},
    ]
    
    for task_data in tasks:
        client.post('/api/tasks/', json=task_data, headers=auth_headers)
    
    response = client.get('/api/tasks/stats', headers=auth_headers)
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['total_tasks'] == 3
    assert data['status_counts']['pending'] == 1
    assert data['status_counts']['in_progress'] == 1
    assert data['status_counts']['completed'] == 1
    assert data['priority_counts']['high'] == 1
    assert data['priority_counts']['medium'] == 1
    assert data['priority_counts']['low'] == 1

def test_tasks_require_authentication(client):
    """Test that task endpoints require authentication."""
    endpoints = [
        ('GET', '/api/tasks/'),
        ('POST', '/api/tasks/'),
        ('GET', '/api/tasks/1'),
        ('PUT', '/api/tasks/1'),
        ('DELETE', '/api/tasks/1'),
        ('GET', '/api/tasks/stats'),
    ]
    
    for method, endpoint in endpoints:
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint, json={})
        elif method == 'PUT':
            response = client.put(endpoint, json={})
        elif method == 'DELETE':
            response = client.delete(endpoint)
        
        assert response.status_code == 401

