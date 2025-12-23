'use client';

import React, { Component, ReactNode } from 'react';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
        // TODO: Send to error reporting service (e.g., Sentry)
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    minHeight: '100vh',
                    padding: '2rem',
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white'
                }}>
                    <div style={{
                        background: 'rgba(255, 255, 255, 0.1)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: '16px',
                        padding: '3rem',
                        maxWidth: '500px'
                    }}>
                        <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>😔</h1>
                        <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Oops! Something went wrong</h2>
                        <p style={{ marginBottom: '2rem', opacity: 0.9 }}>
                            We encountered an unexpected error. Don't worry, your data is safe.
                        </p>
                        {this.state.error && (
                            <details style={{ marginBottom: '2rem', textAlign: 'left' }}>
                                <summary style={{ cursor: 'pointer', marginBottom: '0.5rem' }}>Error details</summary>
                                <pre style={{
                                    background: 'rgba(0, 0, 0, 0.2)',
                                    padding: '1rem',
                                    borderRadius: '8px',
                                    overflow: 'auto',
                                    fontSize: '0.875rem'
                                }}>
                                    {process.env.NODE_ENV === 'development' 
                                        ? `${this.state.error.message}\n\n${this.state.error.stack}` 
                                        : this.state.error.message}
                                </pre>
                            </details>                        )}
                        <button
                            onClick={() => window.location.href = '/'}
                            style={{
                                background: 'white',
                                color: '#667eea',
                                border: 'none',
                                padding: '0.875rem 2rem',
                                borderRadius: '8px',
                                fontSize: '1rem',
                                fontWeight: 600,
                                cursor: 'pointer',
                                transition: 'transform 0.2s'
                            }}
                            onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                            onMouseOut={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                        >
                            Return to Home
                        </button>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
