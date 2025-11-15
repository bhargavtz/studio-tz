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

const initialHtml = `<div class="bg-gray-900 text-white font-sans">
  <div class="container mx-auto px-4 py-20 text-center">
    <h1 class="text-5xl font-bold font-headline text-white mb-4">Build Your Website with AI</h1>
    <p class="text-xl text-gray-300 max-w-2xl mx-auto">
      Describe the website you want to build in the chat, and I'll generate the code for you. Click on any element in the preview to edit it.
    </p>
    <div class="mt-8">
      <button class="bg-primary text-primary-foreground font-bold py-3 px-8 rounded-lg text-lg hover:bg-primary/80 transition-colors">
        Get Started Now
      </button>
    </div>
  </div>
</div>`;
const initialCss = `/* Custom styles can go here */`;
const initialJs = `console.log("Welcome to your WebForgeAI project!");`;
const initialMessages: Message[] = [
  {
    role: 'assistant',
    content: "Hello! I'm WebForgeAI. How can I help you build your website today?",
  },
];

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
        const fullPrompt = `The user wants to update their website.
Current HTML:
---
${htmlContent}
---
User request: "${prompt}"

Based on this, generate new, complete HTML code with Tailwind classes. The user might be asking for a new component or a modification of the existing code. Your goal is to provide a single, coherent HTML body that reflects their request.`;

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
        <div className="col-span-1 border-r flex flex-col min-w-[300px] md:min-w-[350px]">
          <ChatPanel
            messages={messages}
            isLoading={isPending}
            onSubmit={handleChatSubmit}
          />
        </div>
        <div className="relative col-span-1 md:col-span-2 xl:col-span-3">
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
