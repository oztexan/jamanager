/**
 * Component Loader Utility
 * Handles loading and inserting HTML components into the DOM
 */
class ComponentLoader {
    constructor() {
        this.loadedComponents = new Set();
    }

    /**
     * Load a component from a file and insert it into the DOM
     * @param {string} componentPath - Path to the component file
     * @param {string} targetSelector - CSS selector for the target element
     * @param {Object} options - Options for loading
     */
    async loadComponent(componentPath, targetSelector, options = {}) {
        try {
            const response = await fetch(componentPath);
            if (!response.ok) {
                throw new Error(`Failed to load component: ${response.statusText}`);
            }
            
            const html = await response.text();
            const targetElement = document.querySelector(targetSelector);
            
            if (!targetElement) {
                throw new Error(`Target element not found: ${targetSelector}`);
            }

            // Insert the component HTML
            if (options.replace) {
                targetElement.innerHTML = html;
            } else {
                targetElement.insertAdjacentHTML('beforeend', html);
            }

            // Mark as loaded
            this.loadedComponents.add(componentPath);
            
            // Execute any post-load callbacks
            if (options.onLoad) {
                options.onLoad(targetElement);
            }

            return targetElement;
        } catch (error) {
            console.error(`Error loading component ${componentPath}:`, error);
            throw error;
        }
    }

    /**
     * Load multiple components in parallel
     * @param {Array} components - Array of component definitions
     */
    async loadComponents(components) {
        const promises = components.map(comp => 
            this.loadComponent(comp.path, comp.target, comp.options)
        );
        
        try {
            await Promise.all(promises);
            console.log('All components loaded successfully');
        } catch (error) {
            console.error('Error loading components:', error);
            throw error;
        }
    }

    /**
     * Check if a component is already loaded
     * @param {string} componentPath - Path to the component
     */
    isLoaded(componentPath) {
        return this.loadedComponents.has(componentPath);
    }

    /**
     * Clear loaded components cache
     */
    clearCache() {
        this.loadedComponents.clear();
    }
}

// Global component loader instance
window.componentLoader = new ComponentLoader();
