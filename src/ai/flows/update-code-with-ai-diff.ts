'use server';
/**
 * @fileOverview Updates code in HTML, CSS, or JS files based on AI instructions.
 *
 * - updateCodeWithAIDiff - A function that selectively updates code in files.
 * - UpdateCodeWithAIDiffInput - The input type for the updateCodeWithAIDiff function.
 * - UpdateCodeWithAIDiffOutput - The return type for the updateCodeWithAIDiff function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const UpdateCodeWithAIDiffInputSchema = z.object({
  fileType: z.enum(['html', 'css', 'js']).describe('The type of file to update (html, css, or js).'),
  fileContent: z.string().describe('The current content of the file.'),
  instructions: z.string().describe('The instructions for updating the code.'),
  elementDetails: z.string().optional().describe('Details of the element to modify (if applicable)'),
});

export type UpdateCodeWithAIDiffInput = z.infer<typeof UpdateCodeWithAIDiffInputSchema>;

const UpdateCodeWithAIDiffOutputSchema = z.object({
  updatedFileContent: z.string().describe('The updated content of the file.'),
});

export type UpdateCodeWithAIDiffOutput = z.infer<typeof UpdateCodeWithAIDiffOutputSchema>;

export async function updateCodeWithAIDiff(input: UpdateCodeWithAIDiffInput): Promise<UpdateCodeWithAIDiffOutput> {
  return updateCodeWithAIDiffFlow(input);
}

const updateCodeWithAIDiffPrompt = ai.definePrompt({
  name: 'updateCodeWithAIDiffPrompt',
  input: {schema: UpdateCodeWithAIDiffInputSchema},
  output: {schema: UpdateCodeWithAIDiffOutputSchema},
  prompt: `You are a code modification expert. You will receive the content of a file (HTML, CSS, or JS), 
instructions on how to modify it, and, optionally, details of the element that needs to be modified.
Your goal is to modify the file content based on the instructions, making sure to keep the code clean and functional.

File Type: {{{fileType}}}

Current File Content:
{{{fileContent}}}

Instructions: {{{instructions}}}

Element Details (if applicable): {{{elementDetails}}}

Ensure that the updated code is valid and well-formatted. Return only the updated file content.
`,
});

const updateCodeWithAIDiffFlow = ai.defineFlow(
  {
    name: 'updateCodeWithAIDiffFlow',
    inputSchema: UpdateCodeWithAIDiffInputSchema,
    outputSchema: UpdateCodeWithAIDiffOutputSchema,
  },
  async input => {
    const {output} = await updateCodeWithAIDiffPrompt(input);
    return output!;
  }
);
