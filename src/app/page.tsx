'use client';

import { useState, useEffect, useCallback, useTransition, useRef } from 'react';
import { Header } from '@/components/layout/header';
import { ChatPanel } from '@/components/chat/chat-panel';
import { PreviewPanel } from '@/components/preview/preview-panel';
import { EditorPanel } from '@/components/editor/editor-panel';
import { type Message } from '@/components/chat/chat-message';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CodeBlock } from '@/components/ui/code-block';
import { generateHtmlFromPrompt } from '@/ai/flows/generate-html-from-prompt';
import { updateCodeWithAIDiff } from '@/ai/flows/update-code-with-ai-diff';
import { initialHtml, initialCss, initialJs, initialMessages } from '@/lib/initial-content';
import { formatHtml, extractBodyContent } from '@/lib/utils';

export type SelectedElement = {
  path: number[];
  tagName: string;
  textContent: string;
  classNames: string;
};

export default function Home() {
  const [isPending, startTransition] = useTransition();
  const { toast } = useToast();

  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [htmlContent, setHtmlContent] = useState(initialHtml);
  const [cssContent, setCssContent] = useState(initialCss);
  const [jsContent, setJsContent] = useState(initialJs);
  const [selectedElement, setSelectedElement] = useState<SelectedElement | null>(null);
  const [activeFile, setActiveFile] = useState<'html' | 'css' | 'js'>('html');
  const [isSelectMode, setIsSelectMode] = useState(false);

  const handleChatSubmit = (prompt: string) => {
    const newMessages: Message[] = [...messages, { role: 'user', content: prompt }];
    setMessages(newMessages);
    setSelectedElement(null);

    startTransition(async () => {
      try {
        const fullPrompt = `Current project state HTML (for index.html):
---
${htmlContent}
---

User request: "${prompt}"

Think carefully about the overall website structure (sections, navigation, interactions), but do not include your reasoning in the answer. Only return final code for html, css, and js.`;

        const response = await generateHtmlFromPrompt({ prompt: fullPrompt });
        
        if (response.html) {
          const normalizedHtml = extractBodyContent(response.html);
          setHtmlContent(normalizedHtml);
          if (typeof response.css === 'string') {
            setCssContent(response.css);
          }
          if (typeof response.js === 'string') {
            setJsContent(response.js);
          }
          setActiveFile('html');

          const assistantMessages: Message[] = [
            {
              role: 'assistant',
              content: 'Index.html has been updated with the new layout. Check the Code tab or preview to see it.',
            },
          ];

          if (response.css && response.css.trim()) {
            assistantMessages.push({
              role: 'assistant',
              content: 'styles.css was regenerated with Tailwind classes and any custom tweaks.',
            });
          }

          if (response.js && response.js.trim()) {
            assistantMessages.push({
              role: 'assistant',
              content: 'script.js now includes the latest interactivity logic.',
            });
          }

          setMessages([
            ...newMessages,
            ...assistantMessages,
          ]);
        } else {
            throw new Error('AI did not return HTML.');
        }

      } catch (error) {
        console.error('AI Error:', error);

        const isOverloaded =
          error instanceof Error &&
          typeof error.message === 'string' &&
          error.message.includes('503 Service Unavailable');

        toast({
          variant: 'destructive',
          title: isOverloaded ? 'AI model is busy' : 'An error occurred',
          description: isOverloaded
            ? 'The Gemini model is temporarily overloaded. Please wait a moment and try again.'
            : 'Failed to communicate with the AI. Please try again.',
        });

        setMessages([
          ...newMessages,
          {
            role: 'assistant',
            content: isOverloaded
              ? 'The AI model is currently overloaded (503). Please wait a bit and send your request again.'
              : 'Sorry, I encountered an error. Please try again.',
          },
        ]);
      }
    });
  };
  
  const handleElementUpdate = (path: number[], instruction: string) => {
    if (!path) return;

    startTransition(async () => {
      try {
        const response = await updateCodeWithAIDiff({
          fileType: 'html',
          fileContent: htmlContent,
          instructions: instruction,
          elementDetails: `The element to modify can be found using this JS path from document.body: ${path.reduce((acc, index) => `${acc}.children[${index}]`, 'document.body')}`
        });
        
        if (response.updatedFileContent) {
          setHtmlContent(response.updatedFileContent);
          toast({
            title: 'Element Updated',
            description: 'The HTML has been updated successfully.',
          });
          setSelectedElement(null);
        } else {
            throw new Error('AI did not return updated HTML.');
        }

      } catch (error) {
        console.error('AI Update Error:', error);
        toast({
          variant: 'destructive',
          title: 'Update Failed',
          description: 'Failed to update the element. Please try again.',
        });
      }
    });
  };

  const handleMessage = useCallback((event: MessageEvent) => {
    // Basic security: check the origin of the message
    // In a real app, you'd want to make this more secure, e.g., event.origin === 'your-iframe-origin'
    if (event.source !== iframeRef.current?.contentWindow) {
      return;
    }
    
    const { type, ...data } = event.data;
    if (type === 'webforge-select') {
      setSelectedElement(data as SelectedElement);
    }
  }, []);

  const iframeRef = useRef<HTMLIFrameElement>(null);

  useEffect(() => {
    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [handleMessage]);

  const htmlFileForCode = `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charSet="UTF-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n  <title>WebForgeAI Page</title>\n  <link rel="stylesheet" href="styles.css" />\n</head>\n<body>\n${formatHtml(htmlContent)}\n  <script src="script.js"></script>\n</body>\n</html>`;

  const codeForActiveFile =
    activeFile === 'css'
      ? cssContent
      : activeFile === 'js'
        ? jsContent
        : htmlFileForCode;
  const languageForActiveFile =
    activeFile === 'css' ? 'css' : activeFile === 'js' ? 'javascript' : 'html';

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-background text-foreground">
      <Header htmlContent={htmlContent} cssContent={cssContent} jsContent={jsContent} />
      <main className="grid flex-1 min-h-0 pt-16 grid-cols-1 md:grid-cols-3 xl:grid-cols-4">
        <div className="col-span-1 border-r flex flex-col min-w-[300px] md:min-w-[350px] h-full min-h-0">
          <ChatPanel
            messages={messages}
            isLoading={isPending}
            onSubmit={handleChatSubmit}
          />
        </div>
        <div className="relative col-span-1 md:col-span-2 xl:col-span-3 h-full flex flex-col min-h-0">
            <Tabs defaultValue="preview" className="flex flex-col flex-1 min-h-0 w-full">
                <div className="p-2 border-b">
                    <TabsList>
                        <TabsTrigger value="preview">Preview</TabsTrigger>
                        <TabsTrigger value="code">Code</TabsTrigger>
                    </TabsList>
                </div>
                <TabsContent value="preview" className="flex-1 min-h-0 overflow-auto">
                    <PreviewPanel
                        ref={iframeRef}
                        htmlContent={htmlContent}
                        cssContent={cssContent}
                        jsContent={jsContent}
                        isSelectMode={isSelectMode}
                        onToggleSelectMode={() => setIsSelectMode(prev => !prev)}
                    />
                </TabsContent>
                <TabsContent value="code" className="flex-1 min-h-0 overflow-hidden bg-gray-950">
                  <div className="flex h-full min-h-0">
                    <div className="w-48 border-r border-gray-800 bg-gray-950/80">
                      <div className="px-3 py-2 text-xs font-medium uppercase tracking-wide text-gray-400">
                        Files
                      </div>
                      <button
                        type="button"
                        onClick={() => setActiveFile('html')}
                        className={
                          activeFile === 'html'
                            ? 'flex w-full items-center px-3 py-1.5 text-sm text-left bg-gray-900 text-white'
                            : 'flex w-full items-center px-3 py-1.5 text-sm text-left text-gray-300 hover:bg-gray-900/40'
                        }
                      >
                        index.html
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveFile('css')}
                        className={
                          activeFile === 'css'
                            ? 'flex w-full items-center px-3 py-1.5 text-sm text-left bg-gray-900 text-white'
                            : 'flex w-full items-center px-3 py-1.5 text-sm text-left text-gray-300 hover:bg-gray-900/40'
                        }
                      >
                        styles.css
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveFile('js')}
                        className={
                          activeFile === 'js'
                            ? 'flex w-full items-center px-3 py-1.5 text-sm text-left bg-gray-900 text-white'
                            : 'flex w-full items-center px-3 py-1.5 text-sm text-left text-gray-300 hover:bg-gray-900/40'
                        }
                      >
                        script.js
                      </button>
                    </div>
                    <div className="flex-1 min-h-0 overflow-auto">
                      <CodeBlock code={codeForActiveFile} language={languageForActiveFile} />
                    </div>
                  </div>
                </TabsContent>
            </Tabs>

            {selectedElement && (
                <EditorPanel
                  element={selectedElement}
                  onClose={() => setSelectedElement(null)}
                  onUpdate={handleElementUpdate}
                />
            )}
        </div>
      </main>
    </div>
  );
}
