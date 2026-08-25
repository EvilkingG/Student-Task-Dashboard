import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'planner.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tasks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'General',
            priority TEXT CHECK(priority IN ('Low', 'Medium', 'High')) DEFAULT 'Medium',
            status TEXT CHECK(status IN ('Pending', 'In Progress', 'Completed')) DEFAULT 'Pending',
            due_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Create index for user_id to optimize user-isolated task queries
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks (user_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);')

    conn.commit()
    conn.close()

# User queries
def create_user(username, email, password_hash):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username.strip(), email.strip().lower(), password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError as e:
        conn.close()
        raise e
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email.strip().lower(),))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

# Task queries (strictly scoped by user_id)
def get_user_tasks(user_id, status=None, priority=None, timeframe=None, search=None):
    conn = get_db()
    cursor = conn.cursor()

    query = 'SELECT * FROM tasks WHERE user_id = ?'
    params = [user_id]

    if status and status != 'All':
        query += ' AND status = ?'
        params.append(status)

    if priority and priority != 'All':
        query += ' AND priority = ?'
        params.append(priority)

    if search and search.strip():
        query += ' AND (title LIKE ? OR description LIKE ? OR category LIKE ?)'
        term = f"%{search.strip()}%"
        params.extend([term, term, term])

    today_str = datetime.now().strftime('%Y-%m-%d')
    if timeframe == 'Overdue':
        query += ' AND due_date < ? AND status != "Completed"'
        params.append(today_str)
    elif timeframe == 'Due Today':
        query += ' AND due_date = ?'
        params.append(today_str)
    elif timeframe == 'Upcoming':
        query += ' AND due_date > ? AND status != "Completed"'
        params.append(today_str)

    query += ' ORDER BY CASE status WHEN "Pending" THEN 1 WHEN "In Progress" THEN 2 WHEN "Completed" THEN 3 END, due_date ASC, priority DESC'

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return [dict(t) for t in tasks]

def get_task_by_id(task_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    task = cursor.fetchone()
    conn.close()
    return dict(task) if task else None

def create_task(user_id, title, description, category, priority, due_date, status='Pending'):
    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute(
        '''INSERT INTO tasks (user_id, title, description, category, priority, due_date, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (user_id, title.strip(), description.strip() if description else '',
         category.strip() if category else 'General', priority, due_date, status, now_str, now_str)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return get_task_by_id(task_id, user_id)

def update_task(task_id, user_id, title, description, category, priority, due_date, status):
    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute(
        '''UPDATE tasks
           SET title = ?, description = ?, category = ?, priority = ?, due_date = ?, status = ?, updated_at = ?
           WHERE id = ? AND user_id = ?''',
        (title.strip(), description.strip() if description else '',
         category.strip() if category else 'General', priority, due_date, status, now_str, task_id, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected > 0:
        return get_task_by_id(task_id, user_id)
    return None

def update_task_status(task_id, user_id, status):
    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().isoformat()
    cursor.execute(
        '''UPDATE tasks SET status = ?, updated_at = ? WHERE id = ? AND user_id = ?''',
        (status, now_str, task_id, user_id)
    )
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    if affected > 0:
        return get_task_by_id(task_id, user_id)
    return None

def delete_task(task_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

def get_task_summary(user_id):
    conn = get_db()
    cursor = conn.cursor()
    today_str = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = "Completed"', (user_id,))
    completed = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = "Pending"', (user_id,))
    pending = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = "In Progress"', (user_id,))
    in_progress = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND due_date < ? AND status != "Completed"', (user_id, today_str))
    overdue = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND due_date = ? AND status != "Completed"', (user_id, today_str))
    due_today = cursor.fetchone()['count']

    conn.close()

    completion_rate = round((completed / total * 100), 1) if total > 0 else 0

    return {
        'total': total,
        'completed': completed,
        'pending': pending,
        'in_progress': in_progress,
        'overdue': overdue,
        'due_today': due_today,
        'completion_rate': completion_rate
    }
