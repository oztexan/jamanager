/**
 * Dev Environment Indicator Component
 * 
 * This component provides a consistent development environment indicator
 * that can be included on all pages to show the current sprint/version.
 */

class DevIndicator {
    constructor() {
        this.indicator = null;
        this.init();
    }

    init() {
        // Create the dev indicator element
        this.createIndicator();
        // Add it to the page
        this.addToPage();
        // Add the CSS styles
        this.addStyles();
    }

    createIndicator() {
        this.indicator = document.createElement('div');
        this.indicator.className = 'dev-indicator';
        this.indicator.innerHTML = `
            <span class="sprint-info">Loading sprint info...</span><br>
            <span class="git-info">Loading git info...</span>
        `;
        
        // Fetch git information and update sprint info
        this.loadGitInfo();
    }

    addToPage() {
        // Insert at the beginning of the body
        document.body.insertBefore(this.indicator, document.body.firstChild);
    }

    addStyles() {
        // Check if styles already exist
        if (document.getElementById('dev-indicator-styles')) {
            return;
        }

        const style = document.createElement('style');
        style.id = 'dev-indicator-styles';
        style.textContent = `
            .dev-indicator {
                position: fixed;
                top: 10px;
                right: 10px;
                background: #9b59b6;
                color: white;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                z-index: 9999;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.2;
            }
            .dev-indicator.sprint-1-version {
                background: #9b59b6;
            }
            .dev-indicator.sprint-2-version {
                background: #e74c3c;
            }
            .dev-indicator.sprint-3-version {
                background: #f39c12;
            }
            .dev-indicator.sprint-4-version {
                background: #27ae60;
            }
            .dev-indicator.sprint-5-version {
                background: #3498db;
            }
            .dev-indicator.sprint-6-version {
                background: #8e44ad;
            }
            .dev-indicator.sprint-dev-version {
                background: #34495e;
            }
            .dev-indicator .git-info {
                font-size: 10px;
                opacity: 0.9;
                font-weight: normal;
            }
        `;
        document.head.appendChild(style);
    }

    // Method to update the indicator for different sprints
    updateSprint(sprintNumber, sprintName, features) {
        if (!this.indicator) return;

        const colors = {
            1: 'sprint-1-version',
            2: 'sprint-2-version', 
            3: 'sprint-3-version',
            4: 'sprint-4-version',
            5: 'sprint-5-version',
            6: 'sprint-6-version'
        };

        this.indicator.className = `dev-indicator ${colors[sprintNumber] || 'sprint-1-version'}`;
        this.indicator.innerHTML = `
            🚀 SPRINT ${sprintNumber} - ${sprintName.toUpperCase()}<br>
            Port 3000 | ${features}<br>
            <span class="git-info">Loading git info...</span>
        `;
        
        // Reload git information
        this.loadGitInfo();
    }

    // Method to hide the indicator (for production)
    hide() {
        if (this.indicator) {
            this.indicator.style.display = 'none';
        }
    }

    // Method to show the indicator
    show() {
        if (this.indicator) {
            this.indicator.style.display = 'block';
        }
    }

    // Method to load git information and update sprint info
    async loadGitInfo() {
        try {
            const response = await fetch('/api/dev-info');
            if (response.ok) {
                const data = await response.json();
                
                // Update git info
                const gitInfoElement = this.indicator.querySelector('.git-info');
                if (gitInfoElement) {
                    gitInfoElement.innerHTML = `
                        🌿 ${data.git_branch} | ${data.git_commit}
                    `;
                }
                
                // Determine sprint info based on branch
                this.updateSprintFromBranch(data.git_branch);
                
            } else {
                const gitInfoElement = this.indicator.querySelector('.git-info');
                if (gitInfoElement) {
                    gitInfoElement.innerHTML = '🌿 git info unavailable';
                }
                this.updateSprintFromBranch('unknown');
            }
        } catch (error) {
            console.error('Error loading git info:', error);
            const gitInfoElement = this.indicator.querySelector('.git-info');
            if (gitInfoElement) {
                gitInfoElement.innerHTML = '🌿 git info unavailable';
            }
            this.updateSprintFromBranch('unknown');
        }
    }
    
    // Method to update sprint info based on git branch
    updateSprintFromBranch(branch) {
        const sprintInfoElement = this.indicator.querySelector('.sprint-info');
        if (!sprintInfoElement) return;
        
        let sprintInfo = '';
        let className = 'dev-indicator';
        
        if (branch.includes('sprint-1') || branch === 'main') {
            sprintInfo = '🚀 SPRINT 1 - DEVELOPER EXPERIENCE & DOCUMENTATION<br>Port 3000 | Documentation ✅ | Dev Tools ✅';
            className += ' sprint-1-version';
        } else if (branch.includes('sprint-2')) {
            sprintInfo = '🚀 SPRINT 2 - CODE QUALITY & TESTING<br>Port 3000 | Type Hints ✅ | Error Handling ✅';
            className += ' sprint-2-version';
        } else if (branch.includes('sprint-3')) {
            sprintInfo = '🚀 SPRINT 3 - PERFORMANCE & ARCHITECTURE<br>Port 3000 | Performance ✅ | Architecture ✅';
            className += ' sprint-3-version';
        } else if (branch.includes('sprint-4')) {
            sprintInfo = '🚀 SPRINT 4 - ADVANCED FEATURES<br>Port 3000 | Advanced Features ✅';
            className += ' sprint-4-version';
        } else {
            sprintInfo = `🚀 DEVELOPMENT - ${branch.toUpperCase()}<br>Port 3000 | Development Mode`;
            className += ' sprint-dev-version';
        }
        
        this.indicator.className = className;
        sprintInfoElement.innerHTML = sprintInfo;
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check if dev indicator should be shown
    if (shouldShowDevIndicator()) {
        window.devIndicator = new DevIndicator();
    }
});

/**
 * Determine if the dev indicator should be shown
 * @returns {boolean} True if dev indicator should be displayed
 */
function shouldShowDevIndicator() {
    // Check for explicit disable flag in URL
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('hide-dev-indicator') === 'true') {
        return false;
    }
    
    // Check for explicit enable flag in URL
    if (urlParams.get('show-dev-indicator') === 'true') {
        return true;
    }
    
    // Check if we're in a development environment
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '0.0.0.0';
    
    // Check for development port (3000, 8000, 5000, etc.)
    const isDevPort = [3000, 8000, 5000, 3001, 8001].includes(parseInt(window.location.port));
    
    // Check for development indicators in the page
    const hasDevMeta = document.querySelector('meta[name="dev-environment"]');
    const isDevFromMeta = hasDevMeta && hasDevMeta.getAttribute('content') === 'true';
    
    // Show if any development indicators are present
    return isLocalhost || isDevPort || isDevFromMeta;
}

// Export for manual initialization if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DevIndicator;
}
