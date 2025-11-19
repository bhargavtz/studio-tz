'use client';

import { useState, useEffect, useCallback, useTransition, useRef, useMemo } from 'react';
import { Header } from '@/components/layout/header';
import { ChatPanel } from '@/components/chat/chat-panel';
import { PreviewPanel } from '@/components/preview/preview-panel';
import { EditorPanel } from '@/components/editor/editor-panel';
import { type Message } from '@/components/chat/chat-message';
import { useToast } from '@/hooks/use-toast';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CodeEditor } from '@/components/editor/code-editor';
import { CodeBlock } from '@/components/ui/code-block';
import { initializeDefaultProject } from '@/lib/project-initializer';
import { AIFileSync } from '@/lib/ai-file-sync';
import { initialHtml, initialCss, initialJs, initialMessages } from '@/lib/initial-content';
import { formatHtml, extractBodyContent } from '@/lib/utils';
import { mutateHtmlByPath } from '@/lib/html-editor';
import { Button } from '@/components/ui/button';
import { RotateCw, Undo2, Redo2 } from 'lucide-react';

export type SelectedElement = {
  path: number[];
  tagName: string;
  textContent: string;
  classNames: string;
};

export type ElementStyleProperty =
  | 'width'
  | 'height'
  | 'padding'
  | 'margin'
  | 'backgroundColor'
  | 'color'
  | 'borderRadius'
  | 'opacity'
  | 'fontSize'
  | 'fontWeight'
  | 'lineHeight'
  | 'letterSpacing';

type PresetStyle = 'gradient' | 'shadow' | 'border' | 'glass' | 'pill' | 'hover';

export type ElementMutation =
  | { type: 'text'; value: string }
  | { type: 'classes'; value: string }
  | { type: 'style'; property: ElementStyleProperty; value: string }
  | { type: 'align'; value: 'left' | 'center' | 'right' }
  | { type: 'preset'; value: PresetStyle };

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

  // Initialize AI file sync
  const fileSync = useMemo(() => new AIFileSync(), []);

  const [history, setHistory] = useState<string[]>([initialHtml]);
  const [historyIndex, setHistoryIndex] = useState(0);

  const canUndo = historyIndex > 0;
  const canRedo = historyIndex < history.length - 1;

  const pushHistory = useCallback((nextHtml: string) => {
    setHistory((prev: string[]) => {
      const truncated = prev.slice(0, historyIndex + 1);
      return [...truncated, nextHtml];
    });
    setHistoryIndex((prev) => prev + 1);
  }, [historyIndex]);

  const handleUndo = useCallback(() => {
    if (!canUndo) return;
    setHistoryIndex((prev) => prev - 1);
    setHtmlContent(history[historyIndex - 1]);
  }, [canUndo, history, historyIndex]);

  const handleRedo = useCallback(() => {
    if (!canRedo) return;
    setHistoryIndex((prev) => prev + 1);
    setHtmlContent(history[historyIndex + 1]);
  }, [canRedo, history, historyIndex]);

  const handleRefreshPreview = useCallback(() => {
    setHtmlContent((prev: string) => `${prev}`);
  }, []);

  const handleChatSubmit = (prompt: string) => {
    const userMessage: Message = {
      role: 'user',
      content: prompt,
    };
    const newMessages: Message[] = [...messages, userMessage];
    setMessages(newMessages);
    setSelectedElement(null);

    startTransition(async () => {
      try {
        // Check if this is a multi-file project request
        const isMultiFileRequest = prompt.toLowerCase().includes('multi') || 
                                   prompt.toLowerCase().includes('project') || 
                                   prompt.toLowerCase().includes('website') ||
                                   prompt.toLowerCase().includes('create multiple') ||
                                   prompt.toLowerCase().includes('folder');

        // Call streaming API route
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt }),
        });

        if (!response.ok) {
          throw new Error(`API request failed: ${response.statusText}`);
        }

        if (!response.body) {
          throw new Error('No response body');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        // Add initial streaming message
        let streamingMessage: Message = {
          role: 'assistant',
          content: '',
        };
        setMessages(prev => [...prev, streamingMessage]);

        let aiResponse: any = null;
        let isMultiFile = false;
        const streamedFiles: Array<{ name: string; content: string; type: string }> = []
        let streamingCodeContent = '';

        while (true) {
          const { done, value } = await reader.read();

          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));

                switch (data.type) {
                  case 'status':
                    // Update streaming message with status
                    streamingMessage = {
                      ...streamingMessage,
                      content: data.message,
                    };
                    setMessages(prev => {
                      const updated = [...prev];
                      updated[updated.length - 1] = streamingMessage;
                      return updated;
                    });
                    break;

                  case 'code_chunk':
                    // Accumulate streaming code chunks
                    streamingCodeContent += data.chunk;

                    // Update streaming message to show live code generation
                    streamingMessage = {
                      ...streamingMessage,
                      content: `Generating code...\n\`\`\`\`\n${streamingCodeContent}\n\`\`\``,
                      code: streamingCodeContent,
                    };
                    setMessages(prev => {
                      const updated = [...prev];
                      updated[updated.length - 1] = streamingMessage;
                      return updated;
                    });
                    break;

                  case 'file':
                    // Add file to streamed files and update editor
                    streamedFiles.push(data.file);

                    // Update code editor immediately with new file
                    fileSync.syncSingleFile(data.file.name, data.file.content, data.file.type);

                    // Update streaming message to show file creation
                    streamingMessage = {
                      ...streamingMessage,
                      content: `${streamingMessage.content}\n📁 Created ${data.file.name}`,
                    };
                    setMessages(prev => {
                      const updated = [...prev];
                      updated[updated.length - 1] = streamingMessage;
                      return updated;
                    });
                    break;

                  case 'complete':
                    aiResponse = data.response;
                    isMultiFile = data.isMultiFile;

                    // Final success message
                    const finalMessage = isMultiFile
                      ? `✅ Multi-file project structure has been created and synchronized with the code editor. Check the Code tab to see all files and folders.`
                      : `✅ Code has been generated and updated in the editor.`;

                    setMessages(prev => {
                      const updated = [...prev];
                      updated[updated.length - 1] = {
                        role: 'assistant',
                        content: finalMessage,
                      };
                      return updated;
                    });
                    break;

                  case 'error':
                    throw new Error(data.error || 'Unknown error occurred');
                }
              } catch (parseError) {
                console.error('Error parsing stream data:', parseError);
              }
            }
          }
        }

        // Update legacy state for compatibility
        let legacyResponse: { html?: unknown; css?: string; js?: string } = {};

        if (!isMultiFile && aiResponse) {
          // Check if response has pages format (legacy single-file)
          if ('pages' in aiResponse) {
            type LegacyResponseType = {
              html?: unknown;
              css?: string;
              js?: string;
              pages?: Array<{ body: string | unknown }>;
            };
            const legacyTypedResponse = aiResponse as LegacyResponseType;
            const normalizedPages = legacyTypedResponse.pages?.map((page) => ({
              ...page,
              body: extractBodyContent(typeof page.body === 'string' ? page.body : ''),
            }));
            const htmlFromPages = normalizedPages?.[0]?.body;
            
            const legacyHtmlField = legacyTypedResponse.html;
            const legacyHtml = typeof legacyHtmlField === 'string' ? extractBodyContent(legacyHtmlField) : '';
            const normalizedHtml = htmlFromPages ?? legacyHtml;

            if (normalizedHtml) {
              setHtmlContent(normalizedHtml);
              pushHistory(normalizedHtml);
              if (legacyTypedResponse.css) {
                setCssContent(legacyTypedResponse.css);
              }
              if (legacyTypedResponse.js) {
                setJsContent(legacyTypedResponse.js);
              }
              setActiveFile('html');
            }
            
            // Store the typed response for use in message generation
            legacyResponse = legacyTypedResponse;
          }
        } else {
          // Update legacy state from file sync for multi-file responses
          const legacyContents = fileSync.getLegacyContents();
          if (legacyContents.html) {
            setHtmlContent(legacyContents.html);
            pushHistory(legacyContents.html);
          }
          setCssContent(legacyContents.css);
          setJsContent(legacyContents.js);
        }

      } catch (error: any) {
        console.error('Chat submission error:', error);
        toast({
          title: 'Error',
          description: error.message || 'Failed to process your request. Please try again.',
          variant: 'destructive',
        });
        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: 'Sorry, I encountered an error. Please try again.',
          },
        ]);
      }
    });
  };
  
  const handleElementUpdate = useCallback((path: number[], mutation: ElementMutation) => {
    if (!path || !mutation) return;

    const applyStyle = (node: HTMLElement, property: ElementStyleProperty, value: string) => {
      if (!value) return;
      if (property === 'opacity') {
        const numeric = Number(value);
        if (!Number.isNaN(numeric)) {
          node.style.opacity = Math.max(0, Math.min(1, numeric / 100)).toString();
        }
        return;
      }

      // Type-safe style property assignment
      if (property in node.style) {
        // Use direct property access for standard CSS properties
        (node.style as any)[property] = value;
      } else {
        // Handle custom CSS properties
        node.style.setProperty(property, value);
      }
    };

    const applyPreset = (node: HTMLElement, preset: PresetStyle) => {
      switch (preset) {
        case 'gradient':
          node.style.backgroundImage = 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)';
          node.style.color = '#fff';
          node.style.border = 'none';
          node.style.borderRadius = node.style.borderRadius || '9999px';
          break;
        case 'shadow':
          node.style.boxShadow = '0 20px 45px rgba(15, 23, 42, 0.35)';
          break;
        case 'border':
          node.style.border = '1px solid rgba(148, 163, 184, 0.5)';
          node.style.borderRadius = node.style.borderRadius || '16px';
          break;
        case 'glass':
          node.style.backgroundColor = 'rgba(15, 23, 42, 0.6)';
          node.style.border = '1px solid rgba(255, 255, 255, 0.2)';
          node.style.backdropFilter = 'blur(16px)';
          node.style.borderRadius = '24px';
          break;
        case 'pill':
          node.style.borderRadius = '9999px';
          node.style.padding = node.style.padding || '0.75rem 1.5rem';
          break;
        case 'hover':
          node.style.transition = 'transform 200ms ease, box-shadow 200ms ease';
          node.style.transformOrigin = 'center';
          node.onmouseenter = () => {
            node.style.transform = 'scale(1.02)';
            node.style.boxShadow = '0 20px 45px rgba(15, 23, 42, 0.3)';
          };
          node.onmouseleave = () => {
            node.style.transform = 'scale(1)';
            node.style.boxShadow = 'none';
          };
          break;
        default:
          break;
      }
    };

    setHtmlContent((prev) => {
      const next = mutateHtmlByPath(prev, path, (node) => {
        switch (mutation.type) {
          case 'text':
            node.textContent = mutation.value;
            break;
          case 'classes':
            node.className = mutation.value;
            break;
          case 'style':
            applyStyle(node, mutation.property, mutation.value);
            break;
          case 'align':
            node.style.textAlign = mutation.value;
            break;
          case 'preset':
            applyPreset(node, mutation.value);
            break;
          default:
            break;
        }
      });
      pushHistory(next);

      // Sync the updated HTML with the code editor
      const fullHtml = `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charSet="UTF-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n  <title>Next Inai Page</title>\n  <link rel="stylesheet" href="styles.css" />\n</head>\n<body>\n${formatHtml(next)}\n  <script src="script.js"></script>\n</body>\n</html>`;
      fileSync.syncSingleFile('index.html', fullHtml, 'html');

      return next;
    });
  }, [pushHistory, fileSync]);

  const handleMessage = useCallback((event: MessageEvent) => {
    // Basic security: check the origin of the message
    // In a real app, you'd want to make this more secure, e.g., event.origin === 'your-iframe-origin'
    if (event.source !== iframeRef.current?.contentWindow) {
      return;
    }
    
    const { type, ...data } = event.data;
    if (type === 'nextinai-select') {
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

  // Initialize default project on mount
  useEffect(() => {
    initializeDefaultProject();
  }, []);

  const htmlFileForCode = `<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charSet="UTF-8" />\n  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n  <title>Next Inai Page</title>\n  <link rel="stylesheet" href="styles.css" />\n</head>\n<body>\n${formatHtml(htmlContent)}\n  <script src="script.js"></script>\n</body>\n</html>`;

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
                <div className="flex items-center justify-between p-2 border-b gap-2">
                    <TabsList>
                        <TabsTrigger value="preview">Preview</TabsTrigger>
                        <TabsTrigger value="code">Code</TabsTrigger>
                    </TabsList>
                    <div className="flex items-center gap-2">
                      <Button variant="ghost" size="icon" onClick={handleUndo} disabled={!canUndo} title="Undo">
                        <Undo2 className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={handleRedo} disabled={!canRedo} title="Redo">
                        <Redo2 className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" onClick={handleRefreshPreview} title="Refresh preview">
                        <RotateCw className="h-4 w-4" />
                      </Button>
                    </div>
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
                  <CodeEditor className="h-full" />
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
