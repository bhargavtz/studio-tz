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
});
export type GenerateHtmlFromPromptOutput = z.infer<typeof GenerateHtmlFromPromptOutputSchema>;

export async function generateHtmlFromPrompt(input: GenerateHtmlFromPromptInput): Promise<GenerateHtmlFromPromptOutput> {
  return generateHtmlFromPromptFlow(input);
}

const prompt = ai.definePrompt({
  name: 'generateHtmlFromPromptPrompt',
  input: {schema: GenerateHtmlFromPromptInputSchema},
  output: {schema: GenerateHtmlFromPromptOutputSchema},
  prompt: `You are an expert HTML code generator. Generate HTML code based on the following prompt:\n\nPrompt: {{{prompt}}}\n\nMake sure to include tailwind classes for styling and format the output to be readable.
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
