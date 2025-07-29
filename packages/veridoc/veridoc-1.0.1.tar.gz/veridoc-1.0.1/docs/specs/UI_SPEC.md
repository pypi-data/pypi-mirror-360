# VeriDoc UI Specification

## Design Philosophy

VeriDoc's interface is designed for **rapid documentation verification** during AI-assisted development. Every design decision prioritizes speed, clarity, and minimal cognitive overhead.

### Core Principles
- **Verification-First**: Interface optimized for reading, not editing
- **Zero Context-Switch**: Sub-500ms interactions to maintain flow state
- **Minimal Cognitive Load**: Clean, distraction-free interface
- **Documentation-Centric**: Purpose-built for technical documentation

## Overall Layout

### Two-Pane Layout Structure
```
┌─────────────────────────────────────────────────────────────┐
│                    VeriDoc - localhost:5000                 │
├─────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────────────────────────────────┐ │
│ │             │ │                                         │ │
│ │  File Tree  │ │           Content Viewer               │ │
│ │   (Left)    │ │              (Right)                   │ │
│ │             │ │                                         │ │
│ │  - docs/    │ │  # API Documentation                   │ │
│ │    + api/   │ │                                         │ │
│ │    - guide/ │ │  This document describes the API...    │ │
│ │      spec.md│ │                                         │ │
│ │      intro.md│ │  ## Authentication                     │ │
│ │    README.md│ │                                         │ │
│ │             │ │  All API endpoints require...          │ │
│ │             │ │                                         │ │
│ │             │ │                                         │ │
│ └─────────────┘ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                    Terminal Panel (Optional)                │
└─────────────────────────────────────────────────────────────┘
```

### Layout Specifications
- **Left Panel**: 280px width, resizable (min: 200px, max: 400px)
- **Right Panel**: Remaining width, minimum 600px
- **Terminal Panel**: 200px height when open, collapsible
- **Total Min Width**: 800px
- **Total Min Height**: 600px

## Header Bar

### Header Content
```
┌─────────────────────────────────────────────────────────────┐
│ [📁] VeriDoc    [🔍] Search    [⚙️] Settings    [❓] Help    │
└─────────────────────────────────────────────────────────────┘
```

### Header Elements
- **Logo/Title**: "VeriDoc" with folder icon
- **Search Bar**: Global search with autocomplete
- **Settings Menu**: Preferences and configuration
- **Help Menu**: Documentation and shortcuts
- **Status**: Current path and connection status

### Header Styling
```css
.header {
    height: 48px;
    background: #1e1e1e;
    border-bottom: 1px solid #333;
    display: flex;
    align-items: center;
    padding: 0 16px;
    gap: 16px;
}

.header-title {
    font-size: 16px;
    font-weight: 600;
    color: #ffffff;
}

.header-search {
    flex: 1;
    max-width: 400px;
    height: 32px;
    background: #2d2d2d;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 0 12px;
    color: #ffffff;
}
```

## File Tree Panel

### Tree Structure
```
📁 project-root/
├── 📁 docs/
│   ├── 📁 api/
│   │   ├── 📄 endpoints.md
│   │   └── 📄 authentication.md
│   ├── 📁 guides/
│   │   ├── 📄 getting-started.md
│   │   └── 📄 advanced.md
│   └── 📄 README.md
├── 📁 src/
│   ├── 📄 main.py
│   └── 📄 config.py
└── 📄 package.json
```

### Tree Interactions
- **Click**: Navigate to file/directory
- **Double-click**: Open file in content viewer
- **Right-click**: Context menu (copy path, reveal in terminal)
- **Keyboard**: Arrow keys for navigation, Enter to open

### Tree Styling
```css
.file-tree {
    width: 280px;
    height: 100%;
    background: #252526;
    border-right: 1px solid #333;
    overflow-y: auto;
}

.tree-item {
    height: 28px;
    padding: 4px 8px;
    display: flex;
    align-items: center;
    cursor: pointer;
    color: #cccccc;
}

.tree-item:hover {
    background: #2a2d2e;
}

.tree-item.selected {
    background: #094771;
    color: #ffffff;
}

.tree-icon {
    width: 16px;
    height: 16px;
    margin-right: 6px;
}
```

### File Type Icons
- **📁** Directory (expandable)
- **📄** Markdown (.md)
- **📋** Text (.txt)
- **📊** Data (.json, .yaml, .csv)
- **💻** Code (.py, .js, .html, .css)
- **🖼️** Image (.png, .jpg, .svg)
- **📦** Archive (.zip, .tar)
- **❓** Unknown file type

## Content Viewer Panel

### Content Types & Rendering

#### Markdown Files (.md)
```
┌─────────────────────────────────────────────────────────────┐
│ # API Documentation                                         │
│                                                             │
│ This document describes the VeriDoc API endpoints and      │
│ their usage patterns.                                       │
│                                                             │
│ ## Table of Contents                                        │
│ - [Authentication](#authentication)                         │
│ - [Endpoints](#endpoints)                                   │
│ - [Examples](#examples)                                     │
│                                                             │
│ ## Authentication                                           │
│                                                             │
│ All API endpoints require proper authentication...         │
│                                                             │
│ ```python                                                   │
│ import requests                                             │
│ response = requests.get('/api/files')                       │
│ ```                                                         │
└─────────────────────────────────────────────────────────────┘
```

#### Mermaid Diagrams (.mmd)
```
┌─────────────────────────────────────────────────────────────┐
│ graph TD                                                    │
│     A[User Request] --> B[API Gateway]                     │
│     B --> C[File Service]                                  │
│     C --> D[File System]                                   │
│     D --> E[Response]                                       │
│                                                             │
│ [Interactive diagram rendered here]                         │
└─────────────────────────────────────────────────────────────┘
```

#### Code Files (.py, .js, .html, etc.)
```
┌─────────────────────────────────────────────────────────────┐
│   1 │ from fastapi import FastAPI                            │
│   2 │ from pathlib import Path                               │
│   3 │                                                        │
│   4 │ app = FastAPI()                                        │
│   5 │                                                        │
│   6 │ @app.get("/api/files")                                 │
│   7 │ async def get_files(path: str = "/"):                  │
│   8 │     """Get directory listing"""                        │
│   9 │     base_path = Path("/docs")                          │
│  10 │     return {"files": list(base_path.iterdir())}        │
└─────────────────────────────────────────────────────────────┘
```

### Content Viewer Controls
```
┌─────────────────────────────────────────────────────────────┐
│ [📄] api.md  [🔍] Find  [🔗] Links  [📋] Copy  [⚙️] Settings │
└─────────────────────────────────────────────────────────────┘
```

### Content Viewer Features
- **Find in File**: Ctrl+F for text search
- **Table of Contents**: Auto-generated for Markdown
- **Line Numbers**: Toggle for code files
- **Copy Path**: Quick copy of file path
- **Print View**: Print-friendly styling

### Content Styling
```css
.content-viewer {
    flex: 1;
    height: 100%;
    background: #1e1e1e;
    overflow-y: auto;
    padding: 24px;
}

.content-markdown {
    max-width: 800px;
    line-height: 1.6;
    color: #cccccc;
}

.content-markdown h1 {
    color: #ffffff;
    font-size: 28px;
    margin-bottom: 16px;
    border-bottom: 1px solid #333;
    padding-bottom: 8px;
}

.content-markdown h2 {
    color: #ffffff;
    font-size: 22px;
    margin-top: 24px;
    margin-bottom: 12px;
}

.content-markdown code {
    background: #2d2d2d;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Fira Code', monospace;
}

.content-markdown pre {
    background: #2d2d2d;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
```

## Search Interface

### Global Search Bar
```
┌─────────────────────────────────────────────────────────────┐
│ [🔍] Search files and content...                     [×]    │
└─────────────────────────────────────────────────────────────┘
```

### Search Results Panel
```
┌─────────────────────────────────────────────────────────────┐
│ Search Results for "authentication"                         │
│                                                             │
│ 📄 docs/api/auth.md                                         │
│ Authentication methods and security guidelines              │
│                                                             │
│ 📄 docs/guide/security.md                                  │
│ ...implementation of authentication requires...             │
│                                                             │
│ 📄 src/auth.py                                             │
│ def authenticate(token: str) -> bool:                       │
└─────────────────────────────────────────────────────────────┘
```

### Search Features
- **Real-time search**: Results as you type
- **File name matching**: Fuzzy file name search
- **Content matching**: Full-text search within files
- **Regex support**: Advanced pattern matching
- **Filters**: File type, directory, date modified

## Terminal Panel

### Terminal Interface
```
┌─────────────────────────────────────────────────────────────┐
│ Terminal                                            [─] [×] │
├─────────────────────────────────────────────────────────────┤
│ user@localhost:~/project$ ls docs/                         │
│ api/  guides/  README.md                                   │
│ user@localhost:~/project$ cat docs/README.md               │
│ # Project Documentation                                     │
│                                                             │
│ This directory contains all project documentation.         │
│ user@localhost:~/project$ ▊                               │
└─────────────────────────────────────────────────────────────┘
```

### Terminal Features
- **Integrated terminal**: Full shell access
- **Command history**: Previous command recall
- **Copy/paste**: Standard terminal operations
- **Resizable**: Adjustable height
- **Collapsible**: Hide when not needed

## Responsive Design

### Breakpoints
- **Large**: > 1200px (Full two-pane layout)
- **Medium**: 768px - 1200px (Resizable panels)
- **Small**: < 768px (Collapsible sidebar)

### Mobile Layout
```
┌─────────────────────────────────────┐
│ [☰] VeriDoc        [🔍]        [⚙️] │
├─────────────────────────────────────┤
│                                     │
│        Content Viewer               │
│                                     │
│  # API Documentation                │
│                                     │
│  This document describes...         │
│                                     │
│  ## Authentication                  │
│                                     │
│  All endpoints require...           │
│                                     │
└─────────────────────────────────────┘
```

## Color Scheme

### Dark Theme (Default)
```css
:root {
    --bg-primary: #1e1e1e;
    --bg-secondary: #252526;
    --bg-tertiary: #2d2d2d;
    --border: #333333;
    --text-primary: #cccccc;
    --text-secondary: #9d9d9d;
    --text-accent: #ffffff;
    --accent-blue: #007acc;
    --accent-green: #28a745;
    --accent-red: #dc3545;
    --accent-yellow: #ffc107;
}
```

### Light Theme (Optional)
```css
:root[data-theme="light"] {
    --bg-primary: #ffffff;
    --bg-secondary: #f8f9fa;
    --bg-tertiary: #e9ecef;
    --border: #dee2e6;
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --text-accent: #000000;
    --accent-blue: #0066cc;
    --accent-green: #198754;
    --accent-red: #dc3545;
    --accent-yellow: #fd7e14;
}
```

## Typography

### Font Stack
```css
body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 
                 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 
                 'Fira Sans', 'Droid Sans', 'Helvetica Neue', 
                 sans-serif;
}

code, pre {
    font-family: 'Fira Code', 'SF Mono', 'Monaco', 'Inconsolata', 
                 'Roboto Mono', 'Source Code Pro', monospace;
}
```

### Font Sizes
- **H1**: 28px (1.75rem)
- **H2**: 22px (1.375rem)
- **H3**: 18px (1.125rem)
- **Body**: 14px (0.875rem)
- **Small**: 12px (0.75rem)
- **Code**: 13px (0.8125rem)

## Keyboard Shortcuts

### Navigation
- **Ctrl+P**: Quick file finder
- **Ctrl+Shift+F**: Global search
- **Ctrl+B**: Toggle file tree
- **Ctrl+`**: Toggle terminal
- **Ctrl+1**: Focus file tree
- **Ctrl+2**: Focus content viewer

### Content
- **Ctrl+F**: Find in file
- **Ctrl+G**: Go to line
- **Ctrl+K**: Copy file path
- **Ctrl+R**: Refresh content
- **Ctrl+Plus**: Zoom in
- **Ctrl+Minus**: Zoom out

### Terminal
- **Ctrl+Shift+C**: Copy selection
- **Ctrl+Shift+V**: Paste
- **Ctrl+Shift+T**: New terminal
- **Ctrl+D**: Close terminal

## Accessibility

### ARIA Labels
```html
<div class="file-tree" role="tree" aria-label="Project files">
    <div class="tree-item" role="treeitem" aria-expanded="true">
        <span class="tree-icon" aria-hidden="true">📁</span>
        <span class="tree-label">docs</span>
    </div>
</div>
```

### Keyboard Navigation
- **Tab**: Navigate between panels
- **Arrow keys**: Navigate within panels
- **Enter**: Activate selected item
- **Escape**: Close dialogs/panels

### Screen Reader Support
- Semantic HTML structure
- Proper heading hierarchy
- Alt text for images
- Descriptive link text

## Performance Considerations

### Rendering Optimization
- **Virtual scrolling**: For large file lists
- **Lazy loading**: Load content on demand
- **Debounced search**: Reduce API calls
- **Cached rendering**: Reuse rendered content

### Memory Management
- **Component cleanup**: Remove event listeners
- **Image optimization**: Compress and lazy load
- **Cache limits**: Bounded memory usage
- **Garbage collection**: Periodic cleanup

## Animation and Transitions

### Subtle Animations
```css
.tree-item {
    transition: background-color 0.2s ease;
}

.content-viewer {
    transition: opacity 0.3s ease;
}

.panel-resize {
    transition: width 0.2s ease;
}
```

### Loading States
```css
.loading {
    opacity: 0.6;
    pointer-events: none;
}

.loading::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 20px;
    height: 20px;
    border: 2px solid #333;
    border-top: 2px solid #007acc;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
```

## Error States

### Error Message Display
```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️  Error Loading File                                      │
│                                                             │
│ Could not load 'docs/missing.md'                           │
│ File not found or access denied.                           │
│                                                             │
│ [Try Again]  [Go Back]                                      │
└─────────────────────────────────────────────────────────────┘
```

### Error Types
- **File not found**: Clear message with suggested actions
- **Access denied**: Security-appropriate messaging
- **Network error**: Retry options
- **Large file**: Size warning with options

## Settings Panel

### Settings Interface
```
┌─────────────────────────────────────────────────────────────┐
│ Settings                                            [×]     │
├─────────────────────────────────────────────────────────────┤
│ Theme                                                       │
│ ○ Dark  ○ Light  ○ Auto                                    │
│                                                             │
│ Font Size                                                   │
│ [─────●───] 14px                                           │
│                                                             │
│ File Tree                                                   │
│ ☑ Show hidden files                                        │
│ ☑ Auto-expand directories                                  │
│                                                             │
│ Terminal                                                    │
│ ☑ Auto-open terminal                                       │
│ Font: [Fira Code    ▼]                                     │
│                                                             │
│ [Reset to Defaults]                    [Save]              │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Notes

### Component Structure
```javascript
// Main application component
class VeriDocApp {
    constructor() {
        this.fileTree = new FileTree();
        this.contentViewer = new ContentViewer();
        this.terminal = new Terminal();
        this.searchPanel = new SearchPanel();
    }
}

// File tree component
class FileTree {
    render() {
        // Render hierarchical file structure
        // Handle expand/collapse
        // Manage selection state
    }
}

// Content viewer component
class ContentViewer {
    displayFile(path, content, type) {
        // Determine appropriate renderer
        // Display content with syntax highlighting
        // Handle large files with pagination
    }
}
```

### State Management
```javascript
class AppState {
    constructor() {
        this.currentFile = null;
        this.searchQuery = '';
        this.selectedItems = [];
        this.panelSizes = {
            fileTree: 280,
            terminal: 200
        };
    }
    
    updateState(newState) {
        Object.assign(this, newState);
        this.notifyComponents();
    }
}
```