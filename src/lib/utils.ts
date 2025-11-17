import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatHtml(html: string): string {
  const normalized = html.replace(/>\s*</g, ">\n<")
  const lines = normalized.split("\n")
  let indent = 0

  const formatted = lines
    .map((line) => {
      const trimmed = line.trim()
      if (!trimmed) return ""

      if (trimmed.startsWith("</")) {
        indent = Math.max(indent - 1, 0)
      }

      const current = `${"  ".repeat(indent)}${trimmed}`

      const isOpeningTag =
        /^<([a-zA-Z0-9-]+)([^>]*)>$/.test(trimmed) &&
        !trimmed.endsWith("/>") &&
        !/^<(input|img|br|hr|meta|link)/i.test(trimmed)

      if (isOpeningTag) {
        indent += 1
      }

      return current
    })
    .filter(Boolean)
    .join("\n")

  return formatted
}

export function extractBodyContent(html: string): string {
  const match = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i)
  if (match && match[1]) {
    return match[1].trim()
  }
  return html.trim()
}
