/**
 * VeriDoc Main Application
 * Coordinates all components and handles application state
 */

class VeriDocApp {
    constructor() {
        this.components = {};
        this.state = {
            currentFile: null,
            selectedPath: null,
            isLoading: false
        };
        
        this.init();
    }

    /**
     * Initialize application
     */
    async init() {
        try {
            // Show loading overlay
            this.showLoadingOverlay('Initializing VeriDoc...');

            // Check server health
            await this.checkServerHealth();

            // Initialize components
            this.initializeComponents();

            // Bind global events
            this.bindGlobalEvents();

            // Handle initial URL
            this.handleInitialNavigation();

            // Hide loading overlay
            this.hideLoadingOverlay();

        } catch (error) {
            console.error('Failed to initialize VeriDoc:', error);
            this.showError('Failed to initialize application', error);
        }
    }

    /**
     * Check server health
     */
    async checkServerHealth() {
        try {
            await window.apiClient.health();
        } catch (error) {
            throw new Error('Unable to connect to VeriDoc server');
        }
    }

    /**
     * Initialize all components
     */
    initializeComponents() {
        console.log('App: Initializing components...');
        
        // Initialize URL handler
        this.components.urlHandler = new UrlHandler();
        console.log('App: URL handler initialized');

        // Initialize file tree
        const fileTreeContainer = document.getElementById('file-tree');
        console.log('App: File tree container found:', !!fileTreeContainer);
        if (fileTreeContainer) {
            this.components.fileTree = new FileTree(fileTreeContainer, window.apiClient);
            console.log('App: File tree initialized');
        }

        // Initialize content viewer
        const contentContainer = document.getElementById('content-viewer');
        console.log('App: Content container found:', !!contentContainer);
        console.log('App: ContentViewer class available:', !!window.ContentViewer);
        if (contentContainer && window.ContentViewer) {
            try {
                this.components.contentViewer = new ContentViewer(contentContainer, window.apiClient);
                console.log('App: Content viewer initialized');
            } catch (error) {
                console.error('App: Failed to initialize ContentViewer:', error);
                throw error;
            }
        } else {
            console.error('App: Cannot initialize ContentViewer - missing dependencies');
        }

        // Initialize search
        const searchInput = document.getElementById('global-search');
        console.log('App: Search input found:', !!searchInput);
        if (searchInput) {
            this.components.search = new SearchComponent(searchInput, window.apiClient);
            console.log('App: Search component initialized');
        }

        // Initialize resize handler
        this.initializeResizeHandler();
        this.initializeTerminalResizeHandler();

        console.log('✅ VeriDoc components initialized');
    }

    /**
     * Initialize panel resize functionality
     */
    initializeResizeHandler() {
        const resizeHandle = document.getElementById('resize-handle');
        const fileTreePanel = document.getElementById('file-tree-panel');
        const contentPanel = document.getElementById('content-panel');
        
        if (!resizeHandle || !fileTreePanel || !contentPanel) return;

        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        resizeHandle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startWidth = fileTreePanel.offsetWidth;
            
            resizeHandle.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const deltaX = e.clientX - startX;
            const newWidth = startWidth + deltaX;
            const minWidth = 200;
            const maxWidth = 400;
            
            if (newWidth >= minWidth && newWidth <= maxWidth) {
                fileTreePanel.style.width = `${newWidth}px`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizeHandle.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }

    /**
     * Initialize terminal panel resize functionality
     */
    initializeTerminalResizeHandler() {
        const resizeHandle = document.getElementById('terminal-resize-handle');
        const terminalPanel = document.getElementById('terminal-panel');
        
        if (!resizeHandle || !terminalPanel) return;

        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        resizeHandle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startWidth = terminalPanel.offsetWidth;
            
            resizeHandle.classList.add('resizing');
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });

        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;

            const deltaX = startX - e.clientX; // Reverse direction for right panel
            const newWidth = startWidth + deltaX;
            const minWidth = 200;
            const maxWidth = 800;
            
            if (newWidth >= minWidth && newWidth <= maxWidth) {
                terminalPanel.style.width = `${newWidth}px`;
            }
        });

        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                resizeHandle.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
    }

    /**
     * Bind global event listeners
     */
    bindGlobalEvents() {
        console.log('App: Binding global event listeners...');
        
        // File tree events - Listen on the file tree container
        const fileTreeContainer = document.getElementById('file-tree');
        if (fileTreeContainer) {
            fileTreeContainer.addEventListener('filetree:select', (e) => {
                console.log('App: Received filetree:select event:', e.detail);
                this.handleFileSelection(e.detail);
            });

            fileTreeContainer.addEventListener('filetree:open', (e) => {
                console.log('App: Received filetree:open event:', e.detail);
                this.handleFileOpen(e.detail);
            });

            fileTreeContainer.addEventListener('filetree:hiddenToggle', (e) => {
                console.log('App: Received filetree:hiddenToggle event:', e.detail);
                this.updateHiddenToggleButton(e.detail.showHidden);
            });
            console.log('App: File tree event listeners attached');
        } else {
            console.error('App: Could not find file tree container for event binding');
        }

        // Search events
        document.addEventListener('search:select', (e) => {
            this.handleSearchSelection(e.detail);
        });

        // Content viewer events
        document.addEventListener('content:navigate', (e) => {
            this.handleContentNavigation(e.detail);
        });

        // URL handler events
        this.components.urlHandler.on('navigate', (params) => {
            this.handleUrlNavigation(params);
        });

        this.components.urlHandler.on('search', (params) => {
            this.handleUrlSearch(params);
        });

        // Toggle hidden files
        document.getElementById('toggle-hidden-btn')?.addEventListener('click', () => {
            this.toggleHiddenFiles();
        });

        // Files panel collapse/expand
        document.getElementById('toggle-files-panel')?.addEventListener('click', () => {
            this.toggleFilesPanel();
        });

        // Settings and help buttons
        document.getElementById('settings-btn')?.addEventListener('click', () => {
            this.showSettings();
        });

        document.getElementById('help-btn')?.addEventListener('click', () => {
            this.showHelp();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });

        // Window events
        window.addEventListener('resize', () => {
            this.handleWindowResize();
        });

        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    /**
     * Handle initial navigation from URL
     */
    handleInitialNavigation() {
        const params = this.components.urlHandler.getCurrentState();
        
        if (params.search) {
            this.components.search.setQuery(params.search);
        } else if (params.path) {
            this.openFile(params.path, params.line);
        }
    }

    /**
     * Handle file selection in tree
     */
    handleFileSelection(detail) {
        this.state.selectedPath = detail.path;
        
        // Update URL if it's a file
        if (detail.type === 'file') {
            this.components.urlHandler.updateUrl({ path: detail.path }, true);
        }
    }

    /**
     * Handle file opening
     */
    async handleFileOpen(detail) {
        console.log('App: Handling file open:', detail);
        await this.openFile(detail.path);
    }

    /**
     * Handle search result selection
     */
    async handleSearchSelection(detail) {
        await this.openFile(detail.path, detail.line);
        
        // Navigate file tree to the selected file
        await this.components.fileTree.navigateToPath(detail.path);
    }

    /**
     * Handle content navigation (internal links)
     */
    async handleContentNavigation(detail) {
        let targetPath = detail.path;
        
        // Resolve relative paths
        if (this.state.currentFile && !targetPath.startsWith('/')) {
            const currentDir = this.state.currentFile.path.split('/').slice(0, -1).join('/');
            targetPath = this.resolvePath(currentDir, targetPath);
        }

        await this.openFile(targetPath);
    }

    /**
     * Handle URL navigation
     */
    async handleUrlNavigation(params) {
        if (params.path) {
            await this.openFile(params.path, params.line);
            await this.components.fileTree.navigateToPath(params.path);
        }
    }

    /**
     * Handle URL search
     */
    handleUrlSearch(params) {
        if (params.search) {
            this.components.search.setQuery(params.search);
        }
    }

    /**
     * Open file and display content
     */
    async openFile(path, lineNumber = null) {
        console.log('App: Opening file:', path, 'line:', lineNumber);
        try {
            this.state.isLoading = true;
            this.showLoadingOverlay('Loading file...');

            console.log('App: Content viewer available:', !!this.components.contentViewer);
            
            // Display file content
            await this.components.contentViewer.displayFile(path, lineNumber);
            
            // Update state
            this.state.currentFile = { path, lineNumber };
            
            // Update URL
            const urlParams = { path };
            if (lineNumber) {
                urlParams.line = lineNumber;
            }
            this.components.urlHandler.updateUrl(urlParams);

            // Update document title
            const fileName = path.split('/').pop();
            document.title = `${fileName} - VeriDoc`;

            console.log('App: File opened successfully');

        } catch (error) {
            console.error('App: Failed to open file:', error);
            this.showError('Failed to open file', error);
        } finally {
            this.state.isLoading = false;
            this.hideLoadingOverlay();
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboardShortcuts(e) {
        // Global shortcuts
        if (e.ctrlKey || e.metaKey) {
            switch (e.key) {
                case 'p':
                    e.preventDefault();
                    this.components.search.focus();
                    break;
                case 'b':
                    e.preventDefault();
                    this.toggleFileTree();
                    break;
                case '`':
                    e.preventDefault();
                    this.toggleTerminal();
                    break;
                case '/':
                    e.preventDefault();
                    this.components.search.focus();
                    break;
            }
        }

        // Navigation shortcuts
        switch (e.key) {
            case 'F1':
                e.preventDefault();
                this.showHelp();
                break;
        }
    }

    /**
     * Toggle file tree visibility
     */
    toggleFileTree() {
        this.toggleFilesPanel();
    }

    /**
     * Toggle terminal panel
     */
    toggleTerminal() {
        const terminalPanel = document.getElementById('terminal-panel');
        const terminalHandle = document.getElementById('terminal-resize-handle');
        
        if (terminalPanel) {
            const isVisible = terminalPanel.style.display !== 'none';
            const newDisplay = isVisible ? 'none' : 'flex';
            
            terminalPanel.style.display = newDisplay;
            if (terminalHandle) {
                terminalHandle.style.display = newDisplay;
            }
            
            // Initialize terminal placeholder if showing for the first time
            if (newDisplay === 'flex') {
                this.initializeTerminalPlaceholder();
            }
        }
    }

    /**
     * Initialize terminal (Phase 3 feature)
     */
    initializeTerminalPlaceholder() {
        const container = document.getElementById('terminal-container');
        if (!container) return;
        
        // Initialize terminal if not already done
        if (!this.components.terminal) {
            try {
                this.components.terminal = new TerminalComponent();
                this.components.terminal.mount(container);
                console.log('Terminal component initialized');
            } catch (error) {
                console.error('Failed to initialize terminal:', error);
                // Fallback to placeholder
                container.innerHTML = `
                    <div style="padding: var(--spacing-lg); text-align: center; color: var(--text-secondary);">
                        <div style="font-size: var(--font-size-lg); margin-bottom: var(--spacing-md);">
                            ⚠️ Terminal Error
                        </div>
                        <div style="margin-bottom: var(--spacing-md);">
                            <strong>Failed to initialize terminal</strong>
                        </div>
                        <div style="font-size: var(--font-size-sm); line-height: 1.6;">
                            ${error.message || 'Unknown error'}
                        </div>
                    </div>
                `;
            }
        }
    }

    /**
     * Toggle hidden files visibility
     */
    toggleHiddenFiles() {
        if (this.components.fileTree) {
            this.components.fileTree.toggleHiddenFiles();
        }
    }

    /**
     * Update hidden toggle button state
     */
    updateHiddenToggleButton(showHidden) {
        const toggleBtn = document.getElementById('toggle-hidden-btn');
        if (toggleBtn) {
            toggleBtn.textContent = showHidden ? '🙈' : '👁️';
            toggleBtn.title = showHidden ? 'Hide dot files' : 'Show dot files';
        }
    }

    /**
     * Toggle files panel collapse/expand
     */
    toggleFilesPanel() {
        const panel = document.getElementById('file-tree-panel');
        const toggleBtn = document.getElementById('toggle-files-panel');
        
        if (!panel || !toggleBtn) return;
        
        const isCollapsed = panel.classList.contains('collapsed');
        
        if (isCollapsed) {
            // Expand panel
            panel.classList.remove('collapsed');
            toggleBtn.textContent = '◀';
            toggleBtn.title = 'Collapse panel';
        } else {
            // Collapse panel
            panel.classList.add('collapsed');
            toggleBtn.textContent = '▶';
            toggleBtn.title = 'Expand panel';
        }
    }

    /**
     * Show settings dialog
     */
    showSettings() {
        // TODO: Implement settings dialog
        console.log('Settings dialog not yet implemented');
    }

    /**
     * Show help dialog
     */
    showHelp() {
        const helpContent = `
            <div class="help-dialog">
                <div class="help-header">
                    <h2>VeriDoc Help</h2>
                    <button class="panel-btn" onclick="this.closest('.help-dialog').remove()">×</button>
                </div>
                <div class="help-content">
                    <h3>Keyboard Shortcuts</h3>
                    <div class="help-shortcuts">
                        <div class="help-shortcut">
                            <kbd>Ctrl+P</kbd> <span>Focus search</span>
                        </div>
                        <div class="help-shortcut">
                            <kbd>Ctrl+F</kbd> <span>Find in file</span>
                        </div>
                        <div class="help-shortcut">
                            <kbd>Ctrl+B</kbd> <span>Toggle file tree</span>
                        </div>
                        <div class="help-shortcut">
                            <kbd>Ctrl+\`</kbd> <span>Toggle terminal</span>
                        </div>
                        <div class="help-shortcut">
                            <kbd>Ctrl+K</kbd> <span>Copy file path</span>
                        </div>
                        <div class="help-shortcut">
                            <kbd>F1</kbd> <span>Show help</span>
                        </div>
                    </div>
                    
                    <h3>Features</h3>
                    <ul class="help-features">
                        <li>📄 Rich Markdown rendering with Mermaid diagrams</li>
                        <li>🔍 Full-text search across all files</li>
                        <li>💻 Syntax highlighting for code files</li>
                        <li>🖼️ Image preview support</li>
                        <li>📋 Copy code blocks and file paths</li>
                        <li>🔗 Navigate internal links</li>
                        <li>📜 Auto-generated table of contents</li>
                    </ul>
                </div>
            </div>
        `;

        const overlay = document.createElement('div');
        overlay.className = 'help-overlay';
        overlay.innerHTML = helpContent;
        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 2000;
        `;

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.remove();
            }
        });

        document.body.appendChild(overlay);
    }

    /**
     * Handle window resize
     */
    handleWindowResize() {
        // Reposition search results if visible
        const searchPanel = document.getElementById('search-results-panel');
        if (searchPanel && searchPanel.style.display !== 'none') {
            this.components.search.positionResultsPanel();
        }
    }

    /**
     * Show loading overlay
     */
    showLoadingOverlay(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        const text = document.querySelector('#loading-overlay .loading-text');
        
        if (overlay) {
            overlay.style.display = 'flex';
        }
        
        if (text) {
            text.textContent = message;
        }
    }

    /**
     * Hide loading overlay
     */
    hideLoadingOverlay() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    /**
     * Show error message
     */
    showError(title, error) {
        const errorDialog = document.createElement('div');
        errorDialog.className = 'error-dialog';
        errorDialog.innerHTML = `
            <div class="error-content">
                <div class="error-icon">⚠️</div>
                <div class="error-title">${this.escapeHtml(title)}</div>
                <div class="error-message">${this.escapeHtml(error.message || error)}</div>
                <div class="error-actions">
                    <button onclick="this.closest('.error-dialog').remove()">Close</button>
                    <button onclick="location.reload()">Reload</button>
                </div>
            </div>
        `;

        errorDialog.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 3000;
        `;

        document.body.appendChild(errorDialog);
    }

    /**
     * Resolve relative path
     */
    resolvePath(basePath, relativePath) {
        const parts = basePath.split('/').concat(relativePath.split('/'));
        const resolved = [];
        
        for (const part of parts) {
            if (part === '..') {
                resolved.pop();
            } else if (part && part !== '.') {
                resolved.push(part);
            }
        }
        
        return '/' + resolved.join('/');
    }

    /**
     * Cleanup on app shutdown
     */
    cleanup() {
        // Clear any intervals or timeouts
        // Disconnect event listeners if needed
        console.log('🧹 VeriDoc cleanup completed');
    }

    /**
     * Utility function to escape HTML
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Get app performance metrics
     */
    getPerformanceMetrics() {
        return {
            api: window.apiMonitor.getStats(),
            memory: {
                used: performance.memory ? Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) : 'N/A',
                total: performance.memory ? Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) : 'N/A'
            },
            timing: {
                domContentLoaded: performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart,
                loadComplete: performance.timing.loadEventEnd - performance.timing.navigationStart
            }
        };
    }
}

// Additional CSS for dialogs
const dialogCSS = `
    .help-dialog, .error-dialog .error-content {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 8px;
        max-width: 600px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
    }

    .help-header, .error-title {
        background: var(--bg-tertiary);
        border-bottom: 1px solid var(--border);
        padding: var(--spacing-md);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .help-content {
        padding: var(--spacing-lg);
    }

    .help-shortcuts {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: var(--spacing-sm);
        margin-bottom: var(--spacing-lg);
    }

    .help-shortcut {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);
    }

    .help-shortcut kbd {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 3px;
        padding: 2px 6px;
        font-size: var(--font-size-xs);
        font-family: monospace;
        min-width: 60px;
        text-align: center;
    }

    .help-features {
        margin: 0;
        padding-left: var(--spacing-lg);
    }

    .help-features li {
        margin-bottom: var(--spacing-xs);
    }

    .error-content {
        text-align: center;
        padding: var(--spacing-xl);
        min-width: 300px;
    }

    .error-icon {
        font-size: 48px;
        margin-bottom: var(--spacing-md);
    }

    .error-title {
        font-size: var(--font-size-xl);
        margin-bottom: var(--spacing-sm);
        color: var(--text-accent);
        background: none;
        border: none;
        padding: 0;
    }

    .error-message {
        margin-bottom: var(--spacing-lg);
        color: var(--text-secondary);
    }

    .error-actions {
        display: flex;
        gap: var(--spacing-sm);
        justify-content: center;
    }

    .error-actions button {
        padding: var(--spacing-sm) var(--spacing-md);
        background: var(--accent-blue);
        color: var(--text-accent);
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }

    .error-actions button:hover {
        background: #0056b3;
    }
`;

// Inject CSS
const appStyle = document.createElement('style');
appStyle.textContent = dialogCSS;
document.head.appendChild(appStyle);

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.veriDocApp = new VeriDocApp();
    console.log('🚀 VeriDoc application started');
});

// Export for debugging
window.VeriDocApp = VeriDocApp;