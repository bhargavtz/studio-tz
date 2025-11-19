'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  File, 
  Folder, 
  FolderOpen, 
  Plus, 
  X, 
  FileText, 
  ChevronRight,
  ChevronDown,
  Search,
  Settings
} from 'lucide-react';
import { FileNode, ProjectStructure } from '@/types/project';
import { ProjectManager } from '@/lib/project-manager';

interface CodeEditorProps {
  className?: string;
}

export function CodeEditor({ className }: CodeEditorProps) {
  const [project, setProject] = useState<ProjectStructure>(() => ProjectManager.getInstance().getProject());
  const [editingFileId, setEditingFileId] = useState<string | null>(null);
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null);
  const [newFileName, setNewFileName] = useState('');
  const [newFolderName, setNewFolderName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const unsubscribe = ProjectManager.getInstance().subscribe(setProject);
    return unsubscribe;
  }, []);

  const handleCreateFile = useCallback((parentId: string) => {
    if (!newFileName.trim()) return;
    
    try {
      ProjectManager.getInstance().createFile(parentId, newFileName, '', 'text');
      setNewFileName('');
      setEditingFileId(null);
    } catch (error) {
      console.error('Failed to create file:', error);
    }
  }, [newFileName]);

  const handleCreateFolder = useCallback((parentId: string) => {
    if (!newFolderName.trim()) return;
    
    try {
      ProjectManager.getInstance().createFolder(parentId, newFolderName);
      setNewFolderName('');
      setEditingFolderId(null);
    } catch (error) {
      console.error('Failed to create folder:', error);
    }
  }, [newFolderName]);

  const handleDeleteFile = useCallback((fileId: string) => {
    try {
      ProjectManager.getInstance().deleteFile(fileId);
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  }, []);

  const handleRenameFile = useCallback((fileId: string, newName: string) => {
    try {
      ProjectManager.getInstance().renameFile(fileId, newName);
    } catch (error) {
      console.error('Failed to rename file:', error);
    }
  }, []);

  const handleSelectFile = useCallback((fileId: string) => {
    try {
      ProjectManager.getInstance().setActiveFile(fileId);
    } catch (error) {
      console.error('Failed to select file:', error);
    }
  }, []);

  const handleCloseFile = useCallback((fileId: string) => {
    try {
      ProjectManager.getInstance().closeFile(fileId);
    } catch (error) {
      console.error('Failed to close file:', error);
    }
  }, []);

  const handleToggleFolder = useCallback((folderId: string) => {
    try {
      ProjectManager.getInstance().toggleFolder(folderId);
    } catch (error) {
      console.error('Failed to toggle folder:', error);
    }
  }, []);

  const getFileIcon = (node: FileNode) => {
    if (node.type === 'folder') {
      return node.isExpanded ? <FolderOpen className="h-4 w-4" /> : <Folder className="h-4 w-4" />;
    }
    
    const iconMap: { [key: string]: JSX.Element } = {
      'html': <FileText className="h-4 w-4 text-orange-500" />,
      'css': <FileText className="h-4 w-4 text-blue-500" />,
      'javascript': <FileText className="h-4 w-4 text-yellow-500" />,
      'typescript': <FileText className="h-4 w-4 text-blue-600" />,
      'jsx': <FileText className="h-4 w-4 text-cyan-500" />,
      'tsx': <FileText className="h-4 w-4 text-cyan-600" />,
      'json': <FileText className="h-4 w-4 text-gray-500" />
    };
    
    return iconMap[node.language || ''] || <File className="h-4 w-4 text-gray-400" />;
  };

  const renderFileTree = (nodes: FileNode[], depth: number = 0): JSX.Element[] => {
    return nodes.map(node => {
      const isActive = project.activeFileId === node.id;
      const isOpen = project.openFiles.includes(node.id);
      
      if (node.type === 'folder') {
        return (
          <div key={node.id}>
            <div 
              className={`flex items-center gap-1 px-2 py-1 hover:bg-gray-800 cursor-pointer rounded`}
              style={{ paddingLeft: `${depth * 12 + 8}px` }}
              onClick={() => handleToggleFolder(node.id)}
            >
              {node.isExpanded ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
              {getFileIcon(node)}
              <span className="text-sm text-gray-300">{node.name}</span>
              <Button
                variant="ghost"
                size="sm"
                className="ml-auto h-6 w-6 p-0 opacity-0 hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation();
                  setEditingFolderId(node.id);
                  setNewFolderName('');
                }}
              >
                <Plus className="h-3 w-3" />
              </Button>
            </div>
            
            {editingFolderId === node.id && (
              <div 
                className="flex items-center gap-1 px-2 py-1"
                style={{ paddingLeft: `${depth * 12 + 20}px` }}
              >
                <Folder className="h-4 w-4 text-gray-400" />
                <Input
                  value={newFolderName}
                  onChange={(e) => setNewFolderName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleCreateFolder(node.id);
                    } else if (e.key === 'Escape') {
                      setEditingFolderId(null);
                      setNewFolderName('');
                    }
                  }}
                  placeholder="Folder name"
                  className="h-6 text-xs"
                  autoFocus
                />
              </div>
            )}
            
            {node.isExpanded && node.children && renderFileTree(node.children, depth + 1)}
          </div>
        );
      }
      
      return (
        <div key={node.id}>
          <div 
            className={`flex items-center gap-1 px-2 py-1 hover:bg-gray-800 cursor-pointer rounded ${
              isActive ? 'bg-gray-800 text-white' : 'text-gray-300'
            }`}
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => handleSelectFile(node.id)}
          >
            {getFileIcon(node)}
            <span className="text-sm flex-1">{node.name}</span>
            {isActive && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 opacity-0 hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation();
                  handleCloseFile(node.id);
                }}
              >
                <X className="h-3 w-3" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 opacity-0 hover:opacity-100"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteFile(node.id);
              }}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        </div>
      );
    });
  };

  const activeFile = project.activeFileId ? ProjectManager.getInstance().findNodePublic(project.activeFileId) : null;
  const activeContent = activeFile?.content || '';

  return (
    <div className={`flex h-full bg-gray-950 ${className}`}>
      {/* File Explorer */}
      <div className="w-64 border-r border-gray-800 flex flex-col">
        <div className="p-3 border-b border-gray-800">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-300">Explorer</h3>
            <div className="flex gap-1">
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={() => setEditingFileId('root')}
              >
                <Plus className="h-3 w-3" />
              </Button>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0">
                <Settings className="h-3 w-3" />
              </Button>
            </div>
          </div>
          
          <div className="relative">
            <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 h-3 w-3 text-gray-500" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search files..."
              className="pl-7 h-7 text-xs"
            />
          </div>
        </div>
        
        <div className="flex-1 overflow-auto">
          {editingFileId === 'root' && (
            <div className="flex items-center gap-1 px-2 py-1">
              <File className="h-4 w-4 text-gray-400" />
              <Input
                value={newFileName}
                onChange={(e) => setNewFileName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleCreateFile('root');
                  } else if (e.key === 'Escape') {
                    setEditingFileId(null);
                    setNewFileName('');
                  }
                }}
                placeholder="File name"
                className="h-6 text-xs"
                autoFocus
              />
            </div>
          )}
          
          {project.root.children && renderFileTree(project.root.children)}
        </div>
        
        {/* Open Files Tabs */}
        <div className="border-t border-gray-800">
          <div className="px-3 py-2">
            <h4 className="text-xs font-medium text-gray-400 mb-2">Open Files</h4>
            <div className="flex flex-wrap gap-1">
              {project.openFiles.map(fileId => {
                const file = ProjectManager.getInstance().findNodePublic(fileId);
                if (!file) return null;
                
                const isActive = project.activeFileId === fileId;
                return (
                  <Button
                    key={fileId}
                    variant={isActive ? "secondary" : "ghost"}
                    size="sm"
                    className={`h-6 px-2 text-xs ${isActive ? 'bg-gray-800' : 'text-gray-400'}`}
                    onClick={() => handleSelectFile(fileId)}
                  >
                    {file.name}
                    <X 
                      className="h-3 w-3 ml-1 opacity-0 hover:opacity-100" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCloseFile(fileId);
                      }}
                    />
                  </Button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      
      {/* Code Editor Area */}
      <div className="flex-1 flex flex-col">
        {activeFile ? (
          <>
            <div className="border-b border-gray-800 px-4 py-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {getFileIcon(activeFile)}
                  <span className="text-sm font-medium text-gray-300">{activeFile.name}</span>
                </div>
                <div className="text-xs text-gray-500">
                  {activeFile.language}
                </div>
              </div>
            </div>
            
            <div className="flex-1 overflow-auto">
              <textarea
                value={activeContent}
                onChange={(e) => {
                  try {
                    ProjectManager.getInstance().updateFile(activeFile.id, e.target.value);
                  } catch (error) {
                    console.error('Failed to update file:', error);
                  }
                }}
                className="w-full h-full p-4 bg-gray-950 text-gray-300 font-mono text-sm resize-none focus:outline-none"
                placeholder="Start typing..."
                spellCheck={false}
              />
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <File className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">No file selected</p>
              <p className="text-xs mt-2">Select a file from the explorer or create a new one</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
