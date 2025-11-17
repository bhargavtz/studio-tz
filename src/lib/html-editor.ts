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
      return html;
    }
    const parser = new ParserCtor();
    const doc = parser.parseFromString(`<body>${html}</body>`, 'text/html');
    let current: Element | null = doc.body;

    for (const index of path) {
      if (!current || !current.children[index]) {
        return html;
      }
      current = current.children[index];
    }

    if (current) {
      mutator(current as HTMLElement);
      return doc.body.innerHTML;
    }
  } catch (error) {
    console.error('mutateHtmlByPath failed', error);
  }

  return html;
}
