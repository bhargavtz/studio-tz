'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import Editor from '@monaco-editor/react';
import styles from './MonacoCodeViewer.module.css';
import * as api from '@/lib/api';
import { FileTree } from '@/components/ui/file-tree';

interface MonacoCodeViewerProps {
    sessionId: string;
}

interface CodeFile {
    path: string;
    type: 'html' | 'css' | 'javascript';
    content: string;
}

interface FileNode {
    name: string;
    type: 'file' | 'folder';
    children?: FileNode[];
    extension?: string;
}

export default function MonacoCodeViewer({ sessionId }: MonacoCodeViewerProps) {
    const [files, setFiles] = useState<CodeFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<CodeFile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        loadFiles();
    }, [sessionId]);

    const buildFileTree = (fileList: CodeFile[]): FileNode[] => {
        const root: FileNode[] = [];
        const folders: Map<string, FileNode> = new Map();

        fileList.forEach(file => {
            const parts = file.path.split('/');

            if (parts.length === 1) {
                // Root level file
                root.push({
                    name: file.path,
                    type: 'file',
                    extension: file.path.split('.').pop()
                });
            } else {
                // File in folder
                const folderName = parts[0];
                const fileName = parts.slice(1).join('/');

                if (!folders.has(folderName)) {
                    const folderNode: FileNode = {
                        name: folderName,
                        type: 'folder',
                        children: []
                    };
                    folders.set(folderName, folderNode);
                    root.push(folderNode);
                }

                folders.get(folderName)!.children!.push({
                    name: fileName,
                    type: 'file',
                    extension: fileName.split('.').pop()
                });
            }
        });

        return root;
    };

    // Memoize file tree to prevent expensive recalculation on every render
    const fileTree = useMemo(() => buildFileTree(files), [files]);

    const loadFiles = async () => {
        try {
            setLoading(true);
            setError('');
            console.log('Loading files for session:', sessionId);

            let preview;
            try {
                preview = await api.getPreviewUrl(sessionId);
            } catch (previewErr) {
                // Website not generated yet
                console.log('Preview not ready:', previewErr);
                setError('Website not generated yet. Generate a website first.');
                setLoading(false);
                return;
            }

            console.log('Preview data:', preview);
            const fileList = preview.files || [];
            console.log('File list:', fileList);

            if (fileList.length === 0) {
                setError('No files generated yet.');
                setLoading(false);
                return;
            }

            // Load content for each file
            const loadedFiles: CodeFile[] = [];
            for (const filePath of fileList) {
                try {
                    console.log('Loading file:', filePath);
                    const fileData = await api.getFileContent(sessionId, filePath);
                    console.log('File data for', filePath, ':', fileData);
                    loadedFiles.push({
                        path: filePath,
                        type: fileData.file_type as 'html' | 'css' | 'javascript',
                        content: fileData.content || '// No content available'
                    });
                } catch (err) {
                    console.error(`Failed to load ${filePath}:`, err);
                }
            }

            console.log('Loaded files:', loadedFiles);
            setFiles(loadedFiles);

            if (loadedFiles.length > 0) {
                // Select index.html by default
                const indexFile = loadedFiles.find(f => f.path === 'index.html') || loadedFiles[0];
                console.log('Selected file:', indexFile);
                setSelectedFile(indexFile);
            }
        } catch (err) {
            setError('Failed to load code files');
            console.error('Load files error:', err);
        } finally {
            setLoading(false);
        }
    };

    const getLanguage = (type: string): string => {
        switch (type) {
            case 'html': return 'html';
            case 'css': return 'css';
            case 'javascript': return 'javascript';
            default: return 'plaintext';
        }
    };

    const getFileIcon = (path: string): string => {
        if (path.endsWith('.html')) return '📄';
        if (path.endsWith('.css')) return '🎨';
        if (path.endsWith('.js')) return '⚡';
        return '📝';
    };

    const handleCopy = async () => {
        if (!selectedFile) return;
        try {
            await navigator.clipboard.writeText(selectedFile.content);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    const handleDownload = () => {
        if (!selectedFile) return;
        const blob = new Blob([selectedFile.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = selectedFile.path;
        a.click();
        URL.revokeObjectURL(url);
    };

    const handleFileSelect = (path: string) => {
        const file = files.find(f => f.path === path);
        if (file) {
            setSelectedFile(file);
            setHasUnsavedChanges(false); // Reset unsaved changes when switching files
        }
    };

    const handleEditorChange = (value: string | undefined) => {
        if (!selectedFile) return;

        // Update the file content in state
        const updatedFile = { ...selectedFile, content: value || '' };
        setSelectedFile(updatedFile);

        // Update in files array
        setFiles(prevFiles =>
            prevFiles.map(f => f.path === selectedFile.path ? updatedFile : f)
        );

        setHasUnsavedChanges(true);
    };

    const handleSave = async () => {
        if (!selectedFile || !hasUnsavedChanges) return;

        try {
            setSaving(true);

            // Call the edit API
            const result = await api.editWebsite(sessionId, {
                edit_type: 'manual',
                file_path: selectedFile.path,
                instruction: `Manual edit to ${selectedFile.path}`,
                value: selectedFile.content
            });

            if (result.success) {
                setHasUnsavedChanges(false);
                console.log('File saved successfully:', result);
            } else {
                throw new Error('Save failed');
            }
        } catch (error) {
            console.error('Failed to save file:', error);
            alert('Failed to save changes. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <div className={styles.loading}>
                <div className={styles.spinner}></div>
                <p>Loading code files...</p>
            </div>
        );
    }

    if (error || files.length === 0) {
        return (
            <div className={styles.empty}>
                <p>{error || 'No code files available'}</p>
            </div>
        );
    }

    return (
        <div className={styles.monacoViewer}>
            {/* File Tree Sidebar */}
            <div className={styles.sidebar}>
                <FileTree
                    data={fileTree}
                    onFileSelect={handleFileSelect}
                    className="h-full w-full rounded-none border-none bg-transparent p-0"
                />
            </div>

            {/* Editor Section */}
            <div className={styles.editorSection}>

                {/* Editor Header */}
                {selectedFile && (
                    <div className={styles.editorHeader}>
                        <div className={styles.tabContainer}>
                            <div className={styles.activeTab}>
                                <span className={styles.fileIcon}>{getFileIcon(selectedFile.path)}</span>
                                <span className={styles.filePath}>{selectedFile.path}</span>
                            </div>
                        </div>
                        <div className={styles.actions}>
                            <button
                                onClick={handleSave}
                                className={`${styles.actionBtn} ${hasUnsavedChanges ? styles.saveBtn : ''}`}
                                title="Save Changes"
                                disabled={saving || !hasUnsavedChanges}
                            >
                                {saving ? '💾' : '💾'}
                            </button>
                            <button onClick={handleCopy} className={styles.actionBtn} title="Copy to Clipboard">
                                📋
                            </button>
                            <button onClick={handleDownload} className={styles.actionBtn} title="Download File">
                                ⬇
                            </button>
                        </div>
                    </div>
                )}

                {/* Monaco Editor */}
                {selectedFile && (
                    <div className={styles.editorContainer}>
                        <Editor
                            height="100%"
                            language={getLanguage(selectedFile.type)}
                            value={selectedFile.content || '// No content'}
                            theme="vs-dark"
                            onChange={handleEditorChange}
                            loading={
                                <div className={styles.loading}>
                                    <div className={styles.spinner}></div>
                                    <p>Loading editor...</p>
                                </div>
                            }
                            options={{
                                readOnly: false,
                                minimap: { enabled: true },
                                fontSize: 14,
                                lineNumbers: 'on',
                                scrollBeyondLastLine: false,
                                automaticLayout: true,
                                wordWrap: 'on',
                                folding: true,
                                renderWhitespace: 'selection',
                                bracketPairColorization: { enabled: true },
                                scrollbar: {
                                    vertical: 'visible',
                                    horizontal: 'visible',
                                },
                            }}
                            onMount={(editor, monaco) => {
                                // Editor mounted successfully
                                console.log('Monaco Editor mounted with content:', selectedFile.content?.substring(0, 100));
                            }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}
