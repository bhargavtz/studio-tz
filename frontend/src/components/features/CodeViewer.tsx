'use client';

import { useState, useEffect } from 'react';
import styles from './CodeViewer.module.css';
import * as api from '@/lib/api';

interface CodeViewerProps {
    sessionId: string;
}

type FileType = 'html' | 'css' | 'javascript';

interface CodeFile {
    path: string;
    type: FileType;
    content: string;
}

export default function CodeViewer({ sessionId }: CodeViewerProps) {
    const [files, setFiles] = useState<CodeFile[]>([]);
    const [selectedFile, setSelectedFile] = useState<CodeFile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [copied, setCopied] = useState(false);

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
                        type: fileData.file_type as FileType,
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

    const handleCopy = async () => {
        if (!selectedFile) return;

        try {
            await navigator.clipboard.writeText(selectedFile.content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
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

    const getFileIcon = (type: FileType) => {
        switch (type) {
            case 'html': return '📄';
            case 'css': return '🎨';
            case 'javascript': return '⚡';
            default: return '📝';
        }
    };

    const getLanguageClass = (type: FileType) => {
        switch (type) {
            case 'html': return 'language-html';
            case 'css': return 'language-css';
            case 'javascript': return 'language-js';
            default: return '';
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

    if (error) {
        return (
            <div className={styles.error}>
                <p>{error}</p>
                <button onClick={loadFiles}>Retry</button>
            </div>
        );
    }

    if (files.length === 0) {
        return (
            <div className={styles.empty}>
                <p>No code files generated yet.</p>
                <p>Generate your website first to view the code.</p>
            </div>
        );
    }

    return (
        <div className={styles.codeViewer}>
            <div className={styles.header}>
                <h3>💻 Generated Code</h3>
                <p>View and download your website's source code</p>
            </div>

            <div className={styles.fileList}>
                {files.map((file) => (
                    <button
                        key={file.path}
                        className={`${styles.fileButton} ${selectedFile?.path === file.path ? styles.active : ''}`}
                        onClick={() => setSelectedFile(file)}
                    >
                        <span className={styles.fileIcon}>{getFileIcon(file.type)}</span>
                        <span className={styles.fileName}>{file.path}</span>
                    </button>
                ))}
            </div>

            {selectedFile && (
                <div className={styles.codeContainer}>
                    <div className={styles.codeHeader}>
                        <div className={styles.fileInfo}>
                            <span className={styles.fileIcon}>{getFileIcon(selectedFile.type)}</span>
                            <span className={styles.filePath}>{selectedFile.path}</span>
                            <span className={styles.fileType}>{selectedFile.type.toUpperCase()}</span>
                        </div>
                        <div className={styles.actions}>
                            <button onClick={handleCopy} className={styles.actionBtn}>
                                {copied ? '✓ Copied!' : '📋 Copy'}
                            </button>
                            <button onClick={handleDownload} className={styles.actionBtn}>
                                ⬇ Download
                            </button>
                        </div>
                    </div>

                    <div className={styles.codeWrapper}>
                        <pre className={styles.codeBlock}>
                            <code className={getLanguageClass(selectedFile.type)}>
                                {selectedFile.content}
                            </code>
                        </pre>
                    </div>

                    <div className={styles.codeFooter}>
                        <span className={styles.lineCount}>
                            {selectedFile.content.split('\n').length} lines
                        </span>
                        <span className={styles.charCount}>
                            {selectedFile.content.length} characters
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}
