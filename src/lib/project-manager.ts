import { FileNode, ProjectStructure, FileOperation } from '@/types/project';
import { initialPages } from '@/lib/initial-content';

export class ProjectManager {
  private static instance: ProjectManager;
  private project: ProjectStructure;
  private listeners: ((project: ProjectStructure) => void)[] = [];

  private constructor() {
    this.project = this.initializeProject();
  }

  static getInstance(): ProjectManager {
    if (!ProjectManager.instance) {
      ProjectManager.instance = new ProjectManager();
    }
    return ProjectManager.instance;
  }

  private initializeProject(): ProjectStructure {
    const root: FileNode = {
      id: 'root',
      name: 'project',
      type: 'folder',
      path: '/',
      isExpanded: true,
      children: [
        {
          id: 'html',
          name: 'index.html',
          type: 'file',
          path: '/index.html',
          content: initialPages[0]?.body || '',
          language: 'html'
        },
        {
          id: 'css',
          name: 'styles.css',
          type: 'file',
          path: '/styles.css',
          content: '/* CSS styles */',
          language: 'css'
        },
        {
          id: 'js',
          name: 'script.js',
          type: 'file',
          path: '/script.js',
          content: '// JavaScript code',
          language: 'javascript'
        }
      ]
    };

    return {
      root,
      activeFileId: 'html',
      openFiles: ['html']
    };
  }

  getProject(): ProjectStructure {
    return { ...this.project };
  }

  subscribe(listener: (project: ProjectStructure) => void) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  private notify() {
    this.listeners.forEach(listener => listener(this.getProject()));
  }

  createFile(parentId: string, name: string, content: string = '', language: string = 'text'): FileNode {
    const parent = this.findNode(parentId);
    if (!parent || parent.type !== 'folder') {
      throw new Error('Parent folder not found');
    }

    const fileId = this.generateId();
    const path = `${parent.path === '/' ? '' : parent.path}/${name}`;

    const newFile: FileNode = {
      id: fileId,
      name,
      type: 'file',
      path,
      content,
      language
    };

    if (!parent.children) {
      parent.children = [];
    }
    parent.children.push(newFile);

    this.notify();
    return newFile;
  }

  createFolder(parentId: string, name: string): FileNode {
    const parent = this.findNode(parentId);
    if (!parent || parent.type !== 'folder') {
      throw new Error('Parent folder not found');
    }

    const folderId = this.generateId();
    const path = `${parent.path === '/' ? '' : parent.path}/${name}`;

    const newFolder: FileNode = {
      id: folderId,
      name,
      type: 'folder',
      path,
      isExpanded: false,
      children: []
    };

    if (!parent.children) {
      parent.children = [];
    }
    parent.children.push(newFolder);

    this.notify();
    return newFolder;
  }

  deleteFile(fileId: string) {
    const node = this.findNode(fileId);
    if (!node) {
      throw new Error('File not found');
    }

    const parent = this.findParent(fileId);
    if (parent && parent.children) {
      parent.children = parent.children.filter(child => child.id !== fileId);

      // Remove from open files and active file
      this.project.openFiles = this.project.openFiles.filter(id => id !== fileId);
      if (this.project.activeFileId === fileId) {
        this.project.activeFileId = this.project.openFiles[0] || null;
      }

      this.notify();
    }
  }

  deleteFolder(folderId: string): void {
    const node = this.findNode(folderId);
    if (!node || node.type !== 'folder') {
      throw new Error('Folder not found');
    }

    const parent = this.findParent(folderId);
    if (!parent || !parent.children) {
      throw new Error('Parent folder not found');
    }

    // Remove folder from parent
    parent.children = parent.children.filter(child => child.id !== folderId);

    // Remove any open files that were in this folder
    const removeOpenFilesInFolder = (folderNode: FileNode) => {
      if (folderNode.type === 'file') {
        this.project.openFiles = this.project.openFiles.filter(id => id !== folderNode.id);
        if (this.project.activeFileId === folderNode.id) {
          this.project.activeFileId = this.project.openFiles[0] || null;
        }
      } else if (folderNode.children) {
        folderNode.children.forEach(removeOpenFilesInFolder);
      }
    };

    removeOpenFilesInFolder(node);
    this.notify();
  }

  updateFile(fileId: string, content: string) {
    const node = this.findNode(fileId);
    if (!node || node.type !== 'file') {
      throw new Error('File not found or not a file');
    }

    node.content = content;
    this.notify();
  }

  renameFile(fileId: string, newName: string) {
    const node = this.findNode(fileId);
    if (!node) {
      throw new Error('File not found');
    }

    node.name = newName;

    // Update path
    const parent = this.findParent(fileId);
    if (parent) {
      const parentPath = parent.path === '/' ? '' : parent.path;
      node.path = `${parentPath}/${newName}`;
    }

    this.notify();
  }

  setActiveFile(fileId: string) {
    const node = this.findNode(fileId);
    if (!node || node.type !== 'file') {
      throw new Error('File not found or not a file');
    }

    this.project.activeFileId = fileId;

    // Add to open files if not already there
    if (!this.project.openFiles.includes(fileId)) {
      this.project.openFiles.push(fileId);
    }

    this.notify();
  }

  closeFile(fileId: string) {
    this.project.openFiles = this.project.openFiles.filter(id => id !== fileId);

    // If closing the active file, switch to another open file
    if (this.project.activeFileId === fileId) {
      this.project.activeFileId = this.project.openFiles[0] || null;
    }

    this.notify();
  }

  toggleFolder(folderId: string) {
    const node = this.findNode(folderId);
    if (!node || node.type !== 'folder') {
      throw new Error('Folder not found');
    }

    node.isExpanded = !node.isExpanded;
    this.notify();
  }

  getFileContent(fileId: string): string {
    const node = this.findNode(fileId);
    if (!node || node.type !== 'file') {
      throw new Error('File not found or not a file');
    }
    return node.content || '';
  }

  private findNode(id: string): FileNode | null {
    return this.searchNode(this.project.root, id);
  }

  // Public method to find node for external components
  public findNodePublic(id: string): FileNode | null {
    return this.searchNode(this.project.root, id);
  }

  public getFileByPath(path: string): FileNode | null {
    const searchByPath = (node: FileNode): FileNode | null => {
      if (node.type === 'file' && node.path === path) {
        return node;
      }
      if (node.children) {
        for (const child of node.children) {
          const found = searchByPath(child);
          if (found) return found;
        }
      }
      return null;
    };
    return searchByPath(this.project.root);
  }

  private findParent(id: string): FileNode | null {
    return this.searchParent(this.project.root, id);
  }

  private searchNode(node: FileNode, id: string): FileNode | null {
    if (node.id === id) {
      return node;
    }

    if (node.children) {
      for (const child of node.children) {
        const found = this.searchNode(child, id);
        if (found) {
          return found;
        }
      }
    }

    return null;
  }

  private searchParent(node: FileNode, id: string, parent: FileNode | null = null): FileNode | null {
    if (node.id === id) {
      return parent;
    }

    if (node.children) {
      for (const child of node.children) {
        const found = this.searchParent(child, id, node);
        if (found) {
          return found;
        }
      }
    }

    return null;
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  // Import/Export functionality for AI responses
  importProjectStructure(files: Array<{ name: string; content: string; type: string }>) {
    // Validate input
    if (!Array.isArray(files)) {
      console.error('Invalid files array provided to importProjectStructure');
      return;
    }

    const newRoot: FileNode = {
      id: 'root',
      name: 'project',
      type: 'folder',
      path: '/',
      children: []
    };

    const folders: { [key: string]: FileNode } = {
      '/': newRoot
    };

    files.forEach(file => {
      // Validate file object
      if (!file || !file.name) {
        console.error('Invalid file object:', file);
        return;
      }

      const parts = file.name.split('/');
      const fileName = parts.pop() || 'untitled';
      const folderPath = parts.join('/');

      // Create folder structure
      if (folderPath && !folders[folderPath]) {
        const currentPath = '';
        parts.forEach((part, index) => {
          const path = parts.slice(0, index + 1).join('/');
          if (!folders[path]) {
            const parentId = index === 0 ? 'root' : folders[parts.slice(0, index).join('/')].id;
            const folder = this.createFolder(parentId, part);
            folders[path] = folder;
          }
        });
      }

      // Create file
      const parentId = folderPath ? folders[folderPath].id : 'root';
      const language = this.getLanguageFromExtension(fileName);
      this.createFile(parentId, fileName, file.content, language);
    });

    this.notify();
  }

  exportProjectStructure(): Array<{ name: string; content: string; type: string }> {
    const files: Array<{ name: string; content: string; type: string }> = [];

    const traverse = (node: FileNode, basePath: string = '') => {
      if (node.type === 'file' && node.content) {
        files.push({
          name: node.path.substring(1), // Remove leading slash
          content: node.content,
          type: node.language || 'text'
        });
      } else if (node.type === 'folder' && node.children) {
        node.children.forEach(child => traverse(child, basePath));
      }
    };

    this.project.root.children?.forEach(child => traverse(child));
    return files;
  }

  private getLanguageFromExtension(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    const languageMap: { [key: string]: string } = {
      'html': 'html',
      'htm': 'html',
      'css': 'css',
      'js': 'javascript',
      'jsx': 'jsx',
      'ts': 'typescript',
      'tsx': 'tsx',
      'json': 'json',
      'md': 'markdown',
      'py': 'python',
      'php': 'php',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'go': 'go',
      'rs': 'rust',
      'sql': 'sql',
      'xml': 'xml',
      'yaml': 'yaml',
      'yml': 'yaml',
      'sh': 'bash',
      'bash': 'bash',
      'zsh': 'bash'
    };

    return languageMap[ext || ''] || 'text';
  }
}
