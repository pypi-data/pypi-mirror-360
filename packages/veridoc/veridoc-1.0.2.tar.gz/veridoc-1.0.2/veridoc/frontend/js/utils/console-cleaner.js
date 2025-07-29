/**
 * Console Cleaner Utility
 * Removes debug console.log statements from production builds
 */

class ConsoleManager {
    constructor() {
        this.isDevelopment = window.location.hostname === 'localhost' || 
                            window.location.hostname === '127.0.0.1' ||
                            window.location.search.includes('debug=true');
        
        this.originalConsole = {
            log: console.log,
            debug: console.debug,
            info: console.info,
            warn: console.warn,
            error: console.error
        };
        
        this.setupConsole();
    }
    
    setupConsole() {
        if (!this.isDevelopment) {
            // In production, replace console methods with no-ops
            console.log = () => {};
            console.debug = () => {};
            
            // Keep info, warn, and error for important messages
            console.info = this.originalConsole.info;
            console.warn = this.originalConsole.warn;
            console.error = this.originalConsole.error;
        }
    }
    
    restoreConsole() {
        // Restore original console methods
        Object.assign(console, this.originalConsole);
    }
    
    log(...args) {
        if (this.isDevelopment) {
            this.originalConsole.log(...args);
        }
    }
    
    debug(...args) {
        if (this.isDevelopment) {
            this.originalConsole.debug(...args);
        }
    }
    
    info(...args) {
        this.originalConsole.info(...args);
    }
    
    warn(...args) {
        this.originalConsole.warn(...args);
    }
    
    error(...args) {
        this.originalConsole.error(...args);
    }
}

// Initialize console manager
const consoleManager = new ConsoleManager();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = consoleManager;
}

// Global access
window.VeriDocConsole = consoleManager;