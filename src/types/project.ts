export type FileNode = {
  id: string;
  name: string;
  type: 'file' | 'folder';
  path: string;
  content?: string;
  children?: FileNode[];
  language?: string;
  isExpanded?: boolean;
};

export type ProjectStructure = {
  root: FileNode;
  activeFileId: string | null;
  openFiles: string[];
};

export type FileOperation = {
  type: 'create' | 'update' | 'delete' | 'rename' | 'move';
  fileId: string;
  payload?: any;
};

export type EditorTab = {
  id: string;
  name: string;
  path: string;
  content: string;
  language: string;
  isDirty: boolean;
};
