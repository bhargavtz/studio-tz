'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import styles from './page.module.css';
import * as api from '@/lib/api';
import { SignInButton, SignUpButton, SignedIn, SignedOut, UserButton, useUser } from '@clerk/nextjs';

export default function Home() {
  const [intent, setIntent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const router = useRouter();
  const { isSignedIn, isLoaded } = useUser();


  // No auto-redirect - users stay on landing page until they click dashboard

  // Mouse parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20,
      });
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!intent.trim()) {
      setError('Please describe your website idea');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      // Create session with the vision/intent directly
      const sessionData = await api.createSession(intent);
      const sessionId = sessionData.session_id;

      router.push(`/builder/${sessionId}`);
    } catch (err) {
      setError('Something went wrong. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className={styles.main}>
      {/* Animated Background */}
      <div className={styles.bgWrapper}>
        <div
          className={styles.bgOrb1}
          style={{
            transform: `translate(${mousePosition.x}px, ${mousePosition.y}px)`,
          }}
        />
        <div
          className={styles.bgOrb2}
          style={{
            transform: `translate(${-mousePosition.x}px, ${-mousePosition.y}px)`,
          }}
        />
        <div className={styles.bgGrid} />
        <div className={styles.bgNoise} />
      </div>

      {/* Floating Header */}
      <header className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.logo}>
            <div className={styles.logoGlow} />
            <span className={styles.logoIcon}>✦</span>
            <span className={styles.logoText}>NCD INAI</span>
          </div>
          <div className={styles.authSection}>
            <nav className={styles.nav}>
              <a href="#features" className={styles.navLink}>Features</a>
              <a href="#showcase" className={styles.navLink}>Showcase</a>
              <a href="#pricing" className={styles.navLink}>Pricing</a>
            </nav>
            <div className={styles.authButtons}>
              <SignedOut>
                <SignInButton mode="modal">
                  <button className={styles.signInButton}>
                    <span className={styles.userIcon}>👤</span>
                    <span>Sign In</span>
                  </button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button className={styles.signUpButton}>
                    <span>Sign Up</span>
                    <span className={styles.buttonArrow}>→</span>
                  </button>
                </SignUpButton>
              </SignedOut>
              <SignedIn>
                <a href="/dashboard" className={styles.dashboardButton}>
                  <span>📊</span>
                  <span>Dashboard</span>
                </a>
                <UserButton afterSignOutUrl="/" />
              </SignedIn>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          {/* Status Badge */}
          <div className={styles.statusBadge}>
            <span className={styles.statusDot} />
            <span>AI-Powered • No Code Required</span>
          </div>

          {/* Main Heading */}
          <h1 className={styles.heroTitle}>
            <span className={styles.heroTitleLine}>Create Stunning</span>
            <span className={`${styles.heroTitleLine} ${styles.gradient}`}>
              Websites with AI
            </span>
          </h1>

          {/* Subtitle */}
          <p className={styles.heroSubtitle}>
            Transform your ideas into professional websites in minutes.
            Our AI understands your vision and builds exactly what you need.
          </p>

          {/* CTA Input */}
          <form className={styles.ctaForm} onSubmit={handleSubmit} suppressHydrationWarning>
            <div className={styles.inputGroup}>
              <div className={styles.inputIcon}>✨</div>
              <input
                type="text"
                className={styles.ctaInput}
                placeholder="Describe your dream website..."
                value={intent}
                onChange={(e) => setIntent(e.target.value)}
                disabled={isLoading}
              />
              <button
                type="submit"
                className={styles.ctaButton}
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className={styles.spinner} />
                ) : (
                  <>
                    <span>Start Building</span>
                    <span className={styles.buttonArrow}>→</span>
                  </>
                )}
              </button>
            </div>
            {error && <p className={styles.errorText}>{error}</p>}
          </form>

          {/* Quick Examples */}
          <div className={styles.quickExamples}>
            <span className={styles.examplesLabel}>Popular:</span>
            {['E-commerce Store', 'Portfolio', 'Restaurant', 'SaaS Landing'].map((example) => (
              <button
                key={example}
                className={styles.exampleChip}
                onClick={() => setIntent(`A modern ${example.toLowerCase()} website`)}
              >
                {example}
              </button>
            ))}
          </div>

          {/* Stats */}
          <div className={styles.stats}>
            <div className={styles.statItem}>
              <div className={styles.statNumber}>10K+</div>
              <div className={styles.statLabel}>Websites Created</div>
            </div>
            <div className={styles.statDivider} />
            <div className={styles.statItem}>
              <div className={styles.statNumber}>99%</div>
              <div className={styles.statLabel}>Satisfaction Rate</div>
            </div>
            <div className={styles.statDivider} />
            <div className={styles.statItem}>
              <div className={styles.statNumber}>{'<'} 5min</div>
              <div className={styles.statLabel}>Average Build Time</div>
            </div>
          </div>
        </div>

        {/* 3D Mockup */}
        <div className={styles.heroVisual}>
          <div className={styles.floatingCard}>
            <div className={styles.cardGlow} />
            <div className={styles.browserMockup}>
              <div className={styles.browserBar}>
                <div className={styles.browserDots}>
                  <span /><span /><span />
                </div>
                <div className={styles.browserUrl}>yourwebsite.com</div>
                <div className={styles.browserActions} />
              </div>
              <div className={styles.browserContent}>
                <div className={styles.contentPlaceholder}>
                  <div className={styles.placeholderNav} />
                  <div className={styles.placeholderHero}>
                    <div className={styles.placeholderTitle} />
                    <div className={styles.placeholderText} />
                    <div className={styles.placeholderButton} />
                  </div>
                  <div className={styles.placeholderCards}>
                    <div className={styles.placeholderCard} />
                    <div className={styles.placeholderCard} />
                    <div className={styles.placeholderCard} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className={styles.features}>
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>
            <span className={styles.gradient}>Powerful Features</span>
          </h2>
          <p className={styles.sectionSubtitle}>
            Everything you need to build professional websites
          </p>
        </div>

        <div className={styles.featureGrid}>
          {[
            { icon: '🧠', title: 'Smart AI', desc: 'Understands your business and creates tailored designs' },
            { icon: '🎨', title: 'Custom Themes', desc: 'Choose from beautiful presets or create your own' },
            { icon: '📱', title: 'Responsive', desc: 'Perfect on desktop, tablet, and mobile devices' },
            { icon: '⚡', title: 'Lightning Fast', desc: 'Optimized code for blazing fast load times' },
            { icon: '🔒', title: 'Secure', desc: 'Built-in security best practices and HTTPS' },
            { icon: '📊', title: 'Analytics', desc: 'Track visitors and understand your audience' },
          ].map((feature, i) => (
            <div key={i} className={styles.featureCard}>
              <div className={styles.featureCardGlow} />
              <div className={styles.featureIcon}>{feature.icon}</div>
              <h3 className={styles.featureTitle}>{feature.title}</h3>
              <p className={styles.featureDesc}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        <div className={styles.footerContent}>
          <div className={styles.footerBrand}>
            <div className={styles.logo}>
              <span className={styles.logoIcon}>✦</span>
              <span className={styles.logoText}>NCD INAI</span>
            </div>
            <p className={styles.footerTagline}>
              Building the future of web design with AI
            </p>
          </div>
          <div className={styles.footerCopy}>
            © 2024 NCD INAI. Crafted with ❤️
          </div>
        </div>
      </footer>
    </main>
  );
}
