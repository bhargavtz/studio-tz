'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useAuth, UserButton } from '@clerk/nextjs';
import styles from './dashboard.module.css';
import * as api from '@/lib/api';
import type { DashboardProject, StorageSummary } from '@/lib/api';

export default function DashboardPage() {
    const router = useRouter();
    const { user, isLoaded: userLoaded } = useUser();
    const { getToken } = useAuth();

    const [projects, setProjects] = useState<DashboardProject[]>([]);
    const [storage, setStorage] = useState<StorageSummary | null>(null);
    const [pagination, setPagination] = useState({ page: 1, limit: 12, total: 0, pages: 0 });
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('created_at_desc');
    const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
    const [renamingProject, setRenamingProject] = useState<string | null>(null);
    const [renameValue, setRenameValue] = useState('');

    const loadDashboard = useCallback(async (page = 1) => {
        try {
            setIsLoading(true);
            setError('');

            const token = user?.id || '';

            const [projectsData, storageData] = await Promise.all([
                api.getDashboardProjects(token, page, pagination.limit, sortBy, searchQuery || undefined),
                api.getStorageSummary(token)
            ]);

            setProjects(projectsData.projects);
            setPagination(projectsData.pagination);
            setStorage(storageData);
        } catch (err) {
            console.error('Failed to load dashboard:', err);
            setError('Failed to load your projects. Please try again.');
        } finally {
            setIsLoading(false);
        }
    }, [user?.id, pagination.limit, sortBy, searchQuery]);

    useEffect(() => {
        if (userLoaded && user) {
            loadDashboard();
        } else if (userLoaded && !user) {
            router.push('/');
        }
    }, [userLoaded, user, loadDashboard, router]);

    const handleSearch = (e: React.FormEvent) => {
        e.preventDefault();
        loadDashboard(1);
    };

    const handleSortChange = (newSort: string) => {
        setSortBy(newSort);
        // Will trigger reload via useEffect
    };

    const handleDeleteProject = async (sessionId: string) => {
        try {
            const token = user?.id || '';
            await api.deleteProject(token, sessionId);
            setDeleteConfirm(null);
            loadDashboard(pagination.page);
        } catch (err) {
            console.error('Failed to delete project:', err);
            setError('Failed to delete project. Please try again.');
        }
    };

    const handleRenameStart = (sessionId: string, currentTitle: string) => {
        setRenamingProject(sessionId);
        setRenameValue(currentTitle);
    };

    const handleRenameCancel = () => {
        setRenamingProject(null);
        setRenameValue('');
    };

    const handleRenameSave = async (sessionId: string) => {
        if (!renameValue.trim()) {
            handleRenameCancel();
            return;
        }

        try {
            const token = user?.id || '';
            await api.renameProject(token, sessionId, renameValue.trim());
            setRenamingProject(null);
            setRenameValue('');
            loadDashboard(pagination.page);
        } catch (err) {
            console.error('Failed to rename project:', err);
            setError('Failed to rename project. Please try again.');
        }
    };

    const handleNewProject = async () => {
        try {
            setIsLoading(true);
            const token = user?.id || '';
            const sessionData = await api.createSession(token);
            router.push(`/builder/${sessionData.session_id}`);
        } catch (err) {
            console.error('Failed to create project:', err);
            setError('Failed to create new project. Please try again.');
            setIsLoading(false);
        }
    };

    const handleOpenProject = (sessionId: string) => {
        router.push(`/builder/${sessionId}`);
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'website_generated':
                return styles.statusComplete;
            case 'editing':
                return styles.statusEditing;
            case 'blueprint_confirmed':
                return styles.statusProgress;
            default:
                return styles.statusDraft;
        }
    };

    const getStatusLabel = (status: string) => {
        switch (status) {
            case 'website_generated':
                return 'Complete';
            case 'editing':
                return 'Editing';
            case 'blueprint_confirmed':
                return 'In Progress';
            case 'blueprint_generated':
                return 'Blueprint Ready';
            default:
                return 'Draft';
        }
    };

    if (!userLoaded) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p>Loading...</p>
            </div>
        );
    }

    return (
        <main className={styles.main}>
            {/* Header */}
            <header className={styles.header}>
                <div className={styles.headerContent}>
                    <div className={styles.logo}>
                        <span className={styles.logoIcon}>✦</span>
                        <span className={styles.logoText}>NCD INAI</span>
                    </div>
                    <div className={styles.headerRight}>
                        <button className={styles.cloudBtn} onClick={() => router.push('/cloud')}>
                            <span>☁️</span>
                            <span>Cloud</span>
                        </button>
                        <button className={styles.newProjectBtn} onClick={handleNewProject}>
                            <span>+</span>
                            <span>New Project</span>
                        </button>
                        <UserButton
                            appearance={{
                                elements: {
                                    avatarBox: "w-10 h-10 border-2 border-purple-500"
                                }
                            }}
                            afterSignOutUrl="/"
                        />
                    </div>
                </div>
            </header>

            {/* Storage Banner */}
            {storage && (
                <div className={`${styles.storageBanner} ${storage.is_at_limit ? styles.storageCritical : storage.is_near_limit ? styles.storageWarning : ''}`}>
                    <div className={styles.storageInfo}>
                        <span className={styles.storageLabel}>Storage Used</span>
                        <span className={styles.storageValue}>
                            {storage.storage_used_mb}MB / {storage.storage_limit_mb}MB
                        </span>
                    </div>
                    <div className={styles.storageBarContainer}>
                        <div
                            className={styles.storageBar}
                            style={{ width: `${Math.min(storage.usage_percentage, 100)}%` }}
                        />
                    </div>
                    <span className={styles.storagePercent}>{storage.usage_percentage.toFixed(1)}%</span>
                </div>
            )}

            {/* Dashboard Content */}
            <div className={styles.dashboardContent}>
                {/* Toolbar */}
                <div className={styles.toolbar}>
                    <div className={styles.toolbarLeft}>
                        <h1 className={styles.pageTitle}>My Projects</h1>
                        <span className={styles.projectCount}>
                            {pagination.total} {pagination.total === 1 ? 'project' : 'projects'}
                        </span>
                    </div>
                    <div className={styles.toolbarRight}>
                        <form onSubmit={handleSearch} className={styles.searchForm}>
                            <input
                                type="text"
                                placeholder="Search projects..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className={styles.searchInput}
                            />
                            <button type="submit" className={styles.searchBtn}>🔍</button>
                        </form>
                        <select
                            value={sortBy}
                            onChange={(e) => handleSortChange(e.target.value)}
                            className={styles.sortSelect}
                        >
                            <option value="created_at_desc">Newest First</option>
                            <option value="created_at_asc">Oldest First</option>
                            <option value="title_asc">Name A-Z</option>
                            <option value="title_desc">Name Z-A</option>
                            <option value="size_desc">Largest First</option>
                            <option value="size_asc">Smallest First</option>
                        </select>
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className={styles.errorBanner}>
                        <span>⚠️ {error}</span>
                        <button onClick={() => setError('')}>×</button>
                    </div>
                )}

                {/* Loading State */}
                {isLoading ? (
                    <div className={styles.loadingGrid}>
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className={styles.skeletonCard}></div>
                        ))}
                    </div>
                ) : projects.length === 0 ? (
                    /* Empty State */
                    <div className={styles.emptyState}>
                        <div className={styles.emptyIcon}>📁</div>
                        <h2>No Projects Yet</h2>
                        <p>Create your first AI-powered website in minutes</p>
                        <button className={styles.createBtn} onClick={handleNewProject}>
                            <span>+</span> Create Your First Project
                        </button>
                    </div>
                ) : (
                    /* Projects Grid */
                    <div className={styles.projectsGrid}>
                        {projects.map((project) => (
                            <div key={project.session_id} className={styles.projectCard}>
                                {/* Thumbnail */}
                                <div className={styles.projectThumbnail}>
                                    {project.thumbnail_url ? (
                                        <img src={project.thumbnail_url} alt={project.project_title} />
                                    ) : (
                                        <div className={styles.thumbnailPlaceholder}>
                                            <span>🌐</span>
                                        </div>
                                    )}
                                    <div className={`${styles.statusBadge} ${getStatusColor(project.status)}`}>
                                        {getStatusLabel(project.status)}
                                    </div>
                                </div>

                                {/* Card Content */}
                                <div className={styles.projectInfo}>
                                    {renamingProject === project.session_id ? (
                                        <div className={styles.renameInput}>
                                            <input
                                                type="text"
                                                value={renameValue}
                                                onChange={(e) => setRenameValue(e.target.value)}
                                                onKeyPress={(e) => {
                                                    if (e.key === 'Enter') handleRenameSave(project.session_id);
                                                    if (e.key === 'Escape') handleRenameCancel();
                                                }}
                                                autoFocus
                                                className={styles.renameField}
                                            />
                                            <div className={styles.renameActions}>
                                                <button onClick={() => handleRenameSave(project.session_id)} className={styles.saveRenameBtn}>✓</button>
                                                <button onClick={handleRenameCancel} className={styles.cancelRenameBtn}>✕</button>
                                            </div>
                                        </div>
                                    ) : (
                                        <h3 className={styles.projectTitle} onClick={() => handleRenameStart(project.session_id, project.project_title)}>
                                            {project.project_title}
                                            <span className={styles.editIcon}>✏️</span>
                                        </h3>
                                    )}
                                    {project.domain && (
                                        <span className={styles.projectDomain}>{project.domain}</span>
                                    )}
                                    <div className={styles.projectMeta}>
                                        <span className={styles.metaItem}>
                                            📄 {project.file_count} files
                                        </span>
                                        <span className={styles.metaItem}>
                                            💾 {project.total_size_mb}MB
                                        </span>
                                    </div>
                                    <span className={styles.projectDate}>
                                        {formatDate(project.created_at)}
                                    </span>
                                </div>

                                {/* Card Actions */}
                                <div className={styles.projectActions}>
                                    <button
                                        className={styles.openBtn}
                                        onClick={() => handleOpenProject(project.session_id)}
                                    >
                                        <span>Open</span>
                                        <span className={styles.btnIcon}>→</span>
                                    </button>
                                    <button
                                        className={styles.deleteBtn}
                                        onClick={() => setDeleteConfirm(project.session_id)}
                                        title="Delete project"
                                    >
                                        🗑️
                                    </button>
                                </div>

                                {/* Delete Confirmation */}
                                {deleteConfirm === project.session_id && (
                                    <div className={styles.deleteConfirmOverlay}>
                                        <div className={styles.deleteConfirmContent}>
                                            <p>Delete "{project.project_title}"?</p>
                                            <p className={styles.deleteWarning}>
                                                This will free up {project.total_size_mb}MB of storage.
                                            </p>
                                            <div className={styles.deleteConfirmActions}>
                                                <button
                                                    className={styles.cancelBtn}
                                                    onClick={() => setDeleteConfirm(null)}
                                                >
                                                    Cancel
                                                </button>
                                                <button
                                                    className={styles.confirmDeleteBtn}
                                                    onClick={() => handleDeleteProject(project.session_id)}
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Pagination */}
                {pagination.pages > 1 && (
                    <div className={styles.pagination}>
                        <button
                            className={styles.pageBtn}
                            disabled={pagination.page === 1}
                            onClick={() => loadDashboard(pagination.page - 1)}
                        >
                            ← Previous
                        </button>
                        <span className={styles.pageInfo}>
                            Page {pagination.page} of {pagination.pages}
                        </span>
                        <button
                            className={styles.pageBtn}
                            disabled={pagination.page === pagination.pages}
                            onClick={() => loadDashboard(pagination.page + 1)}
                        >
                            Next →
                        </button>
                    </div>
                )}
            </div>
        </main>
    );
}
