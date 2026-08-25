# 🎓 Student Task Planner

A modern, aesthetic full-stack task management application designed for students and individual users to organize daily coursework, track study goals, prioritize assignments, and receive real-time deadline reminder notifications.

---

## 👨‍💻 Author & Developer Info

- **Developer & Author**: **Shubham Singh**
- **Instagram**: [@shubhamss.roy](https://instagram.com/shubhamss.roy)
- **GitHub Profile**: [EvilkingG](https://github.com/EvilkingG)
- **GitHub Repository**: [https://github.com/EvilkingG/Student-Task-Dashboard](https://github.com/EvilkingG/Student-Task-Dashboard)

---

## ✨ Features

- **🔐 User Authentication & Authorization**: Secure registration and login using JWT (JSON Web Tokens) and Bcrypt password hashing.
- **🛡️ Strict User Data Isolation**: Users can only view, create, edit, and delete their own personal tasks.
- **📌 Comprehensive Task Management**:
  - Task title, description, category/subject tagging.
  - Priority levels: **Low**, **Medium**, and **High**.
  - Status states: **Pending**, **In Progress**, and **Completed**.
  - Target Due Date setting.
- **📊 Real-time Dashboard Summary & Progress Metrics**:
  - Live metric counters (Total, Pending, In Progress, Completed, Overdue).
  - Dynamic completion rate percentage & visual progress bar.
- **🔔 Smart Deadline Reminders & Alerts**:
  - Highlighted badges for **Due Today** and **Overdue** tasks.
  - Automatic banner alert for approaching deadlines requiring immediate attention.
- **🔍 Advanced Filtering & Search**:
  - Search by title, description, or subject keyword in real-time.
  - Filter by Status, Priority, or Deadline timeframe (Due Today, Upcoming, Overdue).
- **🎨 Glassmorphic Aesthetic Dark & Light Theme**:
  - Built with CSS custom properties, backdrop blur effects, vibrant priority badges, micro-animations, and theme toggle.

---

## 🛠️ Technologies Used

### Backend
- **Python 3.14+**
- **Flask**: Lightweight web framework and REST API server.
- **SQLite3**: Relational database with foreign key constraints and user index optimizations.
- **PyJWT**: Secure JWT token generation and verification.
- **Bcrypt**: Password hashing and verification.
- **Flask-CORS**: Cross-Origin Resource Sharing middleware.

### Frontend
- **HTML5 & Modern Vanilla CSS3**: Custom CSS variables, glassmorphism, responsive grid layout.
- **JavaScript ES6+**: Vanilla JS modules (`ApiService`, `AuthManager`, `TaskManager`, `DashboardManager`).
- **FontAwesome 6.5**: Icon suite for intuitive UI feedback.

---

## 🚀 Installation & Setup Instructions

### Prerequisites
- Python 3.8+ installed on your system.

### 1. Clone the Repository
```bash
git clone https://github.com/EvilkingG/student-task-planner.git
cd student-task-planner
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional)
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create a `.env` file inside the `backend/` directory or project root based on `.env.example`:
```env
PORT=5000
SECRET_KEY=student_planner_secret_key_2026_shubham_singh
FLASK_ENV=development
```

### 4. Run the Backend Server
```bash
python app.py
```
The server will start on **`http://127.0.0.1:5000`** and automatically initialize the SQLite database (`planner.db`).

### 5. Access the Web Application
Open your browser and visit:
👉 **`http://127.0.0.1:5000`**

---

## 📡 API Information & Endpoints

### Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/auth/register` | Create a new user account | No |
| `POST` | `/api/auth/login` | Authenticate user & return JWT token | No |
| `GET` | `/api/auth/me` | Fetch currently logged-in user details | Yes |

### Task Management Endpoints
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/tasks` | Get list of user's tasks (filters: status, priority, timeframe, search) | Yes |
| `POST` | `/api/tasks` | Create a new task for current user | Yes |
| `GET` | `/api/tasks/<id>` | Fetch single task by ID | Yes |
| `PUT` | `/api/tasks/<id>` | Update existing task details | Yes |
| `PATCH` | `/api/tasks/<id>/status` | Quick update task status | Yes |
| `DELETE` | `/api/tasks/<id>` | Delete task by ID | Yes |
| `GET` | `/api/tasks/summary` | Get task progress metrics & completion stats | Yes |

---

## 🗄️ Database Schema & Information

The SQLite database (`planner.db`) comprises two core tables connected with foreign key constraints:

### `users` Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `tasks` Table
```sql
CREATE TABLE tasks (
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
);
```
- Indexed on `user_id` to guarantee ultra-fast query execution and strict user isolation.

---

## 📄 License & Credits

Developed with ❤️ by **Shubham Singh** ([@shubhamss.roy](https://instagram.com/shubhamss.roy)).
Repository: [EvilkingG/student-task-planner](https://github.com/EvilkingG/student-task-planner)
