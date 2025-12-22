'use client';

import { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import styles from './MonacoCodeViewer.module.css';
import * as api from '@/lib/api';

interface MonacoCodeViewerProps {
    sessionId: string;
}

interface CodeFile {
    path: string;
    type: 'html' | 'css' | 'javascript';
    content: string;
}

export default function MonacoCodeViewer({ sessionId }: MonacoCodeViewerProps) {
    const [files, setFiles] = useState<CodeFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<CodeFile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadFiles();
    }, [sessionId]);

    const loadFiles = async () => {
        try {
            setLoading(true);
            const preview = await api.getPreviewUrl(sessionId);
            const fileList = preview.files || [];

            // Load content for each file
            const loadedFiles: CodeFile[] = [];
            for (const filePath of fileList) {
                try {
                    const fileData = await api.getFileContent(sessionId, filePath);
                    loadedFiles.push({
                        path: filePath,
                        type: fileData.file_type as 'html' | 'css' | 'javascript',
                        content: fileData.content
                    });
                } catch (err) {
                    console.error(`Failed to load ${filePath}:`, err);
                }
            }

            setFiles(loadedFiles);
            if (loadedFiles.length > 0) {
                // Select index.html by default
                const indexFile = loadedFiles.find(f => f.path === 'index.html') || loadedFiles[0];
                setSelectedFile(indexFile);
            }
        } catch (err) {
            setError('Failed to load code files');
            console.error(err);
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
                <p>No code files available</p>
            </div>
        );
    }

    return (
        <div className={styles.monacoViewer}>
            {/* File Tabs */}
            <div className={styles.fileTabs}>
                {files.map((file) => (
                    <button
                        key={file.path}
                        className={`${styles.fileTab} ${selectedFile?.path === file.path ? styles.active : ''}`}
                        onClick={() => setSelectedFile(file)}
                    >
                        <span className={styles.fileIcon}>{getFileIcon(file.path)}</span>
                        <span className={styles.fileName}>{file.path}</span>
                    </button>
                ))}
            </div>

            {/* Editor Header */}
            {selectedFile && (
                <div className={styles.editorHeader}>
                    <div className={styles.fileInfo}>
                        <span className={styles.fileIcon}>{getFileIcon(selectedFile.path)}</span>
                        <span className={styles.filePath}>{selectedFile.path}</span>
                        <span className={styles.fileType}>{selectedFile.type.toUpperCase()}</span>
                    </div>
                    <div className={styles.actions}>
                        <button onClick={handleCopy} className={styles.actionBtn}>
                            📋 Copy
                        </button>
                        <button onClick={handleDownload} className={styles.actionBtn}>
                            ⬇ Download
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
                        value={selectedFile.content}
                        theme="vs-dark"
                        loading={
                            <div className={styles.loading}>
                                <div className={styles.spinner}></div>
                                <p>Loading editor...</p>
                            </div>
                        }
                        options={{
                            readOnly: true,
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
                            console.log('Monaco Editor mounted');
                        }}
                    />
                </div>
            )}
        </div>
    );
}
