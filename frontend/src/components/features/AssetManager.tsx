import { useState, useEffect, useRef } from 'react';
import * as api from '@/lib/api';
import { config } from '@/lib/config';
import styles from './AssetManager.module.css';

interface AssetManagerProps {
    sessionId: string;
}

export default function AssetManager({ sessionId }: AssetManagerProps) {
    const [assets, setAssets] = useState<api.Asset[]>([]);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        loadAssets();
    }, [sessionId]);

    async function loadAssets() {
        try {
            const result = await api.getAssets(sessionId);
            setAssets(result.assets);
        } catch (err) {
            console.error('Failed to load assets:', err);
        }
    }

    async function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
        if (!e.target.files || e.target.files.length === 0) return;

        const file = e.target.files[0];
        setUploading(true);
        try {
            await api.uploadAsset(sessionId, file);
            await loadAssets();
        } catch (err) {
            console.error('Failed to upload asset:', err);
            alert('Failed to upload asset');
        } finally {
            setUploading(false);
            if (fileInputRef.current) fileInputRef.current.value = '';
        }
    }

    async function handleDelete(filename: string) {
        if (!confirm('Are you sure you want to delete this asset?')) return;

        try {
            await api.deleteAsset(sessionId, filename);
            setAssets(assets.filter(a => a.filename !== filename));
        } catch (err) {
            console.error('Failed to delete asset:', err);
        }
    }

    function copyToClipboard(url: string) {
        const fullUrl = `${config.apiUrl}${url}`;
        navigator.clipboard.writeText(fullUrl);
        alert('URL copied to clipboard!');
    }

    return (
        <div className={styles.container}>
            <div className={styles.uploadSection}>
                <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileSelect}
                    className={styles.hiddenInput}
                    accept="image/*"
                />
                <button
                    className={styles.uploadBtn}
                    onClick={() => fileInputRef.current?.click()}
                    disabled={uploading}
                >
                    {uploading ? 'Uploading...' : '☁️ Upload Image'}
                </button>
            </div>

            <div className={styles.assetsGrid}>
                {assets.map((asset) => (
                    <div key={asset.filename} className={styles.assetCard}>
                        <div className={styles.preview}>
                            <img src={`${config.apiUrl}${asset.url}`} alt={asset.filename} />
                        </div>
                        <div className={styles.assetInfo}>
                            <span className={styles.filename} title={asset.filename}>
                                {asset.filename}
                            </span>
                            <div className={styles.actions}>
                                <button
                                    onClick={() => copyToClipboard(asset.url)}
                                    className={styles.actionBtn}
                                    title="Copy URL"
                                >
                                    🔗
                                </button>
                                <button
                                    onClick={() => handleDelete(asset.filename)}
                                    className={`${styles.actionBtn} ${styles.deleteBtn}`}
                                    title="Delete"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>
                ))}

                {assets.length === 0 && (
                    <div className={styles.emptyState}>
                        <p>No assets uploaded yet</p>
                    </div>
                )}
            </div>
        </div>
    );
}
