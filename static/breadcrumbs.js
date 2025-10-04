/**
 * Breadcrumb Navigation System
 * Provides hierarchical navigation for jam manager interface
 */

class BreadcrumbManager {
    constructor() {
        this.breadcrumbs = [];
        this.container = null;
    }

    init(containerId = 'breadcrumb-container') {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.warn('Breadcrumb container not found:', containerId);
            return;
        }
        
        // Only show breadcrumbs for jam managers
        if (this.isJamManager()) {
            this.render();
        } else {
            this.hide();
        }
    }

    addBreadcrumb(label, url = null, isActive = false) {
        this.breadcrumbs.push({
            label: label,
            url: url,
            isActive: isActive
        });
        this.render();
    }

    setBreadcrumbs(breadcrumbs) {
        this.breadcrumbs = breadcrumbs;
        this.render();
    }

    clear() {
        this.breadcrumbs = [];
        this.render();
    }

    isJamManager() {
        // Check if user has jam manager access
        return localStorage.getItem('jamManagerAccess') === 'true';
    }

    hide() {
        if (this.container) {
            this.container.style.display = 'none';
        }
    }

    show() {
        if (this.container) {
            this.container.style.display = 'block';
        }
    }

    render() {
        if (!this.container) return;

        if (this.breadcrumbs.length === 0) {
            this.container.innerHTML = '';
            return;
        }

        const breadcrumbHTML = this.breadcrumbs.map((crumb, index) => {
            const isLast = index === this.breadcrumbs.length - 1;
            const isActive = crumb.isActive || isLast;
            
            if (isActive) {
                return `<span class="breadcrumb-item active" aria-current="page">${crumb.label}</span>`;
            } else {
                return `<a href="${crumb.url || '#'}" class="breadcrumb-item">${crumb.label}</a>`;
            }
        }).join('<span class="breadcrumb-separator">›</span>');

        this.container.innerHTML = `
            <nav class="breadcrumb-nav" aria-label="Breadcrumb">
                ${breadcrumbHTML}
            </nav>
        `;
    }

    // Predefined breadcrumb sets for common pages
    static getHomeBreadcrumbs() {
        return [
            { label: 'Home', url: '/', isActive: true }
        ];
    }

    static getJamManagerBreadcrumbs() {
        return [
            { label: 'Home', url: '/' },
            { label: 'Jam Manager', url: '/jam-manager', isActive: true }
        ];
    }

    static getVenueManagementBreadcrumbs() {
        return [
            { label: 'Home', url: '/' },
            { label: 'Jam Manager', url: '/jam-manager' },
            { label: 'Venue Management', url: '/jam-manager/venues', isActive: true }
        ];
    }

    static getJamDetailsBreadcrumbs(jamName, jamSlug) {
        return [
            { label: 'Home', url: '/' },
            { label: 'Jam Manager', url: '/jam-manager' },
            { label: jamName, url: `/jam/${jamSlug}`, isActive: true }
        ];
    }

    static getSongLibraryBreadcrumbs() {
        return [
            { label: 'Home', url: '/' },
            { label: 'Jam Manager', url: '/jam-manager' },
            { label: 'Song Library', url: '/jam-manager/songs', isActive: true }
        ];
    }

    static getJamManagementBreadcrumbs() {
        return [
            { label: 'Home', url: '/' },
            { label: 'Jam Manager', url: '/jam-manager' },
            { label: 'Jam Management', url: '/jam-manager/jams', isActive: true }
        ];
    }
}

// Global breadcrumb manager instance
window.breadcrumbManager = new BreadcrumbManager();

// Auto-initialize breadcrumbs on page load
document.addEventListener('DOMContentLoaded', function() {
    // Initialize breadcrumbs if container exists
    if (document.getElementById('breadcrumb-container')) {
        window.breadcrumbManager.init();
    }
});
