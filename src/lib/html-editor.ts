"use client";

export type ElementMutator = (element: HTMLElement) => void;

export function mutateHtmlByPath(html: string, path: number[], mutator: ElementMutator): string {
  if (!Array.isArray(path) || path.length === 0) {
    return html;
  }

  if (typeof window === 'undefined') {
    console.warn('mutateHtmlByPath called on server');
    return html;
  }

  try {
    const ParserCtor = window.DOMParser ?? DOMParser;
    if (!ParserCtor) {
      throw new Error('DOMParser not available');
    }
    const parser = new ParserCtor();
    const doc = parser.parseFromString(`<body>${html}</body>`, 'text/html');
    let current: Element | null = doc.body;

    for (const index of path) {
      if (!current || !current.children[index]) {
        throw new Error(`Invalid path index: ${index}`);
      }
      current = current.children[index];
    }

    if (current) {
      mutator(current as HTMLElement);
      return doc.body.innerHTML;
    }

    // If we reach here, no valid element was found
    throw new Error('No valid element found at the specified path');
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    console.error('mutateHtmlByPath failed:', errorMessage, error);
    // Return original HTML to prevent corruption
    return html;
  }
}
