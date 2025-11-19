// Next Inai - Pure Vanilla JavaScript (no Vue 3 or other frameworks)
class NextInai {
    constructor() {
        this.state = {
            messages: [],
            htmlContent: '',
            cssContent: '',
            jsContent: '',
            activeFile: 'html',
            isSelectMode: false,
            selectedElement: null,
            history: [],
            historyIndex: -1,
            isLoading: false
        };
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialContent();
        this.render();
    }

    bindEvents() {
        // Tab switching
        const previewTab = document.getElementById('preview-tab');
        const codeTab = document.getElementById('code-tab');
        
        if (previewTab) previewTab.addEventListener('click', () => this.switchTab('preview'));
        if (codeTab) codeTab.addEventListener('click', () => this.switchTab('code'));

        // File switching in code view
        document.querySelectorAll('.file-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchFile(e.target.dataset.file);
            });
        });

        // Undo/Redo/Refresh
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');
        const refreshBtn = document.getElementById('refresh-btn');
        
        if (undoBtn) undoBtn.addEventListener('click', () => this.undo());
        if (redoBtn) redoBtn.addEventListener('click', () => this.redo());
        if (refreshBtn) refreshBtn.addEventListener('click', () => this.refreshPreview());

        // Export button
        const exportBtn = document.getElementById('export-btn');
        if (exportBtn) exportBtn.addEventListener('click', () => this.exportProject());

        // Editor panel
        const closeEditorBtn = document.getElementById('close-editor');
        if (closeEditorBtn) closeEditorBtn.addEventListener('click', () => this.closeEditor());

        // Chat input
        const chatInput = document.getElementById('chat-input');
        const chatSendBtn = document.getElementById('chat-send');
        
        if (chatSendBtn) {
            chatSendBtn.addEventListener('click', () => this.sendChatMessage());
        }
        
        if (chatInput) {
            chatInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendChatMessage();
                }
            });
        }

        // Message listener from iframe
        window.addEventListener('message', (e) => this.handleIframeMessage(e));
    }

    loadInitialContent() {
        // Default initial content
        this.state.htmlContent = `<header>
    <h1>Welcome to My Website</h1>
    <nav>
        <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>
</header>
    
<main>
    <section id="home">
        <h2>Home Section</h2>
        <p>This is the home section of my website.</p>
    </section>
    
    <section id="about">
        <h2>About Section</h2>
        <p>This is the about section of my website.</p>
    </section>
    
    <section id="contact">
        <h2>Contact Section</h2>
        <p>This is the contact section of my website.</p>
    </section>
</main>
    
<footer>
    <p>&copy; 2024 My Website. All rights reserved.</p>
</footer>`;

        this.state.cssContent = `/* Default styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

header {
    background: #333;
    color: white;
    padding: 1rem 0;
    text-align: center;
}

nav ul {
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}

nav a {
    color: white;
    text-decoration: none;
}

nav a:hover {
    text-decoration: underline;
}

main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}

section {
    margin-bottom: 3rem;
}

footer {
    background: #333;
    color: white;
    text-align: center;
    padding: 1rem 0;
    position: fixed;
    bottom: 0;
    width: 100%;
}`;

        this.state.jsContent = `// Interactive JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add some interactivity
    console.log('Website loaded successfully!');
});`;
    }

    switchTab(tab) {
        const previewTab = document.getElementById('preview-tab');
        const codeTab = document.getElementById('code-tab');
        const previewContent = document.getElementById('preview-content');
        const codeContent = document.getElementById('code-content');

        if (tab === 'preview') {
            if (previewTab) {
                previewTab.classList.add('active');
                previewTab.classList.remove('text-muted-foreground');
            }
            if (codeTab) {
                codeTab.classList.remove('active');
                codeTab.classList.add('text-muted-foreground');
            }
            
            if (previewContent) previewContent.classList.remove('hidden');
            if (codeContent) codeContent.classList.add('hidden');
        } else {
            if (codeTab) {
                codeTab.classList.add('active');
                codeTab.classList.remove('text-muted-foreground');
            }
            if (previewTab) {
                previewTab.classList.remove('active');
                previewTab.classList.add('text-muted-foreground');
            }
            
            if (codeContent) codeContent.classList.remove('hidden');
            if (previewContent) previewContent.classList.add('hidden');
            
            this.updateCodeDisplay();
        }
    }

    switchFile(file) {
        this.state.activeFile = file;
        
        // Update button styles
        document.querySelectorAll('.file-btn').forEach(btn => {
            if (btn.dataset.file === file) {
                btn.classList.add('active');
                btn.classList.remove('text-gray-300');
            } else {
                btn.classList.remove('active');
                btn.classList.add('text-gray-300');
            }
        });
        
        this.updateCodeDisplay();
    }

    updateCodeDisplay() {
        const codeDisplay = document.getElementById('code-display');
        if (!codeDisplay) return;
        
        let content = '';
        let language = '';

        switch (this.state.activeFile) {
            case 'html':
                content = this.getHtmlFileContent();
                language = 'html';
                break;
            case 'css':
                content = this.state.cssContent;
                language = 'css';
                break;
            case 'js':
                content = this.state.jsContent;
                language = 'javascript';
                break;
        }

        codeDisplay.innerHTML = `<code class="language-${language}">${this.escapeHtml(content)}</code>`;
    }

    getHtmlFileContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Next Inai Page</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
${this.state.htmlContent}
    <script src="script.js"></script>
</body>
</html>`;
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    refreshPreview() {
        const iframe = document.getElementById('preview-iframe');
        if (iframe) {
            const blob = new Blob([this.getHtmlFileContent().replace('<link rel="stylesheet" href="styles.css">', `<style>${this.state.cssContent}</style>`).replace('<script src="script.js">', `<script>${this.state.jsContent}</script>`)], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            iframe.src = url;
            
            // Clean up the URL after loading
            iframe.onload = () => URL.revokeObjectURL(url);
        }
    }

    undo() {
        if (this.state.historyIndex > 0) {
            this.state.historyIndex--;
            const previousState = this.state.history[this.state.historyIndex];
            this.state.htmlContent = previousState.html;
            this.state.cssContent = previousState.css;
            this.state.jsContent = previousState.js;
            this.updateUndoRedoButtons();
            this.refreshPreview();
            this.updateCodeDisplay();
        }
    }

    redo() {
        if (this.state.historyIndex < this.state.history.length - 1) {
            this.state.historyIndex++;
            const nextState = this.state.history[this.state.historyIndex];
            this.state.htmlContent = nextState.html;
            this.state.cssContent = nextState.css;
            this.state.jsContent = nextState.js;
            this.updateUndoRedoButtons();
            this.refreshPreview();
            this.updateCodeDisplay();
        }
    }

    updateUndoRedoButtons() {
        const undoBtn = document.getElementById('undo-btn');
        const redoBtn = document.getElementById('redo-btn');
        
        if (undoBtn) undoBtn.disabled = this.state.historyIndex <= 0;
        if (redoBtn) redoBtn.disabled = this.state.historyIndex >= this.state.history.length - 1;
    }

    pushHistory() {
        const currentState = {
            html: this.state.htmlContent,
            css: this.state.cssContent,
            js: this.state.jsContent
        };
        
        // Remove any states after current index
        this.state.history = this.state.history.slice(0, this.state.historyIndex + 1);
        
        // Add new state
        this.state.history.push(currentState);
        this.state.historyIndex++;
        
        // Limit history size
        if (this.state.history.length > 50) {
            this.state.history.shift();
            this.state.historyIndex--;
        }
        
        this.updateUndoRedoButtons();
    }

    async sendChatMessage() {
        const textarea = document.getElementById('chat-input');
        const message = textarea.value.trim();
        
        if (!message || this.state.isLoading) return;
        
        // Add user message
        this.addMessage('user', message);
        textarea.value = '';
        
        this.state.isLoading = true;
        this.render();
        
        try {
            // Simulate AI response (in real app, this would call an API)
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const response = this.generateMockResponse(message);
            this.addMessage('assistant', response);
            
            // Update content based on response
            this.updateContentFromResponse(response);
            
        } catch (error) {
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            this.showToast('Error generating response', 'destructive');
        } finally {
            this.state.isLoading = false;
            this.render();
        }
    }

    addMessage(role, content) {
        this.state.messages.push({ role, content, timestamp: Date.now() });
        this.renderChatMessages();
    }

    renderChatMessages() {
        const chatMessages = document.querySelector('.chat-messages');
        if (!chatMessages) return;
        
        chatMessages.innerHTML = this.state.messages.map(msg => `
            <div class="message ${msg.role}">
                <div class="message-content">
                    ${this.escapeHtml(msg.content)}
                </div>
            </div>
        `).join('');
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    generateMockResponse(message) {
        // Simple mock response generator
        const responses = [
            "I've created a modern landing page with a hero section, features, and contact form.",
            "Here's a portfolio website with project galleries and smooth animations.",
            "I've designed an e-commerce product page with image gallery and purchase options.",
            "This is a clean blog layout with article cards and sidebar navigation."
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    updateContentFromResponse(response) {
        // Simple content update based on response
        if (response.includes('landing page')) {
            this.state.htmlContent = `<header class="hero">
    <h1>Welcome to Our Product</h1>
    <p>Transform your ideas into reality</p>
    <button class="cta-button">Get Started</button>
</header>
<section class="features">
    <div class="feature">
        <h3>Feature 1</h3>
        <p>Description of feature 1</p>
    </div>
    <div class="feature">
        <h3>Feature 2</h3>
        <p>Description of feature 2</p>
    </div>
</section>`;
            
            this.state.cssContent += `
.hero {
    text-align: center;
    padding: 4rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.cta-button {
    background: white;
    color: #667eea;
    border: none;
    padding: 1rem 2rem;
    border-radius: 0.5rem;
    font-weight: bold;
    cursor: pointer;
}`;
        }
        
        this.pushHistory();
        this.refreshPreview();
        this.updateCodeDisplay();
    }

    handleIframeMessage(event) {
        if (event.data.type === 'nextinai-select') {
            this.state.selectedElement = event.data;
            this.openEditor();
        }
    }

    openEditor() {
        const editorPanel = document.getElementById('editor-panel');
        if (editorPanel) {
            editorPanel.classList.remove('hidden');
            this.renderEditor();
        }
    }

    closeEditor() {
        const editorPanel = document.getElementById('editor-panel');
        if (editorPanel) {
            editorPanel.classList.add('hidden');
        }
        this.state.selectedElement = null;
    }

    renderEditor() {
        const editorContent = document.getElementById('editor-content');
        if (!editorContent || !this.state.selectedElement) return;
        
        editorContent.innerHTML = `
            <div class="editor-content">
                <div class="editor-header">
                    <h3 class="text-lg font-semibold">Edit Element</h3>
                    <button type="button" id="close-editor" class="icon-button">
                        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                <div class="editor-field">
                    <label>Text Content</label>
                    <input type="text" id="element-text" value="${this.escapeHtml(this.state.selectedElement.textContent || '')}">
                </div>
                <div class="editor-field">
                    <label>Background Color</label>
                    <input type="color" id="element-bg-color" value="#ffffff">
                </div>
                <div class="editor-field">
                    <label>Text Color</label>
                    <input type="color" id="element-text-color" value="#000000">
                </div>
                <button type="button" id="apply-changes" class="w-full">
                    Apply Changes
                </button>
            </div>
        `;
        
        // Re-bind events for the new editor content
        const closeBtn = document.getElementById('close-editor');
        const applyBtn = document.getElementById('apply-changes');
        
        if (closeBtn) closeBtn.addEventListener('click', () => this.closeEditor());
        if (applyBtn) applyBtn.addEventListener('click', () => this.applyEditorChanges());
    }

    applyEditorChanges() {
        // This would apply changes to the selected element
        this.showToast('Changes applied successfully');
        this.closeEditor();
    }

    showToast(message, variant = 'default') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toastId = 'toast-' + Date.now();
        
        const toast = document.createElement('div');
        toast.id = toastId;
        toast.className = `toast ${variant === 'destructive' ? 'toast-destructive' : ''}`;
        toast.innerHTML = `
            <div class="toast-description">${this.escapeHtml(message)}</div>
            <button class="toast-close" onclick="document.getElementById('${toastId}').remove()">
                <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            const element = document.getElementById(toastId);
            if (element) element.remove();
        }, 5000);
    }

    exportProject() {
        // Create a zip file with the project
        const htmlContent = this.getHtmlFileContent();
        const cssContent = this.state.cssContent;
        const jsContent = this.state.jsContent;
        
        // Simple download simulation (in real app, you'd use JSZip)
        const files = {
            'index.html': htmlContent,
            'styles.css': cssContent,
            'script.js': jsContent
        };
        
        // Create a simple text file with all content for now
        const allContent = `=== index.html ===\n${htmlContent}\n\n=== styles.css ===\n${cssContent}\n\n=== script.js ===\n${jsContent}`;
        
        const blob = new Blob([allContent], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'next-inai-project.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Project exported successfully!');
    }

    render() {
        this.renderChatMessages();
        this.updateCodeDisplay();
        this.refreshPreview();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.nextInai = new NextInai();
});
