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

  const handleChatSubmit = (prompt: string) => {
    const newMessages: Message[] = [...messages, { role: 'user', content: prompt }];
    setMessages(newMessages);
    setSelectedElement(null);

    startTransition(async () => {
      try {
        const fullPrompt = `You are a web developer creating a single HTML page using Tailwind CSS. The user wants to update their website based on their request.
Current HTML content:
---
${htmlContent}
---
User request: "${prompt}"

Your task is to generate the new, complete, and valid HTML code for the body of the page. Do NOT wrap the code in a markdown block. The output must be a single block of HTML code that replaces the previous content entirely.`;

        const response = await generateHtmlFromPrompt({ prompt: fullPrompt });
        
        if (response.html) {
          setHtmlContent(response.html);
          setMessages([
            ...newMessages,
            { role: 'assistant', content: 'I\'ve updated the website based on your request. You can see the changes in the preview.' },
          ]);
        } else {
            throw new Error('AI did not return HTML.');
        }

      } catch (error) {
        console.error('AI Error:', error);
        toast({
          variant: 'destructive',
          title: 'An error occurred',
          description: 'Failed to communicate with the AI. Please try again.',
        });
        setMessages([
          ...newMessages,
          { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
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

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-background text-foreground">
      <Header htmlContent={htmlContent} cssContent={cssContent} jsContent={jsContent} />
      <main className="grid flex-1 pt-16 grid-cols-1 md:grid-cols-3 xl:grid-cols-4">
        <div className="col-span-1 border-r flex flex-col min-w-[300px] md:min-w-[350px] h-full">
          <ChatPanel
            messages={messages}
            isLoading={isPending}
            onSubmit={handleChatSubmit}
          />
        </div>
        <div className="relative col-span-1 md:col-span-2 xl:col-span-3 h-full flex flex-col">
            <Tabs defaultValue="preview" className="h-full w-full flex flex-col">
                <div className="p-2 border-b">
                    <TabsList>
                        <TabsTrigger value="preview">Preview</TabsTrigger>
                        <TabsTrigger value="code">Code</TabsTrigger>
                    </TabsList>
                </div>
                <TabsContent value="preview" className="flex-1 overflow-auto">
                    <PreviewPanel
                        ref={iframeRef}
                        htmlContent={htmlContent}
                        cssContent={cssContent}
                        jsContent={jsContent}
                    />
                </TabsContent>
                <TabsContent value="code" className="flex-1 overflow-auto bg-gray-950">
                   <CodeBlock code={htmlContent} language="html" />
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
