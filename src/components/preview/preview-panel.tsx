'use client';

import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';

type PreviewPanelProps = {
  htmlContent: string;
  cssContent: string;
  jsContent: string;
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
  document.body.addEventListener('mouseover', (e) => {
    if (e.target === document.body || !e.target.tagName) return;
    if (lastHovered) lastHovered.removeAttribute('data-webforge-hover');
    e.target.setAttribute('data-webforge-hover', 'true');
    lastHovered = e.target;
  });

  document.body.addEventListener('mouseout', (e) => {
    if(e.target.removeAttribute) e.target.removeAttribute('data-webforge-hover');
  });

  document.body.addEventListener('click', (e) => {
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

export const PreviewPanel = forwardRef<HTMLIFrameElement, PreviewPanelProps>(({ htmlContent, cssContent, jsContent }, ref) => {
  const localRef = useRef<HTMLIFrameElement>(null);
  useImperativeHandle(ref, () => localRef.current!);


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
        <script>${interactionScript}</script>
      </head>
      <body>
        ${htmlContent}
        <script>${jsContent}</script>
      </body>
      </html>
    `;

    iframe.srcdoc = fullHtml;

  }, [htmlContent, cssContent, jsContent]);

  return (
    <div className="relative h-full w-full bg-background shadow-inner">
      <iframe
        ref={localRef}
        title="Live Preview"
        className="h-full w-full border-0"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
});

PreviewPanel.displayName = 'PreviewPanel';
