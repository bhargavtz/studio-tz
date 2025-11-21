import { ProjectManager } from './project-manager';
import { extractBodyContent } from './utils';

/**
 * Synchronizes AI-generated code with the file editor
 * Handles both multi-file and legacy single-file responses
 */

export class AIFileSync {
  private projectManager: ProjectManager;

  constructor() {
    this.projectManager = ProjectManager.getInstance();
  }

  /**
   * Syncs AI response with file editor
   * Handles both multi-file project structures and legacy single-file responses
   */
  syncAIResponse(response: any, isMultiFile: boolean = false): void {
    if (isMultiFile && response.files) {
      this.syncMultiFileResponse(response.files);
    } else {
      this.syncLegacyResponse(response);
    }
  }

  /**
   * Syncs multi-file AI response with the file editor
   */
  private syncMultiFileResponse(files: Array<{ name: string; content: string; type?: string }>): void {
    // Clear existing project structure
    this.clearProject();

    // Validate and filter files
    if (!Array.isArray(files)) {
      console.error('Invalid files array provided to syncMultiFileResponse');
      return;
    }

    // Filter out invalid files and normalize
    const validFiles = files.filter(file => file && typeof file.name === 'string');
    const normalizedFiles = validFiles.map(file => ({
      name: file.name,
      content: file.content || '',
      type: file.type || 'text'
    }));

    if (normalizedFiles.length === 0) {
      console.warn('No valid files to import');
      return;
    }

    // Import the new file structure
    this.projectManager.importProjectStructure(normalizedFiles);

    // Set the main HTML file as active if it exists
    const htmlFile = normalizedFiles.find(file => file.name.endsWith('.html') || file.name.endsWith('.htm'));
    if (htmlFile) {
      const project = this.projectManager.getProject();
      const htmlNode = this.findFileNode(htmlFile.name);
      if (htmlNode) {
        this.projectManager.setActiveFile(htmlNode.id);
      }
    }
  }

  /**
   * Syncs legacy single-file AI response with the file editor
   */
  private syncLegacyResponse(response: any): void {
    const htmlContent = this.extractHtmlContent(response);
    const cssContent = response.css || '';
    const jsContent = response.js || '';

    // Update or create index.html
    if (htmlContent) {
      this.updateOrCreateFile('index.html', htmlContent, 'html');
    }

    // Update or create styles.css
    if (cssContent) {
      this.updateOrCreateFile('styles.css', cssContent, 'css');
    }

    // Update or create script.js
    if (jsContent) {
      this.updateOrCreateFile('script.js', jsContent, 'javascript');
    }

    // Set index.html as active file
    const indexNode = this.findFileNode('index.html');
    if (indexNode) {
      this.projectManager.setActiveFile(indexNode.id);
    }
  }

  /**
   * Updates an existing file or creates it if it doesn't exist
   */
  private updateOrCreateFile(fileName: string, content: string, language: string): void {
    const existingNode = this.findFileNode(fileName);

    if (existingNode) {
      // Update existing file
      this.projectManager.updateFile(existingNode.id, content);
    } else {
      // Create new file in root
      this.projectManager.createFile('root', fileName, content, language);
    }
  }

  /**
   * Syncs a single file during streaming
   * Updates or creates the file immediately without clearing the project
   */
  syncSingleFile(fileName: string, content: string, type: string): void {
    this.updateOrCreateFile(fileName, content, type);

    // Set as active file if it's index.html
    if (fileName === 'index.html') {
      const node = this.findFileNode(fileName);
      if (node) {
        this.projectManager.setActiveFile(node.id);
      }
    }
  }

  /**
   * Finds a file node by its name in the project
   */
  private findFileNode(fileName: string): any {
    const project = this.projectManager.getProject();

    const searchNode = (node: any): any => {
      if (node.type === 'file' && node.name === fileName) {
        return node;
      }

      if (node.children) {
        for (const child of node.children) {
          const found = searchNode(child);
          if (found) return found;
        }
      }

      return null;
    };

    return searchNode(project.root);
  }

  /**
   * Clears the entire project structure
   */
  private clearProject(): void {
    const project = this.projectManager.getProject();

    if (project.root.children) {
      // Delete all children in reverse order
      const children = [...project.root.children];
      for (let i = children.length - 1; i >= 0; i--) {
        const child = children[i];
        if (child.type === 'file') {
          this.projectManager.deleteFile(child.id);
        } else if (child.type === 'folder') {
          this.projectManager.deleteFolder(child.id);
        }
      }
    }
  }

  /**
   * Extracts HTML content from AI response
   * Returns complete HTML if available, otherwise extracts body content for backward compatibility
   */
  private extractHtmlContent(response: any): string {
    // Handle pages format
    if (response.pages?.length > 0) {
      const page = response.pages[0];
      const bodyContent = typeof page.body === 'string' ? page.body : '';

      // Check if it's a complete HTML document
      if (bodyContent.trim().startsWith('<!DOCTYPE') || bodyContent.trim().startsWith('<html')) {
        // Return complete HTML as-is
        return bodyContent;
      }

      // For backward compatibility: extract body content from incomplete HTML
      return extractBodyContent(bodyContent);
    }

    // Handle legacy html field
    if (response.html && typeof response.html === 'string') {
      // Check if it's a complete HTML document
      if (response.html.trim().startsWith('<!DOCTYPE') || response.html.trim().startsWith('<html')) {
        // Return complete HTML as-is
        return response.html;
      }

      // For backward compatibility: extract body content
      return extractBodyContent(response.html);
    }

    return '';
  }

  /**
   * Gets current file contents for legacy compatibility
   */
  getLegacyContents(): { html: string; css: string; js: string } {
    const project = this.projectManager.getProject();
    const contents = { html: '', css: '', js: '' };

    const searchNode = (node: any) => {
      if (node.type === 'file') {
        if (node.name === 'index.html') {
          contents.html = node.content || '';
        } else if (node.name === 'styles.css') {
          contents.css = node.content || '';
        } else if (node.name === 'script.js') {
          contents.js = node.content || '';
        }
      }

      if (node.children) {
        node.children.forEach(searchNode);
      }
    };

    searchNode(project.root);
    return contents;
  }
}
