from flask_socketio import emit, join_room, leave_room
from flask_jwt_extended import decode_token
from src.models.user import User
from src.models.task import Task

def handle_task_created(socketio, task_data):
    """Emit task created event to relevant users"""
    task = task_data
    
    # Notify task creator
    socketio.emit('task_created', {
        'task': task.to_dict(),
        'message': f'Task "{task.title}" has been created'
    }, room=f'user_{task.created_by}')
    
    # Notify assigned user if different from creator
    if task.assigned_to and task.assigned_to != task.created_by:
        socketio.emit('task_assigned', {
            'task': task.to_dict(),
            'message': f'You have been assigned task: "{task.title}"'
        }, room=f'user_{task.assigned_to}')

def handle_task_updated(socketio, task_data, old_status=None):
    """Emit task updated event to relevant users"""
    task = task_data
    
    # Notify task creator
    socketio.emit('task_updated', {
        'task': task.to_dict(),
        'message': f'Task "{task.title}" has been updated'
    }, room=f'user_{task.created_by}')
    
    # Notify assigned user if different from creator
    if task.assigned_to and task.assigned_to != task.created_by:
        socketio.emit('task_updated', {
            'task': task.to_dict(),
            'message': f'Task "{task.title}" has been updated'
        }, room=f'user_{task.assigned_to}')
    
    # If status changed, send specific status change event
    if old_status and old_status != task.status:
        status_message = f'Task "{task.title}" status changed from {old_status.value} to {task.status.value}'
        
        socketio.emit('task_status_changed', {
            'task': task.to_dict(),
            'old_status': old_status.value,
            'new_status': task.status.value,
            'message': status_message
        }, room=f'user_{task.created_by}')
        
        if task.assigned_to and task.assigned_to != task.created_by:
            socketio.emit('task_status_changed', {
                'task': task.to_dict(),
                'old_status': old_status.value,
                'new_status': task.status.value,
                'message': status_message
            }, room=f'user_{task.assigned_to}')

def handle_task_deleted(socketio, task_data):
    """Emit task deleted event to relevant users"""
    task = task_data
    
    # Notify task creator
    socketio.emit('task_deleted', {
        'task_id': task.id,
        'message': f'Task "{task.title}" has been deleted'
    }, room=f'user_{task.created_by}')
    
    # Notify assigned user if different from creator
    if task.assigned_to and task.assigned_to != task.created_by:
        socketio.emit('task_deleted', {
            'task_id': task.id,
            'message': f'Task "{task.title}" has been deleted'
        }, room=f'user_{task.assigned_to}')

def authenticate_socket_user(token):
    """Authenticate user from socket token"""
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        user = User.query.get(user_id)
        return user
    except Exception as e:
        print(f"Socket authentication failed: {e}")
        return None

