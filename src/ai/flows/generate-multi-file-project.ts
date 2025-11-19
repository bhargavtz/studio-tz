import { z } from 'genkit';
import { ai } from '@/ai/genkit';

const ProjectFileSchema = z.object({
  path: z.string().describe('File path including folders (e.g., pages/index.html, components/Header.vue, styles/main.css)'),
  content: z.string().describe('Complete file content'),
  type: z.enum(['html', 'css', 'javascript', 'vue', 'json', 'md', 'other']).describe('File type for syntax highlighting'),
  description: z.string().optional().describe('Brief description of what this file does'),
});

const ProjectStructureSchema = z.object({
  files: z.array(ProjectFileSchema).min(1).describe('All files in the project'),
  mainEntry: z.string().describe('Main entry point file path'),
  description: z.string().describe('Project description and setup instructions'),
});

export type ProjectStructureInput = {
  prompt: string;
  currentFiles?: Array<{ path: string; content: string; type: string }>;
};

export type ProjectStructureOutput = z.infer<typeof ProjectStructureSchema>;

export async function generateMultiFileProject(input: ProjectStructureInput): Promise<ProjectStructureOutput> {
  const prompt = ai.definePrompt({
    name: 'generateMultiFileProject',
    input: {
      schema: z.object({
        prompt: z.string(),
        currentFiles: z.array(z.object({
          path: z.string(),
          content: z.string(),
          type: z.string(),
        })).optional(),
      }),
    },
    output: { schema: ProjectStructureSchema },
    prompt: `You are Next Inai - an expert full-stack developer specializing in creating complete, production-ready web projects with multiple files and proper folder structure.

Your task: Create a complete multi-file website/project based on the user's request. Generate all necessary files with proper folder organization.

User Request: {{{prompt}}}

{{#currentFiles}}
Current Project Files:
{{#each currentFiles}}
- {{path}} ({{type}})
{{/each}}
{{/currentFiles}}

──────────────────────────────────
REQUIREMENTS
──────────────────────────────────

1. **Project Structure**
   - Create a logical folder structure (pages/, components/, styles/, scripts/, assets/, etc.)
   - Include all necessary files for a complete, functional project
   - Use modern best practices for file organization

2. **File Types Support**
   - HTML files (.html, .htm)
   - CSS files (.css)
   - JavaScript files (.js, .mjs)
   - Vue 3 components (.vue)
   - Configuration files (.json)
   - Documentation files (.md)
   - Any other necessary file types

3. **Technology Stack**
   - **Frontend**: HTML5, CSS3, JavaScript (ES6+)
   - **Framework**: Vue 3 (when appropriate for complex UI)
   - **Styling**: Tailwind CSS CDN or custom CSS
   - **Build Tools**: No complex build tools needed - keep it simple
   - **No Backend**: Static files only

4. **Content Requirements**
   - Each file must be complete and functional
   - Include proper DOCTYPE, meta tags, and structure for HTML files
   - CSS should be well-organized and commented
   - JavaScript should be modular and error-free
   - Vue components should be properly structured

5. **Multi-page Support**
   - For multi-page websites, create separate HTML files
   - Include navigation between pages
   - Shared CSS/JS files should be properly linked

6. **Modern Features**
   - Responsive design
   - Smooth animations and transitions
   - Interactive elements
   - Professional UI/UX
   - Accessibility considerations

7. **Output Format**
   Return a JSON object with:
   - files: Array of all project files with path, content, type, and description
   - mainEntry: Path to the main entry point (usually index.html)
   - description: Project overview and setup instructions

Example Response:
{
  "files": [
    {
      "path": "index.html",
      "content": "<!DOCTYPE html>...",
      "type": "html",
      "description": "Main landing page"
    },
    {
      "path": "styles/main.css",
      "content": "/* Main styles */...",
      "type": "css",
      "description": "Main stylesheet"
    }
  ],
  "mainEntry": "index.html",
  "description": "A modern responsive website with..."
}

Create a complete, professional project that showcases modern web development capabilities.`,
  });

  const flow = ai.defineFlow(
    {
      name: 'generateMultiFileProject',
      inputSchema: z.object({
        prompt: z.string(),
        currentFiles: z.array(z.object({
          path: z.string(),
          content: z.string(),
          type: z.string(),
        })).optional(),
      }),
      outputSchema: ProjectStructureSchema,
    },
    async (input: ProjectStructureInput) => {
      const { output } = await prompt(input);
      return output!;
    }
  );

  return flow(input);
}
