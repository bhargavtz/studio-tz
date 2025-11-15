'use client';

import { useEffect, useRef } from 'react';

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
      [data-webforge-hover] { outline: 2px dashed #FF9800 !important; cursor: pointer !important; transition: outline 0.1s ease-in-out; }
      [data-webforge-selected] { outline: 2px solid #3F51B5 !important; box-shadow: 0 0 15px rgba(63, 81, 181, 0.5) !important; }
  \`;
  document.head.appendChild(style);

  let lastHovered = null;
  document.body.addEventListener('mouseover', (e) => {
    if (e.target === document.body) return;
    if (lastHovered) lastHovered.removeAttribute('data-webforge-hover');
    e.target.setAttribute('data-webforge-hover', 'true');
    lastHovered = e.target;
  });

  document.body.addEventListener('mouseout', (e) => {
    e.target.removeAttribute('data-webforge-hover');
  });

  document.body.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();

      document.querySelectorAll('[data-webforge-selected]').forEach(el => el.removeAttribute('data-webforge-selected'));
      const target = e.target;
      if (target === document.body) return;
      
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

export function PreviewPanel({ htmlContent, cssContent, jsContent }: PreviewPanelProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    if (!iframeRef.current) return;
    const iframe = iframeRef.current;
    
    const fullHtml = \`
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Space+Grotesk:wght@400;500;700&display=swap" rel="stylesheet" />
        <script>
          tailwind.config = {
            theme: {
              extend: {
                fontFamily: {
                  body: ['Inter', 'sans-serif'],
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
            \${cssContent}
        </style>
        <script>${jsContent}</script>
        <script>${interactionScript}</script>
      </head>
      <body>
        \${htmlContent}
      </body>
      </html>
    \`;

    iframe.srcdoc = fullHtml;

  }, [htmlContent, cssContent, jsContent]);

  return (
    <div className="relative h-full w-full bg-white shadow-inner">
      <iframe
        ref={iframeRef}
        title="Live Preview"
        className="h-full w-full border-0"
        sandbox="allow-scripts allow-same-origin"
      />
    </div>
  );
}
