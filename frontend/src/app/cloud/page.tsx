'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useAuth } from '@clerk/nextjs';
import styles from './cloud.module.css';
import * as api from '@/lib/api';
import type { StorageSummary } from '@/lib/api';

export default function CloudPage() {
    const router = useRouter();
    const { user, isLoaded: userLoaded } = useUser();

    const [storage, setStorage] = useState<StorageSummary | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const loadData = async () => {
            if (!userLoaded) return;

            if (!user) {
                router.push('/');
                return;
            }

            try {
                setIsLoading(true);
                const token = user.id;
                const data = await api.getStorageSummary(token);
                setStorage(data);
            } catch (err) {
                console.error('Failed to load storage data:', err);
                setError('Failed to load storage information.');
            } finally {
                setIsLoading(false);
            }
        };

        loadData();
    }, [user, userLoaded, router]);

    if (!userLoaded || isLoading) {
        return (
            <div className={styles.loadingContainer}>
                <div className={styles.spinner}></div>
                <p>Loading Cloud Storage...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.loadingContainer}>
                <p>⚠️ {error}</p>
                <button onClick={() => router.back()} className={styles.backBtn} style={{ marginTop: '1rem' }}>
                    Go Back
                </button>
            </div>
        );
    }

    return (
        <main className={styles.main}>
            <header className={styles.header}>
                <div className={styles.headerContent}>
                    <button onClick={() => router.back()} className={styles.backBtn}>
                        ← Back to Dashboard
                    </button>
                    <div className={styles.title}>Cloud Storage Manager</div>
                    <div style={{ width: 100 }}></div> {/* Spacer for balance */}
                </div>
            </header>

            <div className={styles.content}>
                {storage && (
                    <div className={styles.storageCard}>
                        <div className={styles.cardHeader}>
                            <div className={styles.cardIcon}>☁️</div>
                            <div className={styles.cardTitle}>
                                <h2>Your Cloud Space</h2>
                                <p>Manage your assets and project files</p>
                            </div>
                        </div>

                        <div className={styles.statsGrid}>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Total Projects</span>
                                <span className={styles.statValue}>{storage.total_projects}</span>
                            </div>
                            <div className={styles.statItem}>
                                <span className={styles.statLabel}>Space Remaining</span>
                                <span className={styles.statValue}>{storage.storage_remaining_mb} MB</span>
                            </div>
                        </div>

                        <div className={styles.usageSection}>
                            <div className={styles.barContainer}>
                                <div
                                    className={`${styles.usageBar} ${storage.is_at_limit ? styles.barCritical :
                                        storage.is_near_limit ? styles.barWarning : ''
                                        }`}
                                    style={{ width: `${Math.min(storage.usage_percentage, 100)}%` }}
                                />
                            </div>
                            <div className={styles.usageText}>
                                <span>
                                    {storage.storage_used_mb} MB used
                                </span>
                                <span>
                                    {storage.storage_limit_mb} MB limit
                                </span>
                            </div>
                        </div>
                    </div>
                )}

                <div className={styles.assetList}>
                    <div className={styles.assetListHeader}>
                        <h3>Global Assets</h3>
                        {/* Future: Add asset upload here */}
                    </div>
                    <div className={styles.emptyState}>
                        <p>Global asset management coming soon.</p>
                        <p style={{ fontSize: '0.875rem', marginTop: '0.5rem' }}>
                            Currently, assets are managed within individual projects.
                        </p>
                    </div>
                </div>
            </div>
        </main>
    );
}
