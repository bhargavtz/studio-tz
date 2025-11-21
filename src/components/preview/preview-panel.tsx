"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef, useState, useCallback } from 'react';

type PreviewPanelProps = {
  htmlContent: string;
  cssContent: string;
  jsContent: string;
  isSelectMode: boolean;
  onToggleSelectMode: () => void;
};

// Type augmentation for cleanup function
declare global {
  interface Window {
    _nextInaiCleanup?: (() => void) | undefined;
  }
}

// Interaction script injected inside the iframe. Scoped with an IIFE and safer DOM checks.
const interactionScript = String.raw`(() => {
  const style = document.createElement('style');
  // Sanitize CSS content to prevent XSS
  const cssContent = "[data-nextinai-hover] { outline: 2px dashed #3B82F6 !important; cursor: pointer !important; transition: outline 0.1s ease-in-out; animation: nextinai-shake 0.5s ease-in-out; }\\n[data-nextinai-selected] { outline: 2px solid #93C5FD !important; box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important; }\\n@keyframes nextinai-shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-2px); } 75% { transform: translateX(2px); } }";
  style.textContent = cssContent;
  document.head.appendChild(style);

  let lastHovered: Element | null = null;
  let selectionEnabled = false;

  const sendMessage = (payload) => {
    try { 
      // Security: Only send messages to parent window with specific origin validation
      if (window.parent && window.parent !== window) {
        window.parent.postMessage(payload, window.location.origin);
      }
    } catch (e) { 
      console.warn('Failed to send message to parent:', e);
    }
  };

  // Only observe element nodes
  function isValidTarget(t, body) {
    return t && t.nodeType === 1 && t !== body && t.tagName;
  }

  const setupBodyListeners = () => {
    const body = document.body;
    if (!body) return;

    window.addEventListener('message', (event) => {
      const data = event.data || {};
      if (data && data.type === 'nextinai-select-mode') {
        console.log('[NextInai] Received select-mode message:', data.enabled);
        selectionEnabled = !!data.enabled;
        console.log('[NextInai] Selection mode is now:', selectionEnabled);
        if (!selectionEnabled && lastHovered) {
          if (lastHovered.removeAttribute) {
            lastHovered.removeAttribute('data-nextinai-hover');
            lastHovered.removeAttribute('data-nextinai-selected');
          }
          lastHovered = null;
        }
      }
    }, false);

    body.addEventListener('mouseover', (e) => {
      if (!selectionEnabled) return;
      const target = e.target;
      if (!isValidTarget(target, body)) return;
      if (lastHovered && lastHovered.removeAttribute) lastHovered.removeAttribute('data-nextinai-hover');
      target.setAttribute('data-nextinai-hover', 'true');
      lastHovered = target;
    });

    body.addEventListener('mouseout', (e) => {
      const t = e.target;
      if (t && t.removeAttribute) t.removeAttribute('data-nextinai-hover');
    });

    body.addEventListener('click', (e) => {
      console.log('[NextInai] Click detected, selectionEnabled:', selectionEnabled);
      
      if (!selectionEnabled) {
        // Handle navigation when not in selection mode
        const target = e.target;
        const link = target.closest ? target.closest('a') : null;
        
        if (link) {
          const href = link.getAttribute('href');
          
          // Skip empty links or anchor jumps
          if (!href || href.startsWith('#') || href.startsWith('mailto:')) return;
          
          // Check if it's an internal link
          try {
            const url = new URL(link.href);
            if (url.origin === window.location.origin) {
              e.preventDefault();
              e.stopPropagation();
              
              // Send the path relative to the root
              sendMessage({
                type: 'nextinai-navigate',
                path: url.pathname + url.search + url.hash
              });
            }
          } catch (err) {
            // If URL parsing fails, fall back to attribute check
            if (href && !href.startsWith('http')) {
              e.preventDefault();
              sendMessage({
                type: 'nextinai-navigate',
                path: href
              });
            }
          }
        }
        return;
      }

      // Selection mode handling
      console.log('[NextInai] Selection mode active, processing click');
      e.preventDefault();
      e.stopPropagation();

      document.querySelectorAll('[data-nextinai-selected]').forEach(el => el.removeAttribute('data-nextinai-selected'));
      const target = e.target;
      if (!isValidTarget(target, body)) {
        console.log('[NextInai] Invalid target');
        return;
      }

      target.setAttribute('data-nextinai-selected', 'true');

      let path = [];
      let current = target;
      while (current && current.parentElement && current !== body) {
        const parent = current.parentElement;
        const elementChildren = Array.from(parent.children).filter(n => n.nodeType === 1);
        const index = elementChildren.indexOf(current);
        path.unshift(index);
        current = parent;
      }

      console.log('[NextInai] Sending select message with path:', path);
      sendMessage({
        type: 'nextinai-select',
        path,
        textContent: target.innerText,
        tagName: target.tagName,
        classNames: (target.className || '').replace(/data-nextinai-\\w+/g, '').trim(),
      });
    }, true);

    try {
      const ro = new ResizeObserver(() => {
        try { 
          const height = Math.max(document.documentElement.scrollHeight || 0, body.scrollHeight || 0);
          sendMessage({ type: 'nextinai-resize', height }); 
        } catch (e) {
          console.warn('Failed to send resize message:', e);
        }
      });
      ro.observe(document.documentElement);
      ro.observe(body);
      
      // Cleanup function for ResizeObserver
      const cleanupResizeObserver = () => {
        try {
          ro.disconnect();
        } catch (e) {
          console.warn('Failed to disconnect ResizeObserver:', e);
        }
      };
      
      // Store cleanup function for later use
      window._nextInaiCleanup = cleanupResizeObserver;
    } catch (err) {
      console.warn('ResizeObserver not available, falling back to MutationObserver:', err);
      const mo = new MutationObserver(() => {
        const height = Math.max(document.documentElement.scrollHeight || 0, body.scrollHeight || 0);
        sendMessage({ type: 'nextinai-resize', height });
      });
      mo.observe(body, { childList: true, subtree: true, characterData: true });
      
      // Cleanup function for MutationObserver
      const cleanupMutationObserver = () => {
        try {
          mo.disconnect();
        } catch (e) {
          console.warn('Failed to disconnect MutationObserver:', e);
        }
      };
      
      // Store cleanup function for later use
      window._nextInaiCleanup = cleanupMutationObserver;
    }
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupBodyListeners, { once: true });
  } else {
    setupBodyListeners();
  }
})();`;

// Debounce utility
function debounce<T extends (...args: any[]) => void>(fn: T, wait = 100) {
  let timeoutId: NodeJS.Timeout | null = null;
  return (...args: Parameters<T>) => {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), wait);
  };
}

export const PreviewPanel = forwardRef<HTMLIFrameElement, PreviewPanelProps>((props, ref) => {
  const { htmlContent, cssContent, jsContent, isSelectMode, onToggleSelectMode } = props;
  const iframeRef = useRef<HTMLIFrameElement | null>(null);
  const [iframeHeight, setIframeHeight] = useState<string>('100%');
  const latestIsSelectMode = useRef(isSelectMode);

  useImperativeHandle(ref, () => iframeRef.current as HTMLIFrameElement);

  // Build srcdoc - handle both complete HTML and body-only content
  const buildSrcDoc = useCallback((h: string, c: string, j: string) => {
    // Check if h is a complete HTML document
    const isCompleteHtml = h.trim().startsWith('<!DOCTYPE') || h.trim().startsWith('<html');

    if (isCompleteHtml) {
      // Use complete HTML, but inject CSS, JS, and interaction script
      let modifiedHtml = h;

      // 1. Inject CSS content if provided
      if (c && c.trim()) {
        const headCloseIndex = modifiedHtml.toLowerCase().indexOf('</head>');
        if (headCloseIndex !== -1) {
          modifiedHtml =
            modifiedHtml.substring(0, headCloseIndex) +
            `  <style>\n${c}\n  </style>\n` +
            modifiedHtml.substring(headCloseIndex);
        }
      }

      // 2. Inject interaction script before </head>
      const headCloseIndex2 = modifiedHtml.toLowerCase().indexOf('</head>');
      if (headCloseIndex2 !== -1) {
        modifiedHtml =
          modifiedHtml.substring(0, headCloseIndex2) +
          `  <script>${interactionScript}</script>\n` +
          modifiedHtml.substring(headCloseIndex2);
      }

      // 3. Inject JavaScript before </body>
      if (j && j.trim()) {
        const bodyCloseIndex = modifiedHtml.toLowerCase().lastIndexOf('</body>');
        if (bodyCloseIndex !== -1) {
          modifiedHtml =
            modifiedHtml.substring(0, bodyCloseIndex) +
            `  <script>\n    try {\n      ${j}\n    } catch(e) { console.error('Preview JS execution error:', e); }\n  </script>\n` +
            modifiedHtml.substring(bodyCloseIndex);
        }
      }

      return modifiedHtml;
    }

    // For body-only content, wrap with full HTML structure (backward compatibility)
    return `<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script>window.__NEXT_INAI_INJECTED__ = true;</script>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet" />
  <script>
    tailwind.config = { darkMode: 'class', theme: { extend: { fontFamily: { sans: ['Inter','sans-serif'], headline: ['Space Grotesk','sans-serif'] } } } };
  </script>
  <style>
    html { scroll-behavior: smooth; }
    body { font-family: 'Inter', sans-serif; margin:0; }
    ${c}
  </style>
  <script>${interactionScript}</script>
</head>
<body>
  ${h}
  <script>
    try {
      ${j}
    } catch(e) { 
      console.error('Preview JS execution error:', e);
      // Create safe error element instead of using innerHTML
      const errorDiv = document.createElement('div');
      errorDiv.style.cssText = 'position:fixed;top:10px;right:10px;background:red;color:white;padding:5px;border-radius:3px;font-size:12px;';
      errorDiv.textContent = 'JavaScript Error';
      document.body.appendChild(errorDiv);
    }
  </script>
</body>
</html>`;
  }, []);

  // Post height and selection messages handler coming from iframe
  useEffect(() => {
    const onMessage = (ev: MessageEvent) => {
      const data = ev.data || {};
      if (!data || typeof data !== 'object') return;

      if (data.type === 'nextinai-resize' && typeof data.height === 'number') {
        // clamp and set
        setIframeHeight(`${Math.min(2000, Math.max(300, data.height))}px`);
      }

      if (data.type === 'nextinai-select') {
        // Create custom event with proper data structure
        const event = new CustomEvent('nextinai-select', { detail: data });
        window.dispatchEvent(event);
      }
    };

    window.addEventListener('message', onMessage);
    return () => window.removeEventListener('message', onMessage);
  }, []);

  // Debounced srcdoc update to avoid thrashing on rapid edits
  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    const update = () => {
      try {
        const srcdoc = buildSrcDoc(htmlContent, cssContent, jsContent);
        // Only update if changed to reduce reloads
        if (iframe.srcdoc !== srcdoc) iframe.srcdoc = srcdoc;
      } catch (e) {
        console.warn('Failed to set iframe srcdoc', e);
      }
    };

    const debounced = debounce(update, 150);
    debounced();

    return () => {
      // nothing specific to cleanup
    };
  }, [htmlContent, cssContent, jsContent]);

  // Keep select mode synced, but wait until iframe is ready
  useEffect(() => {
    latestIsSelectMode.current = isSelectMode;
    const sendMode = () => {
      const win = iframeRef.current?.contentWindow;
      if (!win) return;
      try {
        // Security: Use specific origin instead of wildcard
        const targetOrigin = window.location.origin;
        win.postMessage({ type: 'nextinai-select-mode', enabled: isSelectMode }, targetOrigin);
      } catch (e) {
        console.warn('Failed to send select mode message:', e);
      }
    };

    // try immediate, then try again on load
    sendMode();
    const onLoad = () => sendMode();
    const iframe = iframeRef.current;
    iframe?.addEventListener('load', onLoad);
    return () => iframe?.removeEventListener('load', onLoad);
  }, [isSelectMode]);

  // Ensure cleanup: remove listeners when unmounting
  useEffect(() => {
    return () => {
      // nothing to cleanup at top-level here presently
    };
  }, []);

  return (
    <div className="relative h-full w-full bg-background shadow-inner">
      <div className="h-full w-full overflow-auto pr-2 pb-16">
        <iframe
          ref={iframeRef}
          title="Live Preview"
          className="w-full border-0 bg-white"
          style={{ height: iframeHeight, minHeight: '100%' }}
          // Narrow sandbox - only allow scripts inside the iframe
          sandbox="allow-scripts"
        />
      </div>

      <button
        type="button"
        onClick={onToggleSelectMode}
        className={`absolute bottom-4 right-4 flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold shadow-lg transition-colors ${isSelectMode
          ? 'bg-primary text-primary-foreground'
          : 'bg-gray-900/80 text-gray-100 border border-gray-700 hover:bg-gray-800/90'
          }`}
      >
        <span
          className={`inline-block h-2 w-2 rounded-full ${isSelectMode ? 'bg-emerald-400' : 'bg-gray-400'}`}
        />
        <span>{isSelectMode ? 'Selecting elements' : 'Select design'}</span>
      </button>
    </div>
  );
});

PreviewPanel.displayName = 'PreviewPanel';

export default PreviewPanel;
