/**
 * VeriDoc Content Viewer Component
 * Handles file content display with appropriate rendering
 */

class ContentViewer {
    constructor(container, apiClient) {
        this.container = container;
        this.api = apiClient;
        this.currentFile = null;
        this.markdownRenderer = null;
        this.searchTerms = [];
        this.currentSearchIndex = -1;
        
        this.init();
    }

    /**
     * Initialize content viewer
     */
    init() {
        // Initialize markdown renderer when available
        if (window.MarkdownRenderer) {
            this.markdownRenderer = new MarkdownRenderer();
        } else {
            console.warn('MarkdownRenderer not available, will initialize later');
        }
        
        this.bindEvents();
        this.showWelcomeScreen();
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Content controls
        const findBtn = document.getElementById('find-btn');
        const copyPathBtn = document.getElementById('copy-path-btn');
        const toggleTocBtn = document.getElementById('toggle-toc-btn');

        if (findBtn) {
            findBtn.addEventListener('click', () => this.showFindDialog());
        }

        if (copyPathBtn) {
            copyPathBtn.addEventListener('click', () => this.copyCurrentPath());
        }

        if (toggleTocBtn) {
            toggleTocBtn.addEventListener('click', () => this.toggleTableOfContents());
        }

        // Note: ToC close button removed - now using toggle button and click-outside

        // Close ToC when clicking outside
        document.addEventListener('click', (e) => {
            const tocPanel = document.getElementById('toc-panel');
            const toggleTocBtn = document.getElementById('toggle-toc-btn');
            
            if (tocPanel && tocPanel.classList.contains('open')) {
                // If click is not on the ToC panel or the toggle button
                if (!tocPanel.contains(e.target) && e.target !== toggleTocBtn) {
                    this.hideTableOfContents();
                }
            }
        });

        // Find dialog events
        this.bindFindEvents();

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 'f':
                        e.preventDefault();
                        this.showFindDialog();
                        break;
                    case 'k':
                        e.preventDefault();
                        this.copyCurrentPath();
                        break;
                }
            }
        });

        // Listen for markdown navigation events
        this.container.addEventListener('markdown:navigate', (e) => {
            this.handleInternalNavigation(e.detail.path);
        });
    }

    /**
     * Bind find dialog events
     */
    bindFindEvents() {
        const findDialog = document.getElementById('find-dialog');
        const findInput = document.getElementById('find-input');
        const findPrev = document.getElementById('find-prev');
        const findNext = document.getElementById('find-next');
        const findClose = document.getElementById('find-close');

        if (findInput) {
            findInput.addEventListener('input', () => this.performSearch());
            findInput.addEventListener('keydown', (e) => {
                switch (e.key) {
                    case 'Enter':
                        e.preventDefault();
                        if (e.shiftKey) {
                            this.findPrevious();
                        } else {
                            this.findNext();
                        }
                        break;
                    case 'Escape':
                        e.preventDefault();
                        this.hideFindDialog();
                        break;
                }
            });
        }

        if (findPrev) {
            findPrev.addEventListener('click', () => this.findPrevious());
        }

        if (findNext) {
            findNext.addEventListener('click', () => this.findNext());
        }

        if (findClose) {
            findClose.addEventListener('click', () => this.hideFindDialog());
        }

        // Close find dialog when clicking outside
        document.addEventListener('click', (e) => {
            if (findDialog && !findDialog.contains(e.target) && !e.target.closest('#find-btn')) {
                this.hideFindDialog();
            }
        });
    }

    /**
     * Display file content
     */
    async displayFile(path, lineNumber = null) {
        try {
            this.showLoadingState();
            this.updateBreadcrumb(path);
            
            // Get file content
            const data = await this.api.getFileContent(path);
            this.currentFile = { ...data, path };

            // Determine content type and render
            const extension = data.metadata.extension?.toLowerCase();
            const mimeType = data.metadata.mime_type;
            const filename = path.split('/').pop();

            console.log('DEBUG: File rendering decision for', path);
            console.log('DEBUG: Extension:', extension, 'MIME:', mimeType, 'Filename:', filename);
            console.log('DEBUG: isMarkdown:', this.isMarkdownFile(extension, mimeType));
            console.log('DEBUG: isCode:', this.isCodeFile(extension, mimeType));
            console.log('DEBUG: isImage:', this.isImageFile(extension, mimeType));

            // Force dot files and .log files to be rendered as plain text
            if ((filename.startsWith('.') && extension === '') || extension === '.log') {
                console.log('DEBUG: Rendering as PLAIN TEXT (dot file or .log file)');
                this.renderPlainText(data.content);
            } else if (this.isMarkdownFile(extension, mimeType)) {
                console.log('DEBUG: Rendering as MARKDOWN');
                await this.renderMarkdown(data.content);
            } else if (this.isCodeFile(extension, mimeType)) {
                console.log('DEBUG: Rendering as CODE');
                this.renderCode(data.content, extension);
            } else if (this.isImageFile(extension, mimeType)) {
                console.log('DEBUG: Rendering as IMAGE');
                this.renderImage(path);
            } else {
                console.log('DEBUG: Rendering as PLAIN TEXT');
                this.renderPlainText(data.content);
            }

            // Navigate to specific line if requested
            if (lineNumber) {
                this.scrollToLine(lineNumber);
            }

            this.showContentDisplay();

        } catch (error) {
            console.error('Failed to display file:', error);
            this.showError(error);
        }
    }

    /**
     * Render markdown content
     */
    async renderMarkdown(content) {
        // Ensure markdown renderer is available
        if (!this.markdownRenderer && window.MarkdownRenderer) {
            this.markdownRenderer = new MarkdownRenderer();
        }
        
        const display = document.getElementById('content-display');
        
        if (this.markdownRenderer) {
            await this.markdownRenderer.render(content, display);
        } else {
            // Fallback to simple markdown if renderer not available
            display.className = 'content-markdown';
            display.innerHTML = `<pre>${this.escapeHtml(content)}</pre>`;
        }
        
        // Update TOC button state
        const tocBtn = document.getElementById('toggle-toc-btn');
        if (tocBtn) {
            tocBtn.style.display = 'block';
        }
    }

    /**
     * Render code with syntax highlighting
     */
    renderCode(content, extension) {
        console.log('DEBUG: renderCode called with extension:', extension);
        const display = document.getElementById('content-display');
        display.className = 'content-code';
        console.log('DEBUG: Set display className to:', display.className);

        const language = this.getLanguageFromExtension(extension);
        const lines = content.split('\n');

        const codeHTML = `<div class="code-header">
                <span class="code-language">${language || 'Text'}</span>
                <span class="code-lines">${lines.length} lines</span>
            </div><div class="code-content"><table class="code-table">${lines.map((line, index) => `<tr class="code-line" id="line-${index + 1}">
                            <td class="line-number">${index + 1}</td>
                            <td class="line-content"><code>${this.highlightCodeLine(line, language)}</code></td>
                        </tr>`).join('')}</table></div>`;

        display.innerHTML = codeHTML;
        
        console.log('DEBUG: Generated HTML sample:', codeHTML.substring(0, 500));
        console.log('DEBUG: Display element classes:', display.className);
        
        // Wait for DOM to update, then check styles
        setTimeout(() => {
            const firstLineContent = display.querySelector('.line-content');
            if (firstLineContent) {
                console.log('DEBUG: First line element:', firstLineContent.outerHTML.substring(0, 200));
                const computedStyle = window.getComputedStyle(firstLineContent);
                console.log('DEBUG: Computed styles:', {
                    whiteSpace: computedStyle.whiteSpace,
                    textAlign: computedStyle.textAlign,
                    wordBreak: computedStyle.wordBreak,
                    fontFamily: computedStyle.fontFamily,
                    lineHeight: computedStyle.lineHeight,
                    fontSize: computedStyle.fontSize
                });
            }
        }, 100);

        // Hide TOC button for code files
        const tocBtn = document.getElementById('toggle-toc-btn');
        if (tocBtn) {
            tocBtn.style.display = 'none';
        }
    }

    /**
     * Highlight a single line of code
     */
    highlightCodeLine(line, language) {
        try {
            // Use markdown renderer's enhanced highlighting if available
            if (this.markdownRenderer && typeof this.markdownRenderer.highlightCode === 'function') {
                const highlighted = this.markdownRenderer.highlightCode(line, language);
                if (highlighted && highlighted !== line) {
                    return highlighted;
                }
            }
        } catch (error) {
            console.warn('Enhanced highlighting failed:', error);
        }
        
        // Fallback to Prism.js
        if (window.Prism && language && Prism.languages[language]) {
            try {
                return Prism.highlight(line, Prism.languages[language], language);
            } catch (error) {
                console.warn('Prism highlighting failed:', error);
            }
        }

        // Final fallback to escaped HTML
        return this.escapeHtml(line);
    }

    /**
     * Render plain text
     */
    renderPlainText(content) {
        const display = document.getElementById('content-display');
        display.className = 'content-text';

        const lines = content.split('\n');
        const textHTML = `
            <div class="text-header">
                <span class="text-info">Plain Text</span>
                <span class="text-lines">${lines.length} lines</span>
            </div>
            <div class="text-content">
                <pre>${this.escapeHtml(content)}</pre>
            </div>
        `;

        display.innerHTML = textHTML;

        // Hide TOC button
        const tocBtn = document.getElementById('toggle-toc-btn');
        if (tocBtn) {
            tocBtn.style.display = 'none';
        }
    }

    /**
     * Render image
     */
    renderImage(path) {
        const display = document.getElementById('content-display');
        display.className = 'content-image';

        const imageHTML = `
            <div class="image-container">
                <img src="/api/file_content?path=${encodeURIComponent(path)}" alt="${this.escapeHtml(path)}" />
                <div class="image-info">
                    <span class="image-name">${this.escapeHtml(path.split('/').pop())}</span>
                </div>
            </div>
        `;

        display.innerHTML = imageHTML;

        // Hide TOC button
        const tocBtn = document.getElementById('toggle-toc-btn');
        if (tocBtn) {
            tocBtn.style.display = 'none';
        }
    }

    /**
     * Show welcome screen
     */
    showWelcomeScreen() {
        const welcomeScreen = document.getElementById('welcome-screen');
        const contentDisplay = document.getElementById('content-display');
        
        if (welcomeScreen) welcomeScreen.style.display = 'flex';
        if (contentDisplay) contentDisplay.style.display = 'none';
    }

    /**
     * Show content display
     */
    showContentDisplay() {
        const welcomeScreen = document.getElementById('welcome-screen');
        const contentDisplay = document.getElementById('content-display');
        
        if (welcomeScreen) welcomeScreen.style.display = 'none';
        if (contentDisplay) contentDisplay.style.display = 'block';
    }

    /**
     * Show loading state
     */
    showLoadingState() {
        const display = document.getElementById('content-display');
        if (display) {
            display.classList.add('loading');
        }
    }

    /**
     * Hide loading state
     */
    hideLoadingState() {
        const display = document.getElementById('content-display');
        if (display) {
            display.classList.remove('loading');
        }
    }

    /**
     * Update breadcrumb
     */
    updateBreadcrumb(path) {
        const breadcrumb = document.getElementById('breadcrumb');
        if (!breadcrumb) return;

        const parts = path.split('/').filter(part => part);
        let currentPath = '';
        
        const breadcrumbHTML = ['📁 <span class="breadcrumb-separator">/</span>'].concat(parts.map((part, index) => {
            currentPath += '/' + part;
            const separator = index === 0 ? '' : '<span class="breadcrumb-separator">/</span>';
            return `${separator}<span class="breadcrumb-item">${this.escapeHtml(part)}</span>`;
        })).join('');

        breadcrumb.innerHTML = breadcrumbHTML;
    }

    /**
     * Show error message
     */
    showError(error) {
        const display = document.getElementById('content-display');
        
        const errorMessage = error.message || 'An unknown error occurred.';
        
        const errorHTML = `
            <div class="error-display">
                <div class="error-icon">⚠️</div>
                <div class="error-title">Failed to Load File</div>
                <div class="error-message">${this.escapeHtml(errorMessage)}</div>
                <div class="error-actions">
                    <button class="error-button" onclick="location.reload()">Retry</button>
                </div>
            </div>
        `;

        display.innerHTML = errorHTML;
        display.className = 'content-error';
        
        this.showContentDisplay();
    }

    /**
     * Show find dialog
     */
    showFindDialog() {
        if (!this.currentFile) return;

        const findDialog = document.getElementById('find-dialog');
        const findInput = document.getElementById('find-input');
        
        if (findDialog && findInput) {
            findDialog.style.display = 'block';
            findInput.focus();
            findInput.select();
        }
    }

    /**
     * Hide find dialog
     */
    hideFindDialog() {
        const findDialog = document.getElementById('find-dialog');
        
        if (findDialog) {
            findDialog.style.display = 'none';
        }

        // Clear search highlights
        this.clearSearchHighlights();
    }

    /**
     * Perform search in content
     */
    performSearch() {
        const findInput = document.getElementById('find-input');
        const findCount = document.getElementById('find-count');
        
        if (!findInput || !this.currentFile) return;

        const query = findInput.value.trim();
        
        if (!query) {
            this.clearSearchHighlights();
            if (findCount) findCount.textContent = '0/0';
            return;
        }

        // Clear previous highlights
        this.clearSearchHighlights();

        // Find and highlight matches
        const matches = this.highlightSearchTerms(query);
        this.searchTerms = matches;
        this.currentSearchIndex = matches.length > 0 ? 0 : -1;

        // Update count
        if (findCount) {
            findCount.textContent = `${matches.length > 0 ? 1 : 0}/${matches.length}`;
        }

        // Navigate to first match
        if (matches.length > 0) {
            this.scrollToSearchMatch(0);
        }
    }

    /**
     * Find next search result
     */
    findNext() {
        if (this.searchTerms.length === 0) return;

        this.currentSearchIndex = (this.currentSearchIndex + 1) % this.searchTerms.length;
        this.scrollToSearchMatch(this.currentSearchIndex);
        this.updateSearchCount();
    }

    /**
     * Find previous search result
     */
    findPrevious() {
        if (this.searchTerms.length === 0) return;

        this.currentSearchIndex = this.currentSearchIndex <= 0 
            ? this.searchTerms.length - 1 
            : this.currentSearchIndex - 1;
        this.scrollToSearchMatch(this.currentSearchIndex);
        this.updateSearchCount();
    }

    /**
     * Update search result count
     */
    updateSearchCount() {
        const findCount = document.getElementById('find-count');
        if (findCount && this.searchTerms.length > 0) {
            findCount.textContent = `${this.currentSearchIndex + 1}/${this.searchTerms.length}`;
        }
    }

    /**
     * Highlight search terms in content
     */
    highlightSearchTerms(query) {
        const display = document.getElementById('content-display');
        const matches = [];
        
        if (!display) return matches;

        // Create regex for case-insensitive search
        const regex = new RegExp(this.escapeRegex(query), 'gi');
        const walker = document.createTreeWalker(
            display,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }

        textNodes.forEach((textNode, nodeIndex) => {
            const text = textNode.textContent;
            const matches_in_node = [];
            let match;

            while ((match = regex.exec(text)) !== null) {
                matches_in_node.push({
                    start: match.index,
                    end: match.index + match[0].length,
                    text: match[0]
                });
            }

            if (matches_in_node.length > 0) {
                // Replace text node with highlighted content
                const parent = textNode.parentNode;
                const fragment = document.createDocumentFragment();
                let lastEnd = 0;

                matches_in_node.forEach((match, matchIndex) => {
                    // Add text before match
                    if (match.start > lastEnd) {
                        fragment.appendChild(
                            document.createTextNode(text.substring(lastEnd, match.start))
                        );
                    }

                    // Add highlighted match
                    const highlight = document.createElement('span');
                    highlight.className = 'search-highlight';
                    highlight.textContent = match.text;
                    highlight.dataset.searchIndex = matches.length;
                    fragment.appendChild(highlight);
                    
                    matches.push(highlight);
                    lastEnd = match.end;
                });

                // Add remaining text
                if (lastEnd < text.length) {
                    fragment.appendChild(
                        document.createTextNode(text.substring(lastEnd))
                    );
                }

                parent.replaceChild(fragment, textNode);
            }
        });

        return matches;
    }

    /**
     * Clear search highlights
     */
    clearSearchHighlights() {
        const highlights = document.querySelectorAll('.search-highlight');
        highlights.forEach(highlight => {
            const parent = highlight.parentNode;
            parent.replaceChild(document.createTextNode(highlight.textContent), highlight);
            parent.normalize();
        });

        this.searchTerms = [];
        this.currentSearchIndex = -1;
    }

    /**
     * Scroll to search match
     */
    scrollToSearchMatch(index) {
        if (index < 0 || index >= this.searchTerms.length) return;

        // Remove current highlight
        const currentHighlight = document.querySelector('.search-highlight.current');
        if (currentHighlight) {
            currentHighlight.classList.remove('current');
        }

        // Add current highlight
        const match = this.searchTerms[index];
        match.classList.add('current');
        match.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /**
     * Copy current file path
     */
    async copyCurrentPath() {
        if (!this.currentFile) return;

        try {
            await navigator.clipboard.writeText(this.currentFile.path);
            
            // Show feedback
            const copyBtn = document.getElementById('copy-path-btn');
            if (copyBtn) {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = '✅';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }
        } catch (err) {
            console.error('Failed to copy path:', err);
        }
    }

    /**
     * Toggle table of contents
     */
    toggleTableOfContents() {
        if (!this.currentFile) return;

        const tocPanel = document.getElementById('toc-panel');
        if (!tocPanel) return;

        if (tocPanel.classList.contains('open')) {
            this.hideTableOfContents();
        } else {
            this.showTableOfContents();
        }
    }

    /**
     * Show table of contents
     */
    showTableOfContents() {
        const tocPanel = document.getElementById('toc-panel');
        const tocContent = document.getElementById('toc-content');
        const display = document.getElementById('content-display');
        const toggleBtn = document.getElementById('toggle-toc-btn');
        
        if (!tocPanel || !tocContent || !display) return;

        // Extract TOC from markdown content
        if (this.markdownRenderer) {
            const toc = this.markdownRenderer.extractTableOfContents(display);
            
            if (toc.length === 0) {
                tocContent.innerHTML = '<p class="text-muted">No headings found</p>';
            } else {
                this.markdownRenderer.renderTableOfContents(toc, tocContent);
            }
        } else {
            tocContent.innerHTML = '<p class="text-muted">Table of contents not available</p>';
        }

        tocPanel.style.display = 'block';
        tocPanel.classList.add('open');
        
        // Update toggle button appearance
        if (toggleBtn) {
            toggleBtn.classList.add('active');
            toggleBtn.title = 'Hide table of contents';
        }
    }

    /**
     * Hide table of contents
     */
    hideTableOfContents() {
        const tocPanel = document.getElementById('toc-panel');
        const toggleBtn = document.getElementById('toggle-toc-btn');
        
        if (tocPanel) {
            tocPanel.classList.remove('open');
            // Hide after animation completes
            setTimeout(() => {
                if (!tocPanel.classList.contains('open')) {
                    tocPanel.style.display = 'none';
                }
            }, 300); // Match CSS transition duration
        }
        
        // Update toggle button appearance
        if (toggleBtn) {
            toggleBtn.classList.remove('active');
            toggleBtn.title = 'Table of contents';
        }
    }

    /**
     * Scroll to specific line
     */
    scrollToLine(lineNumber) {
        const lineElement = document.getElementById(`line-${lineNumber}`);
        if (lineElement) {
            lineElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            lineElement.classList.add('highlighted-line');
            
            setTimeout(() => {
                lineElement.classList.remove('highlighted-line');
            }, 3000);
        }
    }

    /**
     * Handle internal navigation (relative links)
     */
    handleInternalNavigation(path) {
        // Emit navigation event for app to handle
        const event = new CustomEvent('content:navigate', {
            detail: { path }
        });
        this.container.dispatchEvent(event);
    }

    /**
     * File type detection helpers
     */
    isMarkdownFile(extension, mimeType) {
        const markdownExtensions = ['.md', '.markdown', '.mdown', '.mkd'];
        return markdownExtensions.includes(extension) || mimeType === 'text/markdown';
    }

    isCodeFile(extension, mimeType) {
        const codeExtensions = [
            // Top 10 languages (Phase 3 priority)
            '.py', '.js', '.java', '.ts', '.c', '.cpp', '.cs', '.php', '.rb', '.go',
            // Additional common languages
            '.jsx', '.tsx', '.h', '.hpp', '.cc', '.cxx', '.kt', '.swift', '.rs', '.dart',
            // Web technologies
            '.html', '.css', '.scss', '.sass', '.vue', '.svelte',
            // Data/config files
            '.json', '.yaml', '.yml', '.xml', '.toml', '.ini', '.cfg', '.conf',
            // Shell and scripting
            '.sh', '.bash', '.zsh', '.fish', '.ps1', '.bat', '.cmd',
            // Other
            '.sql', '.r', '.lua', '.perl', '.vim', '.dockerfile'
        ];
        return codeExtensions.includes(extension) || 
               (mimeType && (mimeType.startsWith('text/') || mimeType.includes('javascript') || mimeType.includes('json')));
    }

    isImageFile(extension, mimeType) {
        const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'];
        return imageExtensions.includes(extension) || (mimeType && mimeType.startsWith('image/'));
    }

    /**
     * Get programming language from file extension
     */
    getLanguageFromExtension(extension) {
        const languageMap = {
            // Top 10 languages
            '.py': 'python',
            '.js': 'javascript',
            '.java': 'java',
            '.ts': 'typescript',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            // Additional languages
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.kt': 'kotlin',
            '.swift': 'swift',
            '.rs': 'rust',
            '.dart': 'dart',
            // Web technologies
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.vue': 'vue',
            '.svelte': 'svelte',
            // Data/config files
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.toml': 'toml',
            '.ini': 'ini',
            '.cfg': 'ini',
            '.conf': 'ini',
            // Shell and scripting
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',
            '.fish': 'bash',
            '.ps1': 'powershell',
            '.bat': 'batch',
            '.cmd': 'batch',
            // Other
            '.sql': 'sql',
            '.r': 'r',
            '.lua': 'lua',
            '.perl': 'perl',
            '.vim': 'vim',
            '.dockerfile': 'docker'
        };

        return languageMap[extension] || null;
    }

    /**
     * Utility functions
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeRegex(text) {
        return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// CSS for additional content viewer styles
const contentViewerCSS = `
    .highlighted-line {
        background-color: var(--accent-yellow) !important;
        color: var(--bg-primary) !important;
        transition: background-color 0.3s ease;
    }

    .content-text .text-header {
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border);
        padding: var(--spacing-sm) var(--spacing-md);
        font-size: var(--font-size-xs);
        color: var(--text-secondary);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .content-text .text-content {
        padding: var(--spacing-md);
        overflow: auto;
    }

    .content-image {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        padding: var(--spacing-lg);
    }

    .image-container {
        text-align: center;
        max-width: 100%;
        max-height: 100%;
    }

    .image-container img {
        max-width: 100%;
        max-height: calc(100vh - 200px);
        object-fit: contain;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .image-info {
        margin-top: var(--spacing-md);
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
    }
`;

// Inject CSS
const contentViewerStyle = document.createElement('style');
contentViewerStyle.textContent = contentViewerCSS;
document.head.appendChild(contentViewerStyle);

// Export for use in other modules
window.ContentViewer = ContentViewer;