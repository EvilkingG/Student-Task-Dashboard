// Main Application Script & Event Handlers
document.addEventListener('DOMContentLoaded', async () => {
  initTheme();
  setupEventListeners();

  // Check auth status
  const isAuthenticated = await authManager.checkAuth();
  if (isAuthenticated) {
    showDashboardView();
  } else {
    showAuthView();
  }
});

// Toast notification helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type === 'error' ? 'toast-error' : type === 'success' ? 'toast-success' : ''}`;
  
  const icon = type === 'error' ? 'fa-circle-exclamation' : type === 'success' ? 'fa-circle-check' : 'fa-circle-info';
  
  toast.innerHTML = `
    <i class="fa-solid ${icon}"></i>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
window.showToast = showToast;

// Theme Switcher
function initTheme() {
  const savedTheme = localStorage.getItem('stp_theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
    updateThemeIcon(true);
  }
}

function toggleTheme() {
  const isLight = document.body.classList.toggle('light-theme');
  localStorage.setItem('stp_theme', isLight ? 'light' : 'dark');
  updateThemeIcon(isLight);
}

function updateThemeIcon(isLight) {
  const icon = document.getElementById('theme-icon');
  if (icon) {
    icon.className = isLight ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
  }
}

// View Switches
function showAuthView() {
  document.getElementById('auth-view').style.display = 'flex';
  document.getElementById('dashboard-view').style.display = 'none';
  document.getElementById('user-nav-badge').style.display = 'none';
  document.getElementById('logout-btn').style.display = 'none';
}

function showDashboardView() {
  document.getElementById('auth-view').style.display = 'none';
  document.getElementById('dashboard-view').style.display = 'block';
  
  const navBadge = document.getElementById('user-nav-badge');
  const logoutBtn = document.getElementById('logout-btn');
  const userNameEl = document.getElementById('user-display-name');
  const userAvatarEl = document.getElementById('user-avatar-initial');

  if (navBadge && logoutBtn && authManager.currentUser) {
    navBadge.style.display = 'flex';
    logoutBtn.style.display = 'inline-flex';
    userNameEl.textContent = authManager.currentUser.username;
    userAvatarEl.textContent = authManager.currentUser.username.charAt(0).toUpperCase();
  }

  // Load user's tasks
  taskManager.loadTasks();
}

// Event Listeners Initialization
function setupEventListeners() {
  // Theme toggle
  document.getElementById('theme-toggle-btn').addEventListener('click', toggleTheme);

  // Auth Tabs (Login vs Register)
  const loginTab = document.getElementById('tab-login');
  const registerTab = document.getElementById('tab-register');
  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');

  if (loginTab && registerTab) {
    loginTab.addEventListener('click', () => {
      loginTab.classList.add('active');
      registerTab.classList.remove('active');
      loginForm.style.display = 'block';
      registerForm.style.display = 'none';
    });

    registerTab.addEventListener('click', () => {
      registerTab.classList.add('active');
      loginTab.classList.remove('active');
      registerForm.style.display = 'block';
      loginForm.style.display = 'none';
    });
  }

  // Login Form Submission
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
      await authManager.login(email, password);
      showToast(`Welcome back, ${authManager.currentUser.username}!`, 'success');
      showDashboardView();
    } catch (err) {
      showToast(err.message || 'Login failed', 'error');
    }
  });

  // Register Form Submission
  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('reg-username').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;

    try {
      await authManager.register(username, email, password);
      showToast(`Account created successfully! Welcome, ${username}!`, 'success');
      showDashboardView();
    } catch (err) {
      showToast(err.message || 'Registration failed', 'error');
    }
  });

  // Logout button
  document.getElementById('logout-btn').addEventListener('click', () => {
    authManager.logout();
  });

  // Task Filters
  document.getElementById('filter-status').addEventListener('change', (e) => {
    taskManager.setFilter('status', e.target.value);
  });

  document.getElementById('filter-priority').addEventListener('change', (e) => {
    taskManager.setFilter('priority', e.target.value);
  });

  document.getElementById('filter-timeframe').addEventListener('change', (e) => {
    taskManager.setFilter('timeframe', e.target.value);
  });

  // Real-time Search input with debounce
  let searchTimeout;
  document.getElementById('search-input').addEventListener('input', (e) => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      taskManager.setFilter('search', e.target.value);
    }, 300);
  });

  // Create Task button
  document.getElementById('btn-create-task').addEventListener('click', () => {
    taskManager.openCreateModal();
  });

  // Task Modal Form
  document.getElementById('task-form').addEventListener('submit', (e) => {
    taskManager.handleFormSubmit(e);
  });

  document.getElementById('modal-close-btn').addEventListener('click', () => {
    taskManager.closeModal();
  });

  document.getElementById('modal-cancel-btn').addEventListener('click', () => {
    taskManager.closeModal();
  });

  // Close modal when clicking backdrop
  document.getElementById('task-modal').addEventListener('click', (e) => {
    if (e.target.id === 'task-modal') {
      taskManager.closeModal();
    }
  });
}
