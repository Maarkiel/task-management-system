from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import CORS
from src.models.task import Task, TaskStatus, TaskPriority, db
from src.models.user import User
from datetime import datetime

tasks_bp = Blueprint('tasks', __name__)
CORS(tasks_bp)

def emit_task_event(event_name, task_data, **kwargs):
    """Helper function to emit socket events"""
    try:
        from src.routes.socket_events import handle_task_created, handle_task_updated, handle_task_deleted
        socketio = current_app.extensions.get('socketio')
        
        if socketio:
            if event_name == 'task_created':
                handle_task_created(socketio, task_data)
            elif event_name == 'task_updated':
                handle_task_updated(socketio, task_data, kwargs.get('old_status'))
            elif event_name == 'task_deleted':
                handle_task_deleted(socketio, task_data)
    except Exception as e:
        print(f"Error emitting socket event: {e}")

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get query parameters
        status = request.args.get('status')
        priority = request.args.get('priority')
        assigned_to_me = request.args.get('assigned_to_me', 'false').lower() == 'true'
        created_by_me = request.args.get('created_by_me', 'false').lower() == 'true'
        
        # Build query
        query = Task.query
        
        if assigned_to_me:
            query = query.filter(Task.assigned_to == current_user_id)
        elif created_by_me:
            query = query.filter(Task.created_by == current_user_id)
        else:
            # Show tasks assigned to user or created by user
            query = query.filter(
                (Task.assigned_to == current_user_id) | 
                (Task.created_by == current_user_id)
            )
        
        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter(Task.status == status_enum)
            except ValueError:
                return jsonify({'error': 'Invalid status value'}), 400
        
        if priority:
            try:
                priority_enum = TaskPriority(priority)
                query = query.filter(Task.priority == priority_enum)
            except ValueError:
                return jsonify({'error': 'Invalid priority value'}), 400
        
        tasks = query.order_by(Task.created_at.desc()).all()
        
        return jsonify({
            'tasks': [task.to_dict() for task in tasks],
            'count': len(tasks)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400
        
        # Parse due_date if provided
        due_date = None
        if data.get('due_date'):
            try:
                due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use ISO format.'}), 400
        
        # Validate status if provided
        status = TaskStatus.PENDING
        if data.get('status'):
            try:
                status = TaskStatus(data['status'])
            except ValueError:
                return jsonify({'error': 'Invalid status value'}), 400
        
        # Validate priority if provided
        priority = TaskPriority.MEDIUM
        if data.get('priority'):
            try:
                priority = TaskPriority(data['priority'])
            except ValueError:
                return jsonify({'error': 'Invalid priority value'}), 400
        
        # Validate assigned_to if provided
        assigned_to = data.get('assigned_to')
        if assigned_to:
            assignee = User.query.get(assigned_to)
            if not assignee:
                return jsonify({'error': 'Assigned user not found'}), 404
        
        # Create task
        task = Task(
            title=data['title'],
            description=data.get('description'),
            status=status,
            priority=priority,
            due_date=due_date,
            assigned_to=assigned_to,
            created_by=current_user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Emit socket event
        emit_task_event('task_created', task)
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user has access to this task
        if task.assigned_to != current_user_id and task.created_by != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'task': task.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user has access to modify this task
        if task.created_by != current_user_id:
            return jsonify({'error': 'Only task creator can modify the task'}), 403
        
        # Store old status for socket event
        old_status = task.status
        
        # Update fields
        if 'title' in data:
            if not data['title']:
                return jsonify({'error': 'Title cannot be empty'}), 400
            task.title = data['title']
        
        if 'description' in data:
            task.description = data['description']
        
        if 'status' in data:
            try:
                task.status = TaskStatus(data['status'])
            except ValueError:
                return jsonify({'error': 'Invalid status value'}), 400
        
        if 'priority' in data:
            try:
                task.priority = TaskPriority(data['priority'])
            except ValueError:
                return jsonify({'error': 'Invalid priority value'}), 400
        
        if 'due_date' in data:
            if data['due_date']:
                try:
                    task.due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid due_date format. Use ISO format.'}), 400
            else:
                task.due_date = None
        
        if 'assigned_to' in data:
            if data['assigned_to']:
                assignee = User.query.get(data['assigned_to'])
                if not assignee:
                    return jsonify({'error': 'Assigned user not found'}), 404
                task.assigned_to = data['assigned_to']
            else:
                task.assigned_to = None
        
        db.session.commit()
        
        # Emit socket event
        emit_task_event('task_updated', task, old_status=old_status)
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.get(task_id)
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if user has access to delete this task
        if task.created_by != current_user_id:
            return jsonify({'error': 'Only task creator can delete the task'}), 403
        
        # Store task data before deletion for socket event
        task_data_copy = task.to_dict()
        
        db.session.delete(task)
        db.session.commit()
        
        # Emit socket event with copied data
        emit_task_event('task_deleted', type('Task', (), task_data_copy))
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get task statistics for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get tasks assigned to or created by current user
        user_tasks = Task.query.filter(
            (Task.assigned_to == current_user_id) | 
            (Task.created_by == current_user_id)
        ).all()
        
        # Calculate statistics
        total_tasks = len(user_tasks)
        status_counts = {}
        priority_counts = {}
        
        for task in user_tasks:
            # Count by status
            status_key = task.status.value if task.status else 'unknown'
            status_counts[status_key] = status_counts.get(status_key, 0) + 1
            
            # Count by priority
            priority_key = task.priority.value if task.priority else 'unknown'
            priority_counts[priority_key] = priority_counts.get(priority_key, 0) + 1
        
        # Count overdue tasks
        overdue_tasks = 0
        for task in user_tasks:
            if task.due_date and task.due_date < datetime.utcnow() and task.status != TaskStatus.COMPLETED:
                overdue_tasks += 1
        
        return jsonify({
            'total_tasks': total_tasks,
            'status_counts': status_counts,
            'priority_counts': priority_counts,
            'overdue_tasks': overdue_tasks
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

