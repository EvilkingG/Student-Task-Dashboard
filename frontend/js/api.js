// API helper for Student Task Planner
const API_BASE = '/api';

class ApiService {
  static getHeaders(customHeaders = {}) {
    const token = localStorage.getItem('stp_token');
    const headers = {
      'Content-Type': 'application/json',
      ...customHeaders
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  static async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = this.getHeaders(options.headers);
    const config = {
      ...options,
      headers
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 401 && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register')) {
          // Token expired or invalid
          localStorage.removeItem('stp_token');
          localStorage.removeItem('stp_user');
          window.location.reload();
        }
        throw new Error(data.error || 'API Request Failed');
      }

      return data;
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  // Auth APIs
  static login(email, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  static register(username, email, password) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, email, password })
    });
  }

  static getMe() {
    return this.request('/auth/me', { method: 'GET' });
  }

  // Task APIs
  static getTasks(filters = {}) {
    const params = new URLSearchParams();
    if (filters.status && filters.status !== 'All') params.append('status', filters.status);
    if (filters.priority && filters.priority !== 'All') params.append('priority', filters.priority);
    if (filters.timeframe && filters.timeframe !== 'All') params.append('timeframe', filters.timeframe);
    if (filters.search) params.append('search', filters.search);

    const query = params.toString() ? `?${params.toString()}` : '';
    return this.request(`/tasks${query}`, { method: 'GET' });
  }

  static getTaskSummary() {
    return this.request('/tasks/summary', { method: 'GET' });
  }

  static createTask(taskData) {
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData)
    });
  }

  static updateTask(id, taskData) {
    return this.request(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(taskData)
    });
  }

  static updateTaskStatus(id, status) {
    return this.request(`/tasks/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status })
    });
  }

  static deleteTask(id) {
    return this.request(`/tasks/${id}`, { method: 'DELETE' });
  }
}

window.ApiService = ApiService;
