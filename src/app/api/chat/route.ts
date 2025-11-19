import { NextRequest } from 'next/server';
import { generateHtmlFromPrompt } from '@/ai/flows/generate-html-from-prompt';
import { generateMultiFileProject } from '@/ai/flows/generate-multi-file-project';
import { ai } from '@/ai/genkit';

export { POST };

async function POST(request: NextRequest) {
  const encoder = new TextEncoder();
  
  const stream = new ReadableStream({
    async start(controller) {
      try {
        const { prompt } = await request.json();

        if (!prompt || typeof prompt !== 'string') {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ error: 'Invalid prompt provided', type: 'error' })}\n\n`));
          controller.close();
          return;
        }

        // Detect if this is a multi-file request
        const isMultiFileRequest = prompt.toLowerCase().includes('multi') || 
                                   prompt.toLowerCase().includes('project') || 
                                   prompt.toLowerCase().includes('website') ||
                                   prompt.toLowerCase().includes('create multiple') ||
                                   prompt.toLowerCase().includes('folder');

        // Send initial status
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'status', message: 'Thinking...', stage: 'init' })}\n\n`));

        let response;
        let isMultiFile = false;

        if (isMultiFileRequest) {
          // Send progress for multi-file generation
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'status', message: 'Generating multi-file project structure...', stage: 'generating' })}\n\n`));
          
          response = await generateMultiFileProject({ prompt });
          isMultiFile = true;
          
          // Send file-by-file updates
          if (response.files && Array.isArray(response.files)) {
            for (const file of response.files) {
              controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
                type: 'file', 
                file: {
                  name: file.path,
                  content: file.content,
                  type: file.type
                }
              })}\n\n`));
            }
          }
        } else {
          // Send progress for single-file generation
          controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'status', message: 'Generating HTML, CSS, and JavaScript...', stage: 'generating' })}\n\n`));

          const fullPrompt = `You are a web design assistant. The user wants to modify their current website.

User request: "${prompt}"

Think carefully about the overall website structure (sections, navigation, interactions), but do not include your reasoning in the answer. Only return final code for html, css, and js.`;

          response = await generateHtmlFromPrompt({ prompt: fullPrompt });

          // Send individual parts as they're ready
          if (response.pages && response.pages.length > 0) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'file',
              file: {
                name: 'index.html',
                content: response.pages[0].body,
                type: 'html'
              }
            })}\n\n`));
          }

          if (response.css) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'file',
              file: {
                name: 'styles.css',
                content: response.css,
                type: 'css'
              }
            })}\n\n`));
          }

          if (response.js) {
            controller.enqueue(encoder.encode(`data: ${JSON.stringify({
              type: 'file',
              file: {
                name: 'script.js',
                content: response.js,
                type: 'javascript'
              }
            })}\n\n`));
          }
        }

        // Send completion message
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'complete', 
          response,
          isMultiFile,
          success: true 
        })}\n\n`));

      } catch (error: any) {
        console.error('Chat API error:', error);
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ 
          type: 'error',
          error: error.message || 'Failed to process request',
          success: false 
        })}\n\n`));
      } finally {
        controller.close();
      }
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}
