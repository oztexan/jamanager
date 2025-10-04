/**
 * Modern Notification System
 * Provides modern app-style notifications with auto-dismiss, close buttons, and smooth animations
 */
class NotificationSystem {
    constructor() {
        this.container = document.getElementById('notificationContainer');
        this.notifications = new Map(); // Track active notifications
        this.maxNotifications = 5; // Maximum number of notifications to show
        this.defaultDuration = 4000; // Default auto-dismiss duration in ms
        
        if (!this.container) {
            console.error('Notification container not found');
        }
    }

    /**
     * Show a notification
     * @param {string} message - The notification message
     * @param {string} type - Notification type: 'success', 'error', 'info', 'warning'
     * @param {Object} options - Additional options
     * @param {string} options.title - Custom title (defaults to type-based title)
     * @param {number} options.duration - Auto-dismiss duration in ms (default: 4000)
     * @param {boolean} options.persistent - If true, won't auto-dismiss (default: false)
     * @param {string} options.icon - Custom icon (defaults to type-based icon)
     */
    show(message, type = 'info', options = {}) {
        const {
            title = this.getDefaultTitle(type),
            duration = this.defaultDuration,
            persistent = false,
            icon = this.getDefaultIcon(type)
        } = options;

        // Remove oldest notifications if we're at the limit
        if (this.notifications.size >= this.maxNotifications) {
            const oldestId = this.notifications.keys().next().value;
            this.remove(oldestId);
        }

        const id = this.generateId();
        const notification = this.createNotification(id, title, message, type, icon);
        
        this.container.appendChild(notification);
        this.notifications.set(id, {
            element: notification,
            type,
            duration,
            persistent
        });

        // Trigger animation
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto-dismiss if not persistent
        if (!persistent && duration > 0) {
            this.scheduleAutoDismiss(id, duration);
        }

        return id;
    }

    /**
     * Create notification element
     */
    createNotification(id, title, message, type, icon) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.dataset.id = id;

        // Progress bar for auto-dismiss
        const progressBar = document.createElement('div');
        progressBar.className = 'notification-progress';
        progressBar.style.width = '100%';

        // Icon
        const iconEl = document.createElement('div');
        iconEl.className = 'notification-icon';
        iconEl.textContent = icon;

        // Content
        const content = document.createElement('div');
        content.className = 'notification-content';
        
        const titleEl = document.createElement('div');
        titleEl.className = 'notification-title';
        titleEl.textContent = title;
        
        const messageEl = document.createElement('div');
        messageEl.className = 'notification-message';
        messageEl.textContent = message;
        
        content.appendChild(titleEl);
        content.appendChild(messageEl);

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', 'Close notification');
        closeBtn.onclick = () => this.remove(id);

        notification.appendChild(progressBar);
        notification.appendChild(iconEl);
        notification.appendChild(content);
        notification.appendChild(closeBtn);

        return notification;
    }

    /**
     * Remove a notification
     */
    remove(id) {
        const notificationData = this.notifications.get(id);
        if (!notificationData) return;

        const { element } = notificationData;
        
        // Clear any pending auto-dismiss
        if (notificationData.timeoutId) {
            clearTimeout(notificationData.timeoutId);
        }

        // Animate out
        element.classList.add('hide');
        
        // Remove from DOM after animation
        setTimeout(() => {
            if (element.parentNode) {
                element.parentNode.removeChild(element);
            }
            this.notifications.delete(id);
        }, 300); // Match CSS transition duration
    }

    /**
     * Schedule auto-dismiss for a notification
     */
    scheduleAutoDismiss(id, duration) {
        const notificationData = this.notifications.get(id);
        if (!notificationData) return;

        const { element } = notificationData;
        const progressBar = element.querySelector('.notification-progress');
        
        // Animate progress bar
        if (progressBar) {
            progressBar.style.transition = `width ${duration}ms linear`;
            progressBar.style.width = '0%';
        }

        // Set timeout for removal
        notificationData.timeoutId = setTimeout(() => {
            this.remove(id);
        }, duration);
    }

    /**
     * Clear all notifications
     */
    clearAll() {
        const ids = Array.from(this.notifications.keys());
        ids.forEach(id => this.remove(id));
    }

    /**
     * Get default title based on type
     */
    getDefaultTitle(type) {
        const titles = {
            success: 'Success',
            error: 'Error',
            info: 'Information',
            warning: 'Warning'
        };
        return titles[type] || 'Notification';
    }

    /**
     * Get default icon based on type
     */
    getDefaultIcon(type) {
        const icons = {
            success: '✓',
            error: '✕',
            info: 'ℹ',
            warning: '⚠'
        };
        return icons[type] || 'ℹ';
    }

    /**
     * Generate unique ID for notification
     */
    generateId() {
        return `notification_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Convenience methods for different notification types
     */
    success(message, options = {}) {
        return this.show(message, 'success', options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', options);
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', options);
    }
}

// Create global instance
window.notificationSystem = new NotificationSystem();

// Export for use in other modules
window.NotificationSystem = NotificationSystem;
