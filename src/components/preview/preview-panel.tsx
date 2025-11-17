"use client";

import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from 'react';

type PreviewPanelProps = {
  htmlContent: string;
  cssContent: string;
  jsContent: string;
  isSelectMode: boolean;
  onToggleSelectMode: () => void;
};

// This script will be injected into the iframe to handle interactions.
const interactionScript = `
document.addEventListener('DOMContentLoaded', () => {
  const style = document.createElement('style');
  style.innerHTML = \`
      [data-webforge-hover] { outline: 2px dashed #3B82F6 !important; cursor: pointer !important; transition: outline 0.1s ease-in-out; }
      [data-webforge-selected] { outline: 2px solid #93C5FD !important; box-shadow: 0 0 15px rgba(59, 130, 246, 0.5) !important; }
  \`;
  document.head.appendChild(style);

  let lastHovered = null;
  let selectionEnabled = false;

  window.addEventListener('message', (event) => {
    const data = event.data || {};
    if (data.type === 'webforge-select-mode') {
      selectionEnabled = !!data.enabled;
      if (!selectionEnabled && lastHovered) {
        if (lastHovered.removeAttribute) {
          lastHovered.removeAttribute('data-webforge-hover');
          lastHovered.removeAttribute('data-webforge-selected');
        }
        lastHovered = null;
      }
    }
  });

  document.body.addEventListener('mouseover', (e) => {
    if (!selectionEnabled) return;
    if (e.target === document.body || !e.target.tagName) return;
    if (lastHovered) lastHovered.removeAttribute('data-webforge-hover');
    e.target.setAttribute('data-webforge-hover', 'true');
    lastHovered = e.target;
  });

  document.body.addEventListener('mouseout', (e) => {
    if(e.target.removeAttribute) e.target.removeAttribute('data-webforge-hover');
  });

  document.body.addEventListener('click', (e) => {
      if (!selectionEnabled) return;
      e.preventDefault();
      e.stopPropagation();

      document.querySelectorAll('[data-webforge-selected]').forEach(el => el.removeAttribute('data-webforge-selected'));
      const target = e.target;
      if (target === document.body || !e.target.tagName) return;
      
      target.setAttribute('data-webforge-selected', 'true');
      
      let path = [];
      let current = target;
      while (current && current.parentElement && current !== document.body) {
          const parent = current.parentElement;
          const index = Array.from(parent.children).indexOf(current);
          path.unshift(index);
          current = parent;
      }
      
      window.parent.postMessage({
          type: 'webforge-select',
          path,
          textContent: target.innerText,
          tagName: target.tagName,
          classNames: target.className.replace(/data-webforge-\\w+/g, '').trim(),
      }, '*');
  });
});
`;

export const PreviewPanel = forwardRef<HTMLIFrameElement, PreviewPanelProps>(({ htmlContent, cssContent, jsContent, isSelectMode, onToggleSelectMode }, ref) => {
  const localRef = useRef<HTMLIFrameElement>(null);
  useImperativeHandle(ref, () => localRef.current!);
  const [iframeHeight, setIframeHeight] = useState('100%');


  useEffect(() => {
    const iframe = localRef.current;
    if (!iframe) return;
    
    const fullHtml = `
      <!DOCTYPE html>
      <html lang="en" class="dark">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet" />
        <script>
          tailwind.config = {
            darkMode: 'class',
            theme: {
              extend: {
                fontFamily: {
                  sans: ['Inter', 'sans-serif'],
                  headline: ['Space Grotesk', 'sans-serif'],
                }
              }
            }
          }
        </script>
        <style>
            html { scroll-behavior: smooth; }
            body { 
                font-family: 'Inter', sans-serif;
            }
            ${cssContent}
        </style>
        <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
        <script>${interactionScript}</script>
      </head>
      <body>
        ${htmlContent}
        <script>${jsContent}</script>
      </body>
      </html>
    `;

    iframe.srcdoc = fullHtml;

    const updateHeight = () => {
      try {
        const doc = iframe.contentDocument;
        if (doc) {
          const bodyHeight = doc.body.scrollHeight;
          if (bodyHeight) {
            setIframeHeight(`${bodyHeight}px`);
          }
        }
      } catch (err) {
        console.warn('Failed to read iframe height', err);
      }
    };

    iframe.addEventListener('load', updateHeight);
    requestAnimationFrame(updateHeight);

    return () => {
      iframe.removeEventListener('load', updateHeight);
    };

  }, [htmlContent, cssContent, jsContent]);

  useEffect(() => {
    const iframe = localRef.current;
    if (!iframe || !iframe.contentWindow) return;

    iframe.contentWindow.postMessage(
      {
        type: 'webforge-select-mode',
        enabled: isSelectMode,
      },
      '*'
    );
  }, [isSelectMode]);

  return (
    <div className="relative h-full w-full bg-background shadow-inner">
      <div className="h-full w-full overflow-auto pr-2 pb-16">
        <iframe
          ref={localRef}
          title="Live Preview"
          className="w-full border-0"
          style={{ height: iframeHeight, minHeight: '100%' }}
          sandbox="allow-scripts allow-same-origin"
        />
      </div>
      <button
        type="button"
        onClick={onToggleSelectMode}
        className={`absolute bottom-4 right-4 flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold shadow-lg transition-colors ${
          isSelectMode
            ? 'bg-primary text-primary-foreground'
            : 'bg-gray-900/80 text-gray-100 border border-gray-700 hover:bg-gray-800/90'
        }`}
     >
        <span
          className={`inline-block h-2 w-2 rounded-full ${
            isSelectMode ? 'bg-emerald-400' : 'bg-gray-400'
          }`}
        />
        <span>{isSelectMode ? 'Selecting elements' : 'Select design'}</span>
      </button>
    </div>
  );
});

PreviewPanel.displayName = 'PreviewPanel';
