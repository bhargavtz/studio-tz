'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import dynamicImport from 'next/dynamic';
import styles from './page.module.css';
import * as api from '@/lib/api';
import { config } from '@/lib/config';

// Lazy load heavy components for better initial load performance
const ThemePanel = dynamicImport(() => import('@/components/features/ThemePanel'), {
    loading: () => <div className={styles.lazyLoading}>Loading themes...</div>,
    ssr: false
});

const AssetManager = dynamicImport(() => import('@/components/features/AssetManager'), {
    loading: () => <div className={styles.lazyLoading}>Loading assets...</div>,
    ssr: false
});

const PageManager = dynamicImport(() => import('@/components/features/PageManager'), {
    loading: () => <div className={styles.lazyLoading}>Loading pages...</div>,
    ssr: false
});

const MonacoCodeViewer = dynamicImport(() => import('@/components/features/MonacoCodeViewer'), {
    loading: () => <div className={styles.lazyLoading}>Loading code editor...</div>,
    ssr: false
});

// Force dynamic rendering (no static generation during build)
export const dynamic = 'force-dynamic';

type BuilderStep = 'questions' | 'blueprint' | 'preview';

export default function BuilderPage() {
    const params = useParams();
    const sessionId = params.sessionId as string;

    const [step, setStep] = useState<BuilderStep>('questions');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Session data
    const [session, setSession] = useState<api.Session | null>(null);
    const [questions, setQuestions] = useState<api.Question[]>([]);
    const [answers, setAnswers] = useState<Record<string, unknown>>({});
    const [blueprint, setBlueprint] = useState<api.Blueprint | null>(null);
    const [previewUrl, setPreviewUrl] = useState('');
    const [generating, setGenerating] = useState(false);

    const [chatMessage, setChatMessage] = useState('');
    const [chatHistory, setChatHistory] = useState<Array<{ role: 'user' | 'ai'; content: string }>>([]);
    const [isTyping, setIsTyping] = useState(false);
    const [activeTab, setActiveTab] = useState<'chat' | 'theme' | 'pages' | 'assets' | 'code'>('chat');
    const [deviceMode, setDeviceMode] = useState<'desktop' | 'mobile'>('desktop');
    const [viewMode, setViewMode] = useState<'preview' | 'code'>('preview');

    // Load session and questions
    useEffect(() => {
        async function loadSession() {
            try {
                const sessionData = await api.getSessionStatus(sessionId);
                setSession(sessionData);

                // Determine current step based on session status
                if (sessionData.files_generated.length > 0) {
                    setStep('preview');
                    const preview = await api.getPreviewUrl(sessionId);
                    setPreviewUrl(`${config.apiUrl}${preview.preview_url}`);
                } else if (sessionData.blueprint_confirmed) {
                    setStep('preview');
                } else if (sessionData.status === 'blueprint_generated') {
                    setStep('blueprint');
                    try {
                        const blueprintData = await api.getBlueprint(sessionId);
                        setBlueprint(blueprintData.blueprint);
                    } catch (err) {
                        console.warn('Blueprint not ready yet:', err);
                    }
                } else if (sessionData.status === 'answers_collected') {
                    setStep('questions');
                    try {
                        const questionsData = await api.getQuestions(sessionId);
                        setQuestions(questionsData.questions);
                    } catch (err) {
                        console.warn('Questions not ready:', err);
                    }
                } else if (sessionData.status === 'questions_generated') {
                    const qs = await api.getQuestions(sessionId);
                    setQuestions(qs.questions);
                    setStep('questions');
                } else if (sessionData.status === 'intent_processed') {
                    setStep('questions');
                } else if (sessionData.status === 'domain_identified') {
                    setStep('questions');
                    try {
                        const questionsData = await api.getQuestions(sessionId);
                        setQuestions(questionsData.questions);
                    } catch (err) {
                        console.warn('Questions not ready:', err);
                    }
                }
            } catch (err) {
                console.error('Failed to load session:', err);
                setError('Failed to load session. Please try refreshing the page.');
            } finally {
                setLoading(false);
            }
        }

        loadSession();
    }, [sessionId]);

    const handleAnswerChange = (questionId: string, value: unknown) => {
        setAnswers(prev => ({ ...prev, [questionId]: value }));
    };

    const handleSubmitAnswers = async () => {
        try {
            setLoading(true);
            await api.submitAnswers(sessionId, answers);
            const blueprintData = await api.getBlueprint(sessionId);
            setBlueprint(blueprintData.blueprint);
            setStep('blueprint');
        } catch (err) {
            console.error('Failed to submit answers:', err);
            setError('Failed to submit answers. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleConfirmBlueprint = async () => {
        try {
            setGenerating(true);
            // First confirm the blueprint
            await api.confirmBlueprint(sessionId);
            // Then generate the website
            const result = await api.generateWebsite(sessionId);
            setPreviewUrl(`${config.apiUrl}${result.preview_url}`);
            setStep('preview');
        } catch (err) {
            console.error('Failed to generate website:', err);
            setError('Failed to generate website. Please try again.');
        } finally {
            setGenerating(false);
        }
    };

    const handleDownload = async () => {
        try {
            const blob = await api.downloadProject(sessionId);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `website-${sessionId}.zip`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error('Failed to download:', err);
        }
    };

    const handleSendMessage = async () => {
        if (!chatMessage.trim() || isTyping) return;

        const userMessage = chatMessage;
        setChatMessage('');
        setChatHistory(prev => [...prev, { role: 'user', content: userMessage }]);
        setIsTyping(true);

        // Auto-scroll to bottom
        setTimeout(() => {
            const chatContainer = document.querySelector(`.${styles.chatMessages}`);
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 100);

        try {
            const result = await api.chatEdit(sessionId, userMessage);
            setIsTyping(false);
            setChatHistory(prev => [...prev, { role: 'ai', content: result.message }]);

            if (result.success && result.preview_url) {
                // Force iframe reload with timestamp
                const timestamp = new Date().getTime();
                setPreviewUrl(`${config.apiUrl}${result.preview_url}?t=${timestamp}`);
            }

            // Auto-scroll after AI response
            setTimeout(() => {
                const chatContainer = document.querySelector(`.${styles.chatMessages}`);
                if (chatContainer) {
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }, 100);
        } catch (err) {
            console.error('Chat edit failed:', err);
            setIsTyping(false);
            setChatHistory(prev => [...prev, {
                role: 'ai',
                content: 'Sorry, I couldn\'t process that request. Please try again.'
            }]);
        }
    };

    const handlePagesUpdate = () => {
        // Reload preview when pages are updated
        if (previewUrl) {
            const timestamp = new Date().getTime();
            setPreviewUrl(`${previewUrl.split('?')[0]}?t=${timestamp}`);
        }
    };

    if (loading) {
        return (
            <div className={styles.loadingScreen}>
                <div className={styles.spinner}></div>
                <p>Loading your session...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.errorScreen}>
                <h2>Oops!</h2>
                <p>{error}</p>
                <a href="/" className="btn btn-primary">Start Over</a>
            </div>
        );
    }

    return (
        <div className={styles.builder}>
            {/* Header */}
            <header className={styles.header}>
                <a href="/" className={styles.logo}>
                    <span className={styles.logoIcon}>✦</span>
                    NCD INAI
                </a>
                <div className={styles.steps}>
                    <div className={`${styles.stepIndicator} ${step === 'questions' ? styles.active : ''} ${['blueprint', 'preview'].includes(step) ? styles.completed : ''}`}>
                        <span>1</span> Questions
                    </div>
                    <div className={styles.stepDivider}></div>
                    <div className={`${styles.stepIndicator} ${step === 'blueprint' ? styles.active : ''} ${step === 'preview' ? styles.completed : ''}`}>
                        <span>2</span> Blueprint
                    </div>
                    <div className={styles.stepDivider}></div>
                    <div className={`${styles.stepIndicator} ${step === 'preview' ? styles.active : ''}`}>
                        <span>3</span> Preview
                    </div>
                </div>
                <div className={styles.headerActions}>
                    {step === 'preview' && (
                        <button onClick={handleDownload} className={styles.downloadBtn}>
                            ⬇ Download
                        </button>
                    )}
                </div>
            </header>

            <main className={styles.main}>
                {/* Questions Step */}
                {step === 'questions' && (
                    <div className={styles.questionsContainer}>
                        <div className={styles.questionsHeader}>
                            <h1>Tell us about your business</h1>
                            <p>Answer these questions so we can create the perfect website for you.</p>
                            {session?.domain && (
                                <div className={styles.domainBadge}>
                                    {session.domain.domain.replace('_', ' ')} • {session.domain.industry}
                                </div>
                            )}
                        </div>

                        <div className={styles.questionsList}>
                            {questions.map((q, index) => (
                                <div key={q.id} className={styles.questionCard} style={{ animationDelay: `${index * 0.1}s` }}>
                                    <label className={styles.questionLabel}>
                                        {q.question}
                                        {q.required && <span className={styles.optional}> (optional)</span>}
                                    </label>

                                    {q.type === 'text' && (
                                        <input
                                            type="text"
                                            className={styles.input}
                                            value={(answers[q.id] as string) || ''}
                                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                                            placeholder={q.placeholder}
                                        />
                                    )}

                                    {q.type === 'textarea' && (
                                        <textarea
                                            className={styles.textarea}
                                            value={(answers[q.id] as string) || ''}
                                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                                            placeholder={q.placeholder}
                                        />
                                    )}

                                    {q.type === 'select' && (
                                        <select
                                            className={styles.select}
                                            value={(answers[q.id] as string) || ''}
                                            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                                        >
                                            <option value="">Select an option...</option>
                                            {q.options?.map(opt => (
                                                <option key={opt} value={opt}>{opt}</option>
                                            ))}
                                        </select>
                                    )}

                                    {q.type === 'multiselect' && (
                                        <div className={styles.multiselect}>
                                            {q.options?.map(opt => (
                                                <label key={opt} className={styles.checkbox}>
                                                    <input
                                                        type="checkbox"
                                                        checked={((answers[q.id] as string[]) || []).includes(opt)}
                                                        onChange={(e) => {
                                                            const current = (answers[q.id] as string[]) || [];
                                                            const updated = e.target.checked
                                                                ? [...current, opt]
                                                                : current.filter(v => v !== opt);
                                                            handleAnswerChange(q.id, updated);
                                                        }}
                                                    />
                                                    {opt}
                                                </label>
                                            ))}
                                        </div>
                                    )}

                                    {q.type === 'yesno' && (
                                        <div className={styles.yesno}>
                                            <button
                                                className={`${styles.yesnoBtn} ${answers[q.id] === true ? styles.selected : ''}`}
                                                onClick={() => handleAnswerChange(q.id, true)}
                                            >
                                                Yes
                                            </button>
                                            <button
                                                className={`${styles.yesnoBtn} ${answers[q.id] === false ? styles.selected : ''}`}
                                                onClick={() => handleAnswerChange(q.id, false)}
                                            >
                                                No
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>

                        <div className={styles.questionsFooter}>
                            <button
                                className={styles.submitBtn}
                                onClick={handleSubmitAnswers}
                                disabled={loading}
                            >
                                {loading ? (
                                    <>
                                        <span className={styles.spinnerSmall}></span>
                                        Processing...
                                    </>
                                ) : (
                                    'Continue to Blueprint →'
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Blueprint Step */}
                {step === 'blueprint' && blueprint && (
                    <div className={styles.blueprintContainer}>
                        <div className={styles.blueprintHeader}>
                            <h1>Your Website Blueprint</h1>
                            <p>Review the structure we've created for your website</p>
                        </div>

                        <div className={styles.blueprintContent}>
                            <div className={styles.pagesList}>
                                {blueprint.pages.map((page) => (
                                    <div key={page.id} className={styles.pageCard}>
                                        <div className={styles.pageHeader}>
                                            <h3>{page.title}</h3>
                                            <span className={styles.pageSlug}>{page.slug}</span>
                                        </div>
                                        <div className={styles.sectionsList}>
                                            {page.sections.map((section) => (
                                                <div key={section.id} className={styles.sectionItem}>
                                                    <span className={styles.sectionType}>{section.type}</span>
                                                    {section.title && <span className={styles.sectionTitle}>{section.title}</span>}
                                                    <span className={styles.componentCount}>
                                                        {section.components.length} components
                                                    </span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className={styles.themePreview}>
                                <h3>Theme</h3>
                                <div className={styles.colorSwatches}>
                                    <div className={styles.swatch} style={{ background: blueprint.theme.primaryColor }}>
                                        <span>Primary</span>
                                    </div>
                                    <div className={styles.swatch} style={{ background: blueprint.theme.secondaryColor }}>
                                        <span>Secondary</span>
                                    </div>
                                    <div className={styles.swatch} style={{ background: blueprint.theme.accentColor }}>
                                        <span>Accent</span>
                                    </div>
                                </div>
                                <p className={styles.fontInfo}>Font: {blueprint.theme.fontFamily}</p>
                                <p className={styles.styleInfo}>Style: {blueprint.theme.style}</p>
                            </div>
                        </div>

                        <div className={styles.blueprintFooter}>
                            <button
                                className={styles.submitBtn}
                                onClick={handleConfirmBlueprint}
                                disabled={generating}
                            >
                                {generating ? (
                                    <>
                                        <span className={styles.spinnerSmall}></span>
                                        Building your website...
                                    </>
                                ) : (
                                    'Confirm & Generate Website →'
                                )}
                            </button>
                        </div>
                    </div>
                )}

                {/* Preview Step */}
                {step === 'preview' && (
                    <div className={`${styles.previewContainer} ${viewMode === 'code' ? styles.codeMode : ''}`}>
                        <div className={styles.previewPanel}>
                            <div className={styles.previewHeader}>
                                <div className={styles.deviceButtons}>
                                    <button
                                        className={`${styles.deviceBtn} ${deviceMode === 'desktop' && viewMode === 'preview' ? styles.active : ''}`}
                                        onClick={() => { setDeviceMode('desktop'); setViewMode('preview'); }}
                                    >
                                        💻 Desktop
                                    </button>
                                    <button
                                        className={`${styles.deviceBtn} ${deviceMode === 'mobile' && viewMode === 'preview' ? styles.active : ''}`}
                                        onClick={() => { setDeviceMode('mobile'); setViewMode('preview'); }}
                                    >
                                        📱 Mobile
                                    </button>
                                    <div className={styles.divider}></div>
                                    <button
                                        className={`${styles.deviceBtn} ${viewMode === 'preview' ? styles.active : ''}`}
                                        onClick={() => setViewMode('preview')}
                                    >
                                        👁️ Preview
                                    </button>
                                    <button
                                        className={`${styles.deviceBtn} ${viewMode === 'code' ? styles.active : ''}`}
                                        onClick={() => setViewMode('code')}
                                    >
                                        💻 Code
                                    </button>
                                </div>
                                {viewMode === 'preview' && (
                                    <div className={styles.previewUrl}>
                                        {previewUrl}
                                    </div>
                                )}
                            </div>

                            {viewMode === 'preview' ? (
                                <div className={`${styles.previewWrapper} ${deviceMode === 'mobile' ? styles.mobileMode : ''}`}>
                                    {previewUrl ? (
                                        <iframe
                                            src={previewUrl}
                                            className={styles.previewFrame}
                                            title="Website Preview"
                                        />
                                    ) : (
                                        <div className={styles.previewPlaceholder}>
                                            <div className={styles.spinner}></div>
                                            <p>Generating your website preview...</p>
                                        </div>
                                    )}
                                </div>
                            ) : (
                                <div className={styles.codeEditorWrapper}>
                                    <MonacoCodeViewer sessionId={sessionId} />
                                </div>
                            )}
                        </div>

                        {viewMode === 'preview' && (
                            <div className={styles.chatPanel}>
                                <div className={styles.tabs}>
                                    <button
                                        className={`${styles.tabBtn} ${activeTab === 'chat' ? styles.active : ''}`}
                                        onClick={() => setActiveTab('chat')}
                                    >
                                        💬 AI CHAT
                                    </button>
                                    <button
                                        className={`${styles.tabBtn} ${activeTab === 'theme' ? styles.active : ''}`}
                                        onClick={() => setActiveTab('theme')}
                                    >
                                        🎨 THEME
                                    </button>
                                    <button
                                        className={`${styles.tabBtn} ${activeTab === 'pages' ? styles.active : ''}`}
                                        onClick={() => setActiveTab('pages')}
                                    >
                                        📄 PAGES
                                    </button>
                                    <button
                                        className={`${styles.tabBtn} ${activeTab === 'assets' ? styles.active : ''}`}
                                        onClick={() => setActiveTab('assets')}
                                    >
                                        🖼️ ASSETS
                                    </button>
                                    <button
                                        className={`${styles.tabBtn} ${activeTab === 'code' ? styles.active : ''}`}
                                        onClick={() => setActiveTab('code')}
                                    >
                                        💻 CODE
                                    </button>
                                </div>

                                <div className={styles.featurePanel}>
                                    {activeTab === 'chat' && (
                                        <div className={styles.chatMessages}>
                                            {chatHistory.length === 0 ? (
                                                <div className={styles.chatWelcome}>
                                                    <div className={styles.chatWelcomeIcon}>💬✨</div>
                                                    <h3>AI Website Editor</h3>
                                                    <p className={styles.chatWelcomeDesc}>Chat naturally to make changes to your website. Only what you request will be modified - your entire site won't regenerate!</p>

                                                    <div className={styles.chatExamplesLabel}>Try these examples:</div>
                                                    <button onClick={() => setChatMessage("Change the heading to Welcome to My Business")} className={styles.exampleBtn}>
                                                        <span className={styles.exampleIcon}>✏️</span>
                                                        <span>Change main heading text</span>
                                                    </button>
                                                    <button onClick={() => setChatMessage("Add a contact form with email and message fields")} className={styles.exampleBtn}>
                                                        <span className={styles.exampleIcon}>➕</span>
                                                        <span>Add contact form section</span>
                                                    </button>
                                                    <button onClick={() => setChatMessage("Make the primary color blue")} className={styles.exampleBtn}>
                                                        <span className={styles.exampleIcon}>🎨</span>
                                                        <span>Change colors</span>
                                                    </button>
                                                    <button onClick={() => setChatMessage("Add a 3-column feature section")} className={styles.exampleBtn}>
                                                        <span className={styles.exampleIcon}>📦</span>
                                                        <span>Add features section</span>
                                                    </button>
                                                    <button onClick={() => setChatMessage("Make the font size bigger")} className={styles.exampleBtn}>
                                                        <span className={styles.exampleIcon}>🔤</span>
                                                        <span>Adjust typography</span>
                                                    </button>
                                                </div>
                                            ) : (
                                                <>
                                                    {chatHistory.map((msg, i) => (
                                                        <div key={i} className={`${styles.chatMessage} ${styles[msg.role]} ${styles.slideIn}`}>
                                                            {msg.content}
                                                        </div>
                                                    ))}
                                                    {isTyping && (
                                                        <div className={`${styles.chatMessage} ${styles.ai} ${styles.slideIn}`}>
                                                            <div className={styles.typingIndicator}>
                                                                <span></span>
                                                                <span></span>
                                                                <span></span>
                                                            </div>
                                                        </div>
                                                    )}
                                                </>
                                            )}
                                        </div>
                                    )}

                                    {activeTab === 'theme' && (
                                        <ThemePanel
                                            sessionId={sessionId}
                                            onThemeUpdate={() => {
                                                // Reload preview when theme changes
                                                if (previewUrl) {
                                                    const timestamp = new Date().getTime();
                                                    setPreviewUrl(`${previewUrl.split('?')[0]}?t=${timestamp}`);
                                                }
                                            }}
                                        />
                                    )}

                                    {activeTab === 'pages' && (
                                        <PageManager sessionId={sessionId} onPagesUpdate={handlePagesUpdate} />
                                    )}

                                    {activeTab === 'assets' && (
                                        <AssetManager sessionId={sessionId} />
                                    )}

                                    {activeTab === 'code' && (
                                        <MonacoCodeViewer sessionId={sessionId} />
                                    )}
                                </div>

                                {activeTab === 'chat' && (
                                    <div className={styles.chatInput}>
                                        <input
                                            type="text"
                                            placeholder="Say what to change... add section, change color, edit text, anything!"
                                            value={chatMessage}
                                            onChange={(e) => setChatMessage(e.target.value)}
                                            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                                        />
                                        <button onClick={handleSendMessage}>Send</button>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
