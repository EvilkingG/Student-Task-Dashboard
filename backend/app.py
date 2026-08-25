import os
import sqlite3
from flask import Flask, request, jsonify, g, send_from_directory
from flask_cors import CORS
from database import (
    init_db, create_user, get_user_by_email, get_user_tasks,
    get_task_by_id, create_task, update_task, update_task_status,
    delete_task, get_task_summary
)
from auth import hash_password, check_password, generate_token, token_required

FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

app = Flask(__name__, static_folder=FRONTEND_FOLDER, static_url_path='')
CORS(app)

# Initialize database on startup
with app.app_context():
    init_db()

# Serve static frontend files
@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_FOLDER, path)):
        return send_from_directory(FRONTEND_FOLDER, path)
    return send_from_directory(FRONTEND_FOLDER, 'index.html')

# API Health Check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'app': 'Student Task Planner API',
        'author': 'Shubham Singh',
        'instagram': '@shubhamss.roy',
        'github': 'https://github.com/EvilkingG/student-task-planner'
    }), 200

# Authentication Endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters long.'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Please provide a valid email address.'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    existing_user = get_user_by_email(email)
    if existing_user:
        return jsonify({'error': 'An account with this email already exists.'}), 409

    pwd_hash = hash_password(password)
    try:
        user_id = create_user(username, email, pwd_hash)
        token = generate_token(user_id)
        return jsonify({
            'message': 'Account created successfully!',
            'token': token,
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        }), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Username or email already in use.'}), 409
    except Exception as e:
        return jsonify({'error': f'Failed to create account: {str(e)}'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({'error': 'Invalid email or password.'}), 401

    if not check_password(password, user['password_hash']):
        return jsonify({'error': 'Invalid email or password.'}), 401

    token = generate_token(user['id'])
    return jsonify({
        'message': 'Login successful!',
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me():
    return jsonify({'user': g.current_user}), 200

# Task Management Endpoints (User Isolated)
@app.route('/api/tasks', methods=['GET'])
@token_required
def list_tasks():
    status = request.args.get('status')
    priority = request.args.get('priority')
    timeframe = request.args.get('timeframe')
    search = request.args.get('search')
    
    user_id = g.current_user['id']
    tasks = get_user_tasks(user_id, status=status, priority=priority, timeframe=timeframe, search=search)
    return jsonify({'tasks': tasks}), 200

@app.route('/api/tasks/summary', methods=['GET'])
@token_required
def task_summary():
    user_id = g.current_user['id']
    summary = get_task_summary(user_id)
    return jsonify({'summary': summary}), 200

@app.route('/api/tasks', methods=['POST'])
@token_required
def add_task():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    category = data.get('category', 'General').strip()
    priority = data.get('priority', 'Medium')
    due_date = data.get('due_date', '').strip()
    status = data.get('status', 'Pending')

    if not title:
        return jsonify({'error': 'Task title is required.'}), 400
    if not due_date:
        return jsonify({'error': 'Due date is required.'}), 400
    if priority not in ['Low', 'Medium', 'High']:
        return jsonify({'error': 'Priority must be Low, Medium, or High.'}), 400
    if status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({'error': 'Status must be Pending, In Progress, or Completed.'}), 400

    user_id = g.current_user['id']
    new_task = create_task(user_id, title, description, category, priority, due_date, status)
    return jsonify({
        'message': 'Task created successfully!',
        'task': new_task
    }), 201

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@token_required
def get_task(task_id):
    user_id = g.current_user['id']
    task = get_task_by_id(task_id, user_id)
    if not task:
        return jsonify({'error': 'Task not found or access denied.'}), 404
    return jsonify({'task': task}), 200

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@token_required
def edit_task(task_id):
    user_id = g.current_user['id']
    existing = get_task_by_id(task_id, user_id)
    if not existing:
        return jsonify({'error': 'Task not found or access denied.'}), 404

    data = request.get_json() or {}
    title = data.get('title', existing['title']).strip()
    description = data.get('description', existing['description']).strip()
    category = data.get('category', existing['category']).strip()
    priority = data.get('priority', existing['priority'])
    due_date = data.get('due_date', existing['due_date']).strip()
    status = data.get('status', existing['status'])

    if not title:
        return jsonify({'error': 'Task title is required.'}), 400
    if not due_date:
        return jsonify({'error': 'Due date is required.'}), 400

    updated = update_task(task_id, user_id, title, description, category, priority, due_date, status)
    return jsonify({
        'message': 'Task updated successfully!',
        'task': updated
    }), 200

@app.route('/api/tasks/<int:task_id>/status', methods=['PATCH'])
@token_required
def patch_task_status(task_id):
    user_id = g.current_user['id']
    data = request.get_json() or {}
    new_status = data.get('status')

    if new_status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({'error': 'Invalid status option.'}), 400

    updated = update_task_status(task_id, user_id, new_status)
    if not updated:
        return jsonify({'error': 'Task not found or access denied.'}), 404

    return jsonify({
        'message': f'Task marked as {new_status}',
        'task': updated
    }), 200

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@token_required
def remove_task(task_id):
    user_id = g.current_user['id']
    success = delete_task(task_id, user_id)
    if not success:
        return jsonify({'error': 'Task not found or access denied.'}), 404

    return jsonify({'message': 'Task deleted successfully!'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[+] Student Task Planner Server running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
