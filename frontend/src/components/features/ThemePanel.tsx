import { useState, useEffect } from 'react';
import * as api from '@/lib/api';
import styles from './ThemePanel.module.css';

interface ThemePanelProps {
    sessionId: string;
    onThemeUpdate: (previewUrl: string) => void;
}

export default function ThemePanel({ sessionId, onThemeUpdate }: ThemePanelProps) {
    const [theme, setTheme] = useState<api.Theme | null>(null);
    const [presets, setPresets] = useState<api.ThemePreset[]>([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadThemeData();
    }, [sessionId]);

    async function loadThemeData() {
        try {
            const [themeData, presetsData] = await Promise.all([
                api.getTheme(sessionId),
                api.getThemePresets(sessionId)
            ]);
            setTheme(themeData);
            setPresets(presetsData.presets);
        } catch (err) {
            console.error('Failed to load theme data:', err);
        }
    }

    async function handleColorChange(key: keyof api.Theme, value: string) {
        if (!theme) return;

        const previousTheme: api.Theme | null = theme ? { ...theme } : null;
        const newTheme = { ...theme, [key]: value };
        setTheme(newTheme);

        // Debounce update? For now direct update
        try {
            let updatePayload: Partial<api.Theme> | { colors: Partial<Pick<api.Theme, keyof api.Theme>> };
            if (key.endsWith('Color')) {
                updatePayload = { colors: { [key]: value } };
            } else {
                updatePayload = { [key]: value };
            }
            const result = await api.updateTheme(sessionId, updatePayload);
            onThemeUpdate(result.preview_url);
        } catch (err) {
            if (previousTheme) {
                setTheme(previousTheme);
            } else {
                setTheme(null);
            }
            console.error('Failed to update theme:', err);
        }
    }

    async function handlePresetClick(preset: api.ThemePreset) {
        const previousTheme = { ...theme };
        const flatTheme: api.Theme = { ...preset.colors, fontFamily: preset.fontFamily, style: preset.style };
        setTheme(flatTheme);
        try {
            const result = await api.updateTheme(sessionId, { colors: preset.colors, fontFamily: preset.fontFamily, style: preset.style });
            onThemeUpdate(result.preview_url);
        } catch (err) {
            setTheme({
                primaryColor: previousTheme.primaryColor ?? '',
                secondaryColor: previousTheme.secondaryColor ?? '',
                backgroundColor: previousTheme.backgroundColor ?? '',
                textColor: previousTheme.textColor ?? '',
                accentColor: previousTheme.accentColor ?? '',
                fontFamily: previousTheme.fontFamily ?? '',
                style: previousTheme.style ?? ''
            });
            console.error('Failed to apply preset:', err);
        }
    }

    if (!theme) return <div>Loading theme...</div>;

    return (
        <div className={styles.container}>
            <div className={styles.section}>
                <h3>Presets</h3>
                <div className={styles.presetGrid}>
                    {presets.map((preset, i) => (
                        <button
                            key={i}
                            className={styles.presetBtn}
                            onClick={() => handlePresetClick(preset)}
                            style={{
                                background: `linear-gradient(135deg, ${preset.colors.primaryColor} 0%, ${preset.colors.secondaryColor} 100%)`
                            }}
                        >
                            {preset.name}
                        </button>
                    ))}
                </div>
            </div>

            <div className={styles.section}>
                <h3>Colors</h3>
                <div className={styles.colorInput}>
                    <label>Primary</label>
                    <div className={styles.colorPickerWrapper}>
                        <input
                            type="color"
                            value={theme.primaryColor}
                            onChange={(e) => handleColorChange('primaryColor', e.target.value)}
                        />
                        <span>{theme.primaryColor}</span>
                    </div>
                </div>
                <div className={styles.colorInput}>
                    <label>Secondary</label>
                    <div className={styles.colorPickerWrapper}>
                        <input
                            type="color"
                            value={theme.secondaryColor}
                            onChange={(e) => handleColorChange('secondaryColor', e.target.value)}
                        />
                        <span>{theme.secondaryColor}</span>
                    </div>
                </div>
                <div className={styles.colorInput}>
                    <label>Accent</label>
                    <div className={styles.colorPickerWrapper}>
                        <input
                            type="color"
                            value={theme.accentColor}
                            onChange={(e) => handleColorChange('accentColor', e.target.value)}
                        />
                        <span>{theme.accentColor}</span>
                    </div>
                </div>
                <div className={styles.colorInput}>
                    <label>Background</label>
                    <div className={styles.colorPickerWrapper}>
                        <input
                            type="color"
                            value={theme.backgroundColor}
                            onChange={(e) => handleColorChange('backgroundColor', e.target.value)}
                        />
                        <span>{theme.backgroundColor}</span>
                    </div>
                </div>
                <div className={styles.colorInput}>
                    <label>Text</label>
                    <div className={styles.colorPickerWrapper}>
                        <input
                            type="color"
                            value={theme.textColor}
                            onChange={(e) => handleColorChange('textColor', e.target.value)}
                        />
                        <span>{theme.textColor}</span>
                    </div>
                </div>
            </div>

            <div className={styles.section}>
                <h3>Typography</h3>
                <select
                    value={theme.fontFamily}
                    onChange={(e) => handleColorChange('fontFamily', e.target.value)}
                    className={styles.select}
                >
                    <option value="Inter, sans-serif">Inter</option>
                    <option value="'Roboto', sans-serif">Roboto</option>
                    <option value="'Open Sans', sans-serif">Open Sans</option>
                    <option value="'Playfair Display', serif">Playfair Display</option>
                    <option value="'Courier New', monospace">Courier New</option>
                </select>
            </div>
        </div>
    );
}
