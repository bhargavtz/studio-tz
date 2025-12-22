import { useState, useEffect } from 'react';
import * as api from '@/lib/api';
import styles from './PageManager.module.css';

interface PageManagerProps {
    sessionId: string;
    onPagesUpdate: (pages: api.Page[]) => void;
}

export default function PageManager({ sessionId, onPagesUpdate }: PageManagerProps) {
    const [blueprint, setBlueprint] = useState<api.Blueprint | null>(null);
    const [loading, setLoading] = useState(false);
    const [newPageTitle, setNewPageTitle] = useState('');

    useEffect(() => {
        loadBlueprint();
    }, [sessionId]);

    async function loadBlueprint() {
        try {
            const result = await api.getBlueprint(sessionId);
            setBlueprint(result.blueprint);
        } catch (err) {
            console.error('Failed to load blueprint:', err);
        }
    }

    async function handleAddPage() {
        if (!blueprint || !newPageTitle.trim()) return;

        const slug = newPageTitle.toLowerCase().replace(/[^a-z0-9]+/g, '-');
        const newPage: api.Page = {
            id: slug,
            title: newPageTitle,
            slug: slug,
            sections: [], // Empty start
            meta: {}
        };

        const updatedBlueprint = {
            ...blueprint,
            pages: [...blueprint.pages, newPage]
        };

        await saveBlueprint(updatedBlueprint);
        setNewPageTitle('');
    }

    async function handleDeletePage(pageId: string) {
        if (!blueprint) return;
        if (!confirm('Are you sure you want to delete this page?')) return;

        const updatedBlueprint = {
            ...blueprint,
            pages: blueprint.pages.filter(p => p.id !== pageId)
        };

        await saveBlueprint(updatedBlueprint);
    }

    async function saveBlueprint(updatedBlueprint: api.Blueprint) {
        setLoading(true);
        try {
            await api.updateBlueprint(sessionId, updatedBlueprint);
            setBlueprint(updatedBlueprint);
            onPagesUpdate(updatedBlueprint.pages);
        } catch (err) {
            console.error('Failed to save blueprint:', err);
            alert('Failed to update pages');
        } finally {
            setLoading(false);
        }
    }

    if (!blueprint) return <div>Loading pages...</div>;

    return (
        <div className={styles.container}>
            <div className={styles.addPageSection}>
                <input
                    type="text"
                    value={newPageTitle}
                    onChange={(e) => setNewPageTitle(e.target.value)}
                    placeholder="New Page Title (e.g. Services)"
                    className={styles.input}
                    onKeyDown={(e) => e.key === 'Enter' && handleAddPage()}
                />
                <button
                    onClick={handleAddPage}
                    disabled={!newPageTitle.trim() || loading}
                    className={styles.addBtn}
                >
                    + Add
                </button>
            </div>

            <div className={styles.pageList}>
                {blueprint.pages.map((page) => (
                    <div key={page.id} className={styles.pageCard}>
                        <div className={styles.pageInfo}>
                            <span className={styles.pageTitle}>{page.title}</span>
                            <span className={styles.pageSlug}>/{page.slug}</span>
                        </div>
                        {page.slug !== 'home' && page.slug !== '/' && (
                            <button
                                onClick={() => handleDeletePage(page.id)}
                                className={styles.deleteBtn}
                                title="Delete Page"
                            >
                                ✕
                            </button>
                        )}
                    </div>
                ))}
            </div>

            <p className={styles.hint}>
                Note: Updating pages requires regenerating the website to take effect.
            </p>
        </div>
    );
}
