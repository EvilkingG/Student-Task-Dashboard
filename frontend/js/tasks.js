// Task Manager for Student Task Planner
class TaskManager {
  constructor() {
    this.tasks = [];
    this.currentFilters = {
      status: 'All',
      priority: 'All',
      timeframe: 'All',
      search: ''
    };
    this.editingTaskId = null;
  }

  async loadTasks() {
    const grid = document.getElementById('tasks-grid');
    if (!grid) return;

    grid.innerHTML = '<div style="grid-column: 1/-1; text-align:center; padding: 2rem;"><i class="fa-solid fa-spinner fa-spin fa-2x" style="color:var(--primary)"></i><p style="margin-top:0.5rem; color:var(--text-muted)">Loading your tasks...</p></div>';

    try {
      const res = await ApiService.getTasks(this.currentFilters);
      this.tasks = res.tasks;
      this.renderTasks();
      DashboardManager.updateSummary();
    } catch (err) {
      grid.innerHTML = `<div class="empty-state"><i class="fa-solid fa-exclamation-triangle empty-state-icon" style="color:var(--overdue-red)"></i><h3>Error Loading Tasks</h3><p>${err.message}</p></div>`;
    }
  }

  renderTasks() {
    const grid = document.getElementById('tasks-grid');
    if (!grid) return;

    if (!this.tasks || this.tasks.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <i class="fa-solid fa-clipboard-list empty-state-icon"></i>
          <h3>No Tasks Found</h3>
          <p>You don't have any tasks matching the current filters. Click "Add Task" to create one!</p>
          <button class="btn btn-primary" onclick="taskManager.openCreateModal()">
            <i class="fa-solid fa-plus"></i> Create New Task
          </button>
        </div>
      `;
      return;
    }

    const todayStr = new Date().toISOString().split('T')[0];

    grid.innerHTML = this.tasks.map(t => {
      const isOverdue = t.due_date < todayStr && t.status !== 'Completed';
      const isDueToday = t.due_date === todayStr && t.status !== 'Completed';
      
      const priorityClass = t.priority === 'High' ? 'badge-high' : t.priority === 'Medium' ? 'badge-medium' : 'badge-low';
      
      let statusClass = 'badge-pending';
      if (t.status === 'In Progress') statusClass = 'badge-progress';
      if (t.status === 'Completed') statusClass = 'badge-completed';

      let dueTextClass = '';
      if (isOverdue) dueTextClass = 'overdue-text';
      else if (isDueToday) dueTextClass = 'due-today-text';

      const formattedDate = new Date(t.due_date + 'T00:00:00').toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });

      return `
        <div class="task-card ${t.status === 'Completed' ? 'completed' : ''} ${isOverdue ? 'overdue' : ''}">
          <div>
            <div class="task-header">
              <h4 class="task-title">${this.escapeHtml(t.title)}</h4>
              <span class="badge ${priorityClass}">${t.priority}</span>
            </div>
            
            <p class="task-description">${this.escapeHtml(t.description || 'No description provided.')}</p>

            <div class="task-meta">
              <span class="badge ${statusClass}">${t.status}</span>
              <span class="badge badge-category"><i class="fa-solid fa-tag"></i> ${this.escapeHtml(t.category)}</span>
            </div>

            <div class="task-due ${dueTextClass}">
              <i class="fa-regular fa-calendar-check"></i>
              <span>${isOverdue ? 'Overdue: ' : isDueToday ? 'Due Today: ' : 'Due: '} ${formattedDate}</span>
            </div>
          </div>

          <div class="task-footer">
            <select class="status-dropdown" onchange="taskManager.changeStatus(${t.id}, this.value)">
              <option value="Pending" ${t.status === 'Pending' ? 'selected' : ''}>Pending</option>
              <option value="In Progress" ${t.status === 'In Progress' ? 'selected' : ''}>In Progress</option>
              <option value="Completed" ${t.status === 'Completed' ? 'selected' : ''}>Completed</option>
            </select>

            <div class="task-actions">
              <button class="icon-btn" title="Edit Task" onclick="taskManager.openEditModal(${t.id})">
                <i class="fa-solid fa-pen-to-square"></i>
              </button>
              <button class="icon-btn delete-btn" title="Delete Task" onclick="taskManager.deleteTask(${t.id})">
                <i class="fa-solid fa-trash-can"></i>
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>"']/g, function(m) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[m];
    });
  }

  setFilter(key, value) {
    this.currentFilters[key] = value;
    this.loadTasks();
  }

  openCreateModal() {
    this.editingTaskId = null;
    document.getElementById('modal-title').textContent = 'Create New Task';
    document.getElementById('task-form').reset();
    
    // Set default due date to tomorrow
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    document.getElementById('task-due-date').value = tomorrow.toISOString().split('T')[0];

    document.getElementById('task-modal').classList.add('active');
  }

  openEditModal(taskId) {
    const task = this.tasks.find(t => t.id === taskId);
    if (!task) return;

    this.editingTaskId = taskId;
    document.getElementById('modal-title').textContent = 'Edit Task';
    
    document.getElementById('task-title-input').value = task.title;
    document.getElementById('task-desc-input').value = task.description || '';
    document.getElementById('task-category-input').value = task.category || 'General';
    document.getElementById('task-priority-input').value = task.priority;
    document.getElementById('task-status-input').value = task.status;
    document.getElementById('task-due-date').value = task.due_date;

    document.getElementById('task-modal').classList.add('active');
  }

  closeModal() {
    document.getElementById('task-modal').classList.remove('active');
  }

  async handleFormSubmit(e) {
    e.preventDefault();
    const title = document.getElementById('task-title-input').value.trim();
    const description = document.getElementById('task-desc-input').value.trim();
    const category = document.getElementById('task-category-input').value.trim();
    const priority = document.getElementById('task-priority-input').value;
    const status = document.getElementById('task-status-input').value;
    const due_date = document.getElementById('task-due-date').value;

    if (!title || !due_date) {
      showToast('Title and Due Date are required!', 'error');
      return;
    }

    const payload = { title, description, category, priority, status, due_date };

    try {
      if (this.editingTaskId) {
        await ApiService.updateTask(this.editingTaskId, payload);
        showToast('Task updated successfully!', 'success');
      } else {
        await ApiService.createTask(payload);
        showToast('Task created successfully!', 'success');
      }

      this.closeModal();
      this.loadTasks();
    } catch (err) {
      showToast(err.message || 'Failed to save task', 'error');
    }
  }

  async changeStatus(taskId, newStatus) {
    try {
      await ApiService.updateTaskStatus(taskId, newStatus);
      showToast(`Task marked as ${newStatus}`, 'success');
      this.loadTasks();
    } catch (err) {
      showToast(err.message || 'Failed to update status', 'error');
    }
  }

  async deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task? This cannot be undone.')) return;

    try {
      await ApiService.deleteTask(taskId);
      showToast('Task deleted successfully', 'success');
      this.loadTasks();
    } catch (err) {
      showToast(err.message || 'Failed to delete task', 'error');
    }
  }
}

window.taskManager = new TaskManager();
