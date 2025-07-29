/**
 * VeriDoc File Tree Component
 * Handles hierarchical file/directory display and navigation
 */

class FileTree {
    constructor(container, apiClient) {
        this.container = container;
        this.api = apiClient;
        this.currentPath = '/';
        this.selectedItem = null;
        this.cache = new Map();
        this.showHidden = false;
        
        this.init();
    }

    /**
     * Initialize file tree
     */
    init() {
        console.log('FileTree: Initializing file tree...');
        this.container.innerHTML = '<div class="tree-loading">Loading files...</div>';
        this.loadDirectory('/');
        this.bindEvents();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }

        // Container click delegation
        this.container.addEventListener('click', (e) => {
            this.handleClick(e);
        });

        // Container double-click delegation
        this.container.addEventListener('dblclick', (e) => {
            this.handleDoubleClick(e);
        });

        // Keyboard navigation
        this.container.addEventListener('keydown', (e) => {
            this.handleKeyDown(e);
        });
    }

    /**
     * Load directory contents
     */
    async loadDirectory(path, parentElement = null) {
        try {
            console.log('FileTree: Loading directory:', path);
            const data = await this.api.getFiles(path, {
                includeHidden: this.showHidden,
                sortBy: 'name',
                sortOrder: 'asc'
            });

            console.log('FileTree: Received data:', data);
            this.cache.set(path, data);

            if (!parentElement) {
                this.renderRoot(data);
            } else {
                this.renderChildren(data, parentElement);
            }

        } catch (error) {
            console.error('FileTree: Failed to load directory:', error);
            this.showError(error, parentElement);
        }
    }

    /**
     * Render root directory
     */
    renderRoot(data) {
        console.log('FileTree: Rendering root with', data.items.length, 'items');
        this.container.innerHTML = '';
        
        // Add back button if not at root
        if (this.currentPath !== '/') {
            const backButton = document.createElement('div');
            backButton.className = 'tree-item back-button';
            backButton.innerHTML = `
                <span class="tree-icon">⬆️</span>
                <span class="tree-label">.. (Back)</span>
            `;
            backButton.addEventListener('click', () => {
                const parentPath = this.currentPath.split('/').slice(0, -1).join('/') || '/';
                this.navigateToDirectory(parentPath);
            });
            this.container.appendChild(backButton);
        }

        // Sort items: directories first, then files, both alphabetically
        const sortedItems = data.items.sort((a, b) => {
            // Directories first
            if (a.type === 'directory' && b.type === 'file') return -1;
            if (a.type === 'file' && b.type === 'directory') return 1;
            // Then alphabetically by name
            return a.name.localeCompare(b.name);
        });

        // Render items directly to container
        sortedItems.forEach(item => {
            console.log('FileTree: Creating item for:', item.name);
            const itemElement = this.createTreeItem({
                ...item,
                path: this.joinPath(this.currentPath, item.name)
            });
            this.container.appendChild(itemElement);
        });

        console.log('FileTree: Root rendered successfully');
    }


    /**
     * Create tree item element
     */
    createTreeItem(item) {
        const element = document.createElement('div');
        element.className = `tree-item ${item.type}`;
        element.dataset.path = item.path;
        element.dataset.type = item.type;
        element.tabIndex = 0;

        // Remove expand/collapse arrows - keeping simple navigation only

        // File/directory icon
        const icon = document.createElement('span');
        icon.className = 'tree-icon';
        icon.textContent = this.getIcon(item);
        element.appendChild(icon);

        // Label
        const label = document.createElement('span');
        label.className = 'tree-label';
        label.textContent = item.isRoot ? 'Project Files' : item.name;
        label.title = item.path;
        element.appendChild(label);

        // Add metadata for directories
        if (item.type === 'directory' && item.item_count !== undefined) {
            const count = document.createElement('span');
            count.className = 'tree-count';
            count.textContent = `(${item.item_count})`;
            element.appendChild(count);
        }

        return element;
    }

    /**
     * Get appropriate icon for file/directory
     */
    getIcon(item) {
        if (item.type === 'directory') {
            // Special icon for hidden directories
            if (item.name.startsWith('.')) {
                return '📂';
            }
            return '📁';
        }

        const extension = item.extension?.toLowerCase();
        
        // Special handling for dot files (configuration files)
        if (item.name.startsWith('.')) {
            return '⚙️';
        }
        
        // Markdown files
        if (['.md', '.markdown', '.mdown', '.mkd'].includes(extension)) {
            return '📄';
        }
        
        // Mermaid diagrams
        if (['.mmd', '.mermaid'].includes(extension)) {
            return '📊';
        }
        
        // Code files
        if (['.py', '.js', '.html', '.css', '.json', '.yaml', '.yml', '.xml', '.sh'].includes(extension)) {
            return '💻';
        }
        
        // Text files (including .log files)
        if (['.txt', '.text', '.log'].includes(extension)) {
            return '📋';
        }
        
        // Image files
        if (['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'].includes(extension)) {
            return '🖼️';
        }
        
        // Archive files
        if (['.zip', '.tar', '.gz', '.rar'].includes(extension)) {
            return '📦';
        }
        
        return '📄';
    }

    /**
     * Handle click events
     */
    handleClick(e) {
        console.log('FileTree: Click event triggered', e.target);
        const treeItem = e.target.closest('.tree-item');
        console.log('FileTree: Tree item found:', !!treeItem, treeItem?.dataset);
        
        if (!treeItem) {
            console.log('FileTree: No tree item found, returning');
            return;
        }
        
        console.log('FileTree: Item type:', treeItem.dataset.type);
        console.log('FileTree: Item path:', treeItem.dataset.path);

        // Remove expand/collapse functionality - keeping only navigation

        console.log('FileTree: Selecting item:', treeItem.dataset.path, treeItem.dataset.type);
        this.selectItem(treeItem);
        
        // Auto-open files on single click
        if (treeItem.dataset.type === 'file') {
            console.log('FileTree: Auto-opening file:', treeItem.dataset.path);
            this.openFile(treeItem.dataset.path);
        }
        
        // Navigate into directories on single click
        if (treeItem.dataset.type === 'directory') {
            console.log('FileTree: Navigating into directory:', treeItem.dataset.path);
            this.navigateToDirectory(treeItem.dataset.path);
        }
    }

    /**
     * Navigate to directory (show its contents as root)
     */
    async navigateToDirectory(path) {
        try {
            console.log('FileTree: Navigating to directory:', path);
            this.currentPath = path;
            
            // Load the directory contents
            await this.loadDirectory(path);
            
        } catch (error) {
            console.error('FileTree: Failed to navigate to directory:', error);
            this.showError(error);
        }
    }

    /**
     * Handle double-click events
     */
    handleDoubleClick(e) {
        const treeItem = e.target.closest('.tree-item');
        if (!treeItem) return;

        if (treeItem.dataset.type === 'directory') {
            this.toggleDirectory(treeItem);
        } else {
            this.openFile(treeItem.dataset.path);
        }
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyDown(e) {
        const focused = document.activeElement;
        if (!focused || !focused.classList.contains('tree-item')) return;

        switch (e.key) {
            case 'ArrowUp':
                e.preventDefault();
                this.navigateUp(focused);
                break;
            case 'ArrowDown':
                e.preventDefault();
                this.navigateDown(focused);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                // Navigate to parent directory
                if (this.currentPath !== '/') {
                    const parentPath = this.currentPath.split('/').slice(0, -1).join('/') || '/';
                    this.navigateToDirectory(parentPath);
                }
                break;
            case 'ArrowRight':
            case 'Enter':
                e.preventDefault();
                if (focused.dataset.type === 'directory') {
                    this.navigateToDirectory(focused.dataset.path);
                } else {
                    this.openFile(focused.dataset.path);
                }
                break;
        }
    }

    /**
     * Navigate to previous item
     */
    navigateUp(current) {
        const prev = this.getPreviousVisibleItem(current);
        if (prev) {
            prev.focus();
            this.selectItem(prev);
        }
    }

    /**
     * Navigate to next item
     */
    navigateDown(current) {
        const next = this.getNextVisibleItem(current);
        if (next) {
            next.focus();
            this.selectItem(next);
        }
    }

    /**
     * Get previous visible tree item
     */
    getPreviousVisibleItem(item) {
        const allItems = Array.from(this.container.querySelectorAll('.tree-item'));
        const currentIndex = allItems.indexOf(item);
        
        for (let i = currentIndex - 1; i >= 0; i--) {
            if (this.isItemVisible(allItems[i])) {
                return allItems[i];
            }
        }
        
        return null;
    }

    /**
     * Get next visible tree item
     */
    getNextVisibleItem(item) {
        const allItems = Array.from(this.container.querySelectorAll('.tree-item'));
        const currentIndex = allItems.indexOf(item);
        
        for (let i = currentIndex + 1; i < allItems.length; i++) {
            if (this.isItemVisible(allItems[i])) {
                return allItems[i];
            }
        }
        
        return null;
    }

    /**
     * Check if tree item is visible
     */
    isItemVisible(item) {
        let parent = item.parentElement;
        while (parent && parent !== this.container) {
            if (parent.classList.contains('tree-children') && !parent.classList.contains('expanded')) {
                return false;
            }
            parent = parent.parentElement;
        }
        return true;
    }

    /**
     * Select tree item
     */
    selectItem(item) {
        // Remove previous selection
        if (this.selectedItem) {
            this.selectedItem.classList.remove('selected');
        }

        // Add new selection
        item.classList.add('selected');
        this.selectedItem = item;

        // Emit selection event
        this.emit('select', {
            path: item.dataset.path,
            type: item.dataset.type,
            name: item.querySelector('.tree-label').textContent
        });
    }


    /**
     * Open file
     */
    openFile(path) {
        console.log('FileTree: Opening file:', path);
        this.emit('open', { path });
    }

    /**
     * Refresh tree
     */
    refresh() {
        this.cache.clear();
        this.api.clearCache();
        this.init();
    }

    /**
     * Toggle hidden files visibility
     */
    toggleHiddenFiles() {
        this.showHidden = !this.showHidden;
        this.cache.clear();
        this.api.clearCache();
        this.loadDirectory(this.currentPath);
        
        // Emit event to update UI toggle button state
        this.emit('hiddenToggle', { showHidden: this.showHidden });
    }

    /**
     * Join path components
     */
    joinPath(base, name) {
        if (base === '/') {
            return `/${name}`;
        }
        return `${base}/${name}`;
    }

    /**
     * Show error message
     */
    showError(error, container = null) {
        const errorElement = document.createElement('div');
        errorElement.className = 'tree-error';
        const errorMessage = error.message || 'An unknown error occurred.';
        errorElement.innerHTML = `
            <div class="error-icon">⚠️</div>
            <div class="error-message">${errorMessage}</div>
        `;

        if (container) {
            container.appendChild(errorElement);
        } else {
            this.container.innerHTML = '';
            this.container.appendChild(errorElement);
        }
    }

    /**
     * Simple event emitter
     */
    emit(event, data) {
        console.log('FileTree: Emitting event:', `filetree:${event}`, data);
        const customEvent = new CustomEvent(`filetree:${event}`, {
            detail: data
        });
        this.container.dispatchEvent(customEvent);
        console.log('FileTree: Event dispatched to container:', this.container);
    }

    /**
     * Navigate to specific path
     */
    async navigateToPath(targetPath) {
        // For navigation-only mode, just navigate to the directory containing the target
        const pathParts = targetPath.split('/').filter(part => part);
        const directoryPath = pathParts.length > 1 
            ? '/' + pathParts.slice(0, -1).join('/')
            : '/';
        
        // Navigate to the directory
        await this.navigateToDirectory(directoryPath);
        
        // Select target item if it exists
        const targetItem = this.container.querySelector(`[data-path="${targetPath}"]`);
        if (targetItem) {
            this.selectItem(targetItem);
            targetItem.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}

// Export for use in other modules
window.FileTree = FileTree;