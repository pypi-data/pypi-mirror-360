/**
 * VeriDoc Markdown Renderer
 * Enhanced markdown rendering with Mermaid support
 */

class MarkdownRenderer {
    constructor() {
        this.markedOptions = {
            highlight: (code, lang) => {
                return this.highlightCode(code, lang);
            },
            breaks: true,
            gfm: true
        };
        
        // Initialize syntax highlighting support
        this.initializeSyntaxHighlighting();

        // Configure marked
        if (window.marked) {
            marked.setOptions(this.markedOptions);
        }

        // Configure Mermaid
        if (window.mermaid) {
            mermaid.initialize({
                theme: 'dark',
                startOnLoad: false,
                fontFamily: 'Segoe UI, sans-serif',
                fontSize: 14,
                flowchart: {
                    useMaxWidth: true,
                    htmlLabels: true
                },
                sequence: {
                    useMaxWidth: true,
                    messageFontSize: 14,
                    noteFontSize: 12
                },
                gantt: {
                    useMaxWidth: true,
                    fontSize: 12
                }
            });
        }
    }

    /**
     * Render markdown content
     */
    async render(content, container) {
        if (!content || !container) return;

        try {
            // Clear container
            container.innerHTML = '';
            container.className = 'content-markdown';

            // Process content for Mermaid diagrams
            const processedContent = await this.processMermaidBlocks(content);

            // Render markdown
            if (window.marked) {
                const html = marked.parse(processedContent);
                container.innerHTML = html;
            } else {
                // Fallback to simple text rendering
                container.innerHTML = `<pre>${this.escapeHtml(content)}</pre>`;
            }

            // Post-process the rendered content
            await this.postProcess(container);

        } catch (error) {
            console.error('Markdown rendering error:', error);
            this.renderError(container, 'Failed to render markdown content');
        }
    }

    /**
     * Process Mermaid code blocks
     */
    async processMermaidBlocks(content) {
        // Replace mermaid code blocks with placeholder divs
        return content.replace(/```mermaid\n([\s\S]*?)\n```/g, (match, diagram) => {
            const id = 'mermaid-' + Math.random().toString(36).substr(2, 9);
            return `<div class="mermaid-diagram" data-diagram="${this.escapeHtml(diagram)}" id="${id}"></div>`;
        });
    }

    /**
     * Post-process rendered content
     */
    async postProcess(container) {
        // Process Mermaid diagrams
        await this.renderMermaidDiagrams(container);

        // Add copy buttons to code blocks
        this.addCopyButtons(container);

        // Process internal links
        this.processInternalLinks(container);

        // Add table of contents anchors
        this.addHeadingAnchors(container);

        // Process math expressions if MathJax is available
        if (window.MathJax) {
            MathJax.typesetPromise([container]).catch(err => {
                console.warn('MathJax rendering error:', err);
            });
        }
    }

    /**
     * Render Mermaid diagrams
     */
    async renderMermaidDiagrams(container) {
        const diagrams = container.querySelectorAll('.mermaid-diagram');
        
        for (const diagram of diagrams) {
            try {
                const content = diagram.dataset.diagram;
                const id = diagram.id;
                
                if (window.mermaid && content) {
                    const { svg } = await mermaid.render(id, content);
                    diagram.innerHTML = svg;
                    diagram.classList.add('mermaid-rendered');
                }
            } catch (error) {
                console.error('Mermaid rendering error:', error);
                diagram.innerHTML = `
                    <div class="mermaid-error">
                        <div class="error-icon">⚠️</div>
                        <div class="error-message">Failed to render diagram</div>
                        <details>
                            <summary>Show details</summary>
                            <pre>${this.escapeHtml(error.message)}</pre>
                        </details>
                    </div>
                `;
                diagram.classList.add('mermaid-error');
            }
        }
    }

    /**
     * Add copy buttons to code blocks
     */
    addCopyButtons(container) {
        const codeBlocks = container.querySelectorAll('pre code');
        
        codeBlocks.forEach(block => {
            const pre = block.parentElement;
            
            // Skip if already has copy button
            if (pre.querySelector('.copy-button')) return;

            const copyButton = document.createElement('button');
            copyButton.className = 'copy-button';
            copyButton.textContent = '📋';
            copyButton.title = 'Copy to clipboard';
            copyButton.setAttribute('aria-label', 'Copy code to clipboard');

            copyButton.addEventListener('click', async () => {
                try {
                    const text = block.textContent || block.innerText;
                    await navigator.clipboard.writeText(text);
                    
                    // Show feedback
                    copyButton.textContent = '✅';
                    setTimeout(() => {
                        copyButton.textContent = '📋';
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy:', err);
                    copyButton.textContent = '❌';
                    setTimeout(() => {
                        copyButton.textContent = '📋';
                    }, 2000);
                }
            });

            pre.style.position = 'relative';
            pre.appendChild(copyButton);
        });
    }

    /**
     * Process internal links (relative paths)
     */
    processInternalLinks(container) {
        const links = container.querySelectorAll('a[href^="./"], a[href^="../"], a[href^="/"]');
        
        links.forEach(link => {
            const href = link.getAttribute('href');
            
            // Skip external links
            if (href.startsWith('http') || href.startsWith('mailto:')) return;

            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                // Emit navigation event
                const event = new CustomEvent('markdown:navigate', {
                    detail: { path: href }
                });
                container.dispatchEvent(event);
            });

            // Add visual indicator for internal links
            link.classList.add('internal-link');
        });
    }

    /**
     * Add anchor links to headings
     */
    addHeadingAnchors(container) {
        const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
        
        headings.forEach(heading => {
            const id = this.generateHeadingId(heading.textContent);
            heading.id = id;
            
            const anchor = document.createElement('a');
            anchor.className = 'heading-anchor';
            anchor.href = `#${id}`;
            anchor.textContent = '#';
            anchor.title = 'Link to this section';
            anchor.setAttribute('aria-label', `Link to ${heading.textContent}`);

            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                heading.scrollIntoView({ behavior: 'smooth' });
                
                // Update URL without triggering navigation
                history.replaceState(null, '', `#${id}`);
            });

            heading.appendChild(anchor);
        });
    }

    /**
     * Generate heading ID from text
     */
    generateHeadingId(text) {
        return text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '')
            .replace(/\s+/g, '-')
            .replace(/--+/g, '-')
            .trim();
    }

    /**
     * Extract table of contents
     */
    extractTableOfContents(container) {
        const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
        const toc = [];

        headings.forEach(heading => {
            const level = parseInt(heading.tagName.charAt(1));
            const text = heading.textContent.replace('#', '').trim();
            const id = heading.id || this.generateHeadingId(text);
            
            if (!heading.id) {
                heading.id = id;
            }

            toc.push({
                level,
                text,
                id,
                element: heading
            });
        });

        return toc;
    }

    /**
     * Render table of contents
     */
    renderTableOfContents(toc, container) {
        if (!toc.length) {
            container.innerHTML = '<p class="text-muted">No headings found</p>';
            return;
        }

        const list = document.createElement('div');
        list.className = 'toc-list';

        toc.forEach(item => {
            const link = document.createElement('a');
            link.className = `toc-item level-${item.level}`;
            link.href = `#${item.id}`;
            link.textContent = item.text;
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                item.element.scrollIntoView({ behavior: 'smooth' });
            });

            list.appendChild(link);
        });

        container.innerHTML = '';
        container.appendChild(list);
    }

    /**
     * Initialize syntax highlighting support
     */
    initializeSyntaxHighlighting() {
        // Define language mappings and extensions
        this.languageMap = {
            'js': 'javascript',
            'jsx': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'py': 'python',
            'rb': 'ruby',
            'sh': 'bash',
            'yaml': 'yaml',
            'yml': 'yaml',
            'json': 'json',
            'xml': 'xml',
            'html': 'html',
            'css': 'css',
            'scss': 'scss',
            'sass': 'sass',
            'php': 'php',
            'java': 'java',
            'c': 'c',
            'cpp': 'cpp',
            'cxx': 'cpp',
            'cc': 'cpp',
            'h': 'c',
            'hpp': 'cpp',
            'cs': 'csharp',
            'go': 'go',
            'rs': 'rust',
            'kt': 'kotlin',
            'swift': 'swift',
            'dart': 'dart',
            'r': 'r',
            'sql': 'sql',
            'md': 'markdown',
            'dockerfile': 'docker',
            'vim': 'vim',
            'lua': 'lua',
            'perl': 'perl',
            'powershell': 'powershell',
            'ps1': 'powershell'
        };
        
        // Top 10 languages for Phase 3
        this.topLanguages = [
            'javascript', 'python', 'java', 'typescript', 'c', 'cpp', 
            'csharp', 'php', 'ruby', 'go'
        ];
    }

    /**
     * Enhanced code highlighting
     */
    highlightCode(code, lang) {
        if (!code) return '';
        
        // Normalize language
        const normalizedLang = this.normalizeLanguage(lang);
        
        // Use Prism.js if available
        if (window.Prism && normalizedLang && Prism.languages[normalizedLang]) {
            try {
                return Prism.highlight(code, Prism.languages[normalizedLang], normalizedLang);
            } catch (error) {
                console.warn('Prism highlighting failed:', error);
            }
        }
        
        // Fallback to basic highlighting
        return this.basicHighlight(code, normalizedLang);
    }
    
    /**
     * Normalize language name
     */
    normalizeLanguage(lang) {
        if (!lang) return null;
        
        const normalized = lang.toLowerCase();
        return this.languageMap[normalized] || normalized;
    }
    
    /**
     * Basic syntax highlighting fallback
     */
    basicHighlight(code, lang) {
        if (!lang) return this.escapeHtml(code);
        
        let highlighted = this.escapeHtml(code);
        
        // Basic patterns for common languages
        const patterns = {
            javascript: [
                { pattern: /\b(function|const|let|var|return|if|else|for|while|class|extends|import|export|from|async|await|try|catch|throw|new|this|super)\b/g, className: 'keyword' },
                { pattern: /\b(true|false|null|undefined)\b/g, className: 'boolean' },
                { pattern: /\b\d+(\.\d+)?\b/g, className: 'number' },
                { pattern: /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, className: 'string' },
                { pattern: /\/\/.*$/gm, className: 'comment' },
                { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' }
            ],
            python: [
                { pattern: /\b(def|class|if|elif|else|for|while|try|except|finally|import|from|return|yield|lambda|with|as|pass|break|continue|and|or|not|is|in|True|False|None)\b/g, className: 'keyword' },
                { pattern: /\b(True|False|None)\b/g, className: 'boolean' },
                { pattern: /\b\d+(\.\d+)?\b/g, className: 'number' },
                { pattern: /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, className: 'string' },
                { pattern: /#.*$/gm, className: 'comment' }
            ],
            java: [
                { pattern: /\b(public|private|protected|static|final|abstract|class|interface|extends|implements|import|package|return|if|else|for|while|try|catch|throw|new|this|super|void|int|String|boolean|double|float|long|char)\b/g, className: 'keyword' },
                { pattern: /\b(true|false|null)\b/g, className: 'boolean' },
                { pattern: /\b\d+(\.\d+)?[fFdD]?\b/g, className: 'number' },
                { pattern: /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, className: 'string' },
                { pattern: /\/\/.*$/gm, className: 'comment' },
                { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' }
            ],
            css: [
                { pattern: /[.#][\w-]+/g, className: 'selector' },
                { pattern: /\b(color|background|font|margin|padding|border|width|height|display|position|float|clear|overflow|z-index|opacity|transform|transition|animation)\b/g, className: 'property' },
                { pattern: /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, className: 'string' },
                { pattern: /\/\*[\s\S]*?\*\//g, className: 'comment' }
            ],
            html: [
                { pattern: /<\/?[\w-]+(?:\s+[\w-]+(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?)*\s*\/?>/g, className: 'tag' },
                { pattern: /<!--[\s\S]*?-->/g, className: 'comment' }
            ],
            json: [
                { pattern: /"[\w\s-]+"\s*:/g, className: 'property' },
                { pattern: /\b(true|false|null)\b/g, className: 'boolean' },
                { pattern: /\b\d+(\.\d+)?\b/g, className: 'number' },
                { pattern: /(["'])((?:\\.|(?!\1)[^\\])*?)\1/g, className: 'string' }
            ]
        };
        
        const langPatterns = patterns[lang];
        if (langPatterns) {
            langPatterns.forEach(({ pattern, className }) => {
                highlighted = highlighted.replace(pattern, `<span class="token ${className}">$&</span>`);
            });
        }
        
        return highlighted;
    }

    /**
     * Render error message
     */
    renderError(container, message) {
        container.innerHTML = `
            <div class="error-display">
                <div class="error-icon">⚠️</div>
                <div class="error-title">Rendering Error</div>
                <div class="error-message">${this.escapeHtml(message)}</div>
            </div>
        `;
    }

    /**
     * Escape HTML characters
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Check if content is likely markdown
     */
    isMarkdown(content, filename = '') {
        const extension = filename.split('.').pop()?.toLowerCase();
        const markdownExtensions = ['md', 'markdown', 'mdown', 'mkd'];
        
        if (markdownExtensions.includes(extension)) {
            return true;
        }

        // Check for common markdown patterns
        const markdownPatterns = [
            /^#{1,6}\s/m,           // Headers
            /^\*\s/m,               // Bullet lists
            /^\d+\.\s/m,            // Numbered lists
            /\[.*\]\(.*\)/,         // Links
            /\*\*.*\*\*/,           // Bold
            /\*.*\*/,               // Italic
            /```[\s\S]*```/,        // Code blocks
            /^\>\s/m                // Blockquotes
        ];

        return markdownPatterns.some(pattern => pattern.test(content));
    }
}

// CSS for markdown enhancements
const markdownCSS = `
    .copy-button {
        position: absolute;
        top: 8px;
        right: 8px;
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 4px;
        width: 32px;
        height: 32px;
        font-size: 14px;
        opacity: 0;
        transition: opacity 0.2s ease;
    }

    pre:hover .copy-button {
        opacity: 1;
    }

    .copy-button:hover {
        background: var(--bg-tertiary);
    }

    .heading-anchor {
        margin-left: 8px;
        opacity: 0;
        color: var(--text-secondary);
        text-decoration: none;
        font-weight: normal;
        transition: opacity 0.2s ease;
    }

    h1:hover .heading-anchor,
    h2:hover .heading-anchor,
    h3:hover .heading-anchor,
    h4:hover .heading-anchor,
    h5:hover .heading-anchor,
    h6:hover .heading-anchor {
        opacity: 1;
    }

    .internal-link {
        color: var(--accent-green) !important;
    }

    .internal-link:hover {
        color: var(--accent-blue) !important;
    }

    .mermaid-diagram {
        margin: 16px 0;
        text-align: center;
        background: var(--bg-tertiary);
        border-radius: 6px;
        padding: 16px;
    }

    .mermaid-error {
        background: var(--bg-tertiary);
        border: 1px solid var(--accent-red);
        border-radius: 6px;
        padding: 16px;
        color: var(--accent-red);
    }

    .mermaid-error details {
        margin-top: 8px;
    }

    .mermaid-error pre {
        background: var(--bg-primary);
        color: var(--text-secondary);
        font-size: 12px;
        margin: 8px 0 0 0;
    }
`;

// Inject CSS
const markdownStyle = document.createElement('style');
markdownStyle.textContent = markdownCSS;
document.head.appendChild(markdownStyle);

// Export for use in other modules
window.MarkdownRenderer = MarkdownRenderer;