'use server';

/**
 * @fileOverview A flow to generate HTML code from a user prompt.
 *
 * - generateHtmlFromPrompt - A function that takes a prompt and returns HTML code.
 * - GenerateHtmlFromPromptInput - The input type for the generateHtmlFromPrompt function.
 * - GenerateHtmlFromPromptOutput - The return type for the generateHtmlFromPrompt function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const GenerateHtmlFromPromptInputSchema = z.object({
  prompt: z.string().describe('A prompt describing the desired HTML code.'),
});
export type GenerateHtmlFromPromptInput = z.infer<typeof GenerateHtmlFromPromptInputSchema>;

const GenerateHtmlFromPromptOutputSchema = z.object({
  html: z.string().describe('The generated HTML code.'),
  css: z.string().describe('The generated CSS code.'),
  js: z.string().describe('The generated JavaScript code.'),
});
export type GenerateHtmlFromPromptOutput = z.infer<typeof GenerateHtmlFromPromptOutputSchema>;

export async function generateHtmlFromPrompt(input: GenerateHtmlFromPromptInput): Promise<GenerateHtmlFromPromptOutput> {
  return generateHtmlFromPromptFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateHtmlFromPromptPrompt',
  input: {schema: GenerateHtmlFromPromptInputSchema},
  output: {schema: GenerateHtmlFromPromptOutputSchema},
  prompt: `You are WebForgeAI, an expert front-end engineer and product designer.
Think carefully about the kind of website the user is asking for, what pages or sections are needed, and how they should work together.
Do NOT include your thinking in the response; only return final code.

User request: {{{prompt}}}

Return code for three files that work together:
- html: The full BODY CONTENT for the main page (single-page layout with navigation between sections) using Tailwind CSS utility classes. Do NOT include <html>, <head>, or <body> tags in this field.
- css: Additional Tailwind-based or custom CSS that should live in styles.css.
- js: Plain JavaScript for interactivity (navigation, basic state, modals, etc.).

Additional requirements:
- Every section must be responsive down to 360px width. Use fluid spacing (max-w, mx-auto, px-4) and avoid fixed pixel widths unless necessary.
- Avoid giant empty hero sections. Do not set min-height larger than the viewport minus the header; keep hero content vertically centered with reasonable padding.
- Prefer stacking layouts on small screens and limit top/bottom padding to balanced values (e.g., py-16). No blank space taller than 25% of the viewport should appear before meaningful content.
- Do NOT include external scripts, trackers, analytics beacons, iframes, or remote resources. Everything must run client-side only with inline JS and Tailwind classes.
- Never embed API keys, secrets, credentials, or references to backend endpoints. The page must be self-contained static content.
- Do not attempt to generate server-side code, database calls, or security-bypassing snippets.

All code must be HTML, CSS (including Tailwind classes), or vanilla JavaScript only.
`,
});

const generateHtmlFromPromptFlow = ai.defineFlow(
  {
    name: 'generateHtmlFromPromptFlow',
    inputSchema: GenerateHtmlFromPromptInputSchema,
    outputSchema: GenerateHtmlFromPromptOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
