// Dashboard Summary & Reminder Manager
class DashboardManager {
  static async updateSummary() {
    try {
      const { summary } = await ApiService.getTaskSummary();
      
      // Update Stat Numbers
      const totalEl = document.getElementById('metric-total');
      const pendingEl = document.getElementById('metric-pending');
      const progressEl = document.getElementById('metric-progress');
      const completedEl = document.getElementById('metric-completed');
      const overdueEl = document.getElementById('metric-overdue');
      const rateEl = document.getElementById('completion-rate-text');
      const progressBar = document.getElementById('progress-bar-fill');

      if (totalEl) totalEl.textContent = summary.total;
      if (pendingEl) pendingEl.textContent = summary.pending;
      if (progressEl) progressEl.textContent = summary.in_progress;
      if (completedEl) completedEl.textContent = summary.completed;
      if (overdueEl) overdueEl.textContent = summary.overdue;

      if (rateEl) rateEl.textContent = `${summary.completion_rate}%`;
      if (progressBar) progressBar.style.width = `${summary.completion_rate}%`;

      // Update Reminder Banner
      this.renderReminders(summary);
    } catch (err) {
      console.error('Failed to load dashboard summary:', err);
    }
  }

  static renderReminders(summary) {
    const bannerContainer = document.getElementById('reminder-banner-container');
    if (!bannerContainer) return;

    if (summary.overdue > 0 || summary.due_today > 0) {
      bannerContainer.style.display = 'flex';
      let msg = '';
      if (summary.overdue > 0 && summary.due_today > 0) {
        msg = `⚠️ Attention! You have <strong>${summary.overdue} overdue</strong> task(s) and <strong>${summary.due_today} task(s) due today</strong>.`;
      } else if (summary.overdue > 0) {
        msg = `🚨 Reminder: You have <strong>${summary.overdue} overdue</strong> task(s) requiring immediate action!`;
      } else {
        msg = `🔔 Heads up! You have <strong>${summary.due_today} task(s) due today</strong>. Stay focused!`;
      }

      bannerContainer.innerHTML = `
        <div class="reminder-banner">
          <i class="fa-solid fa-bell reminder-icon"></i>
          <div>${msg}</div>
        </div>
      `;
    } else {
      bannerContainer.style.display = 'none';
      bannerContainer.innerHTML = '';
    }
  }
}

window.DashboardManager = DashboardManager;
