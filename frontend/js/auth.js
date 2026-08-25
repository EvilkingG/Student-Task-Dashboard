// Authentication manager for Student Task Planner
class AuthManager {
  constructor() {
    this.currentUser = null;
    this.token = localStorage.getItem('stp_token');
    
    try {
      const storedUser = localStorage.getItem('stp_user');
      if (storedUser) {
        this.currentUser = JSON.parse(storedUser);
      }
    } catch (e) {
      console.warn('Could not parse stored user JSON', e);
    }
  }

  isAuthenticated() {
    return !!this.token && !!this.currentUser;
  }

  async checkAuth() {
    if (!this.token) return false;
    try {
      const res = await ApiService.getMe();
      this.currentUser = res.user;
      localStorage.setItem('stp_user', JSON.stringify(res.user));
      return true;
    } catch (err) {
      this.logout();
      return false;
    }
  }

  async login(email, password) {
    const res = await ApiService.login(email, password);
    this.token = res.token;
    this.currentUser = res.user;
    localStorage.setItem('stp_token', res.token);
    localStorage.setItem('stp_user', JSON.stringify(res.user));
    return res;
  }

  async register(username, email, password) {
    const res = await ApiService.register(username, email, password);
    this.token = res.token;
    this.currentUser = res.user;
    localStorage.setItem('stp_token', res.token);
    localStorage.setItem('stp_user', JSON.stringify(res.user));
    return res;
  }

  logout() {
    this.token = null;
    this.currentUser = null;
    localStorage.removeItem('stp_token');
    localStorage.removeItem('stp_user');
    window.location.reload();
  }
}

window.authManager = new AuthManager();
