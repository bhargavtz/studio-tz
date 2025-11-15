'use client';

import { useState, useEffect, useCallback, useTransition } from 'react';
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

const initialHtml = `<div class="bg-gray-50 dark:bg-gray-900 min-h-screen flex items-center justify-center font-body">
  <div class="text-center p-8">
    <h1 class="text-5xl font-bold font-headline text-gray-800 dark:text-white mb-4">Welcome to WebForgeAI</h1>
    <p class="text-xl text-gray-600 dark:text-gray-300">
      Tell me what you want to build in the chat on the left.
    </p>
    <p class="text-sm text-gray-400 mt-8">
      For example: "Create a hero section with a title, a subtitle, and a call-to-action button."
    </p>
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
    if (event.source !== event.currentTarget) { // Ensure message is from iframe
        const { type, ...data } = event.data;
        if (type === 'webforge-select') {
          setSelectedElement(data as SelectedElement);
        }
    }
  }, []);

  useEffect(() => {
    window.addEventListener('message', handleMessage);
    return () => {
      window.removeEventListener('message', handleMessage);
    };
  }, [handleMessage]);

  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-background text-foreground">
      <Header htmlContent={htmlContent} cssContent={cssContent} jsContent={jsContent} />
      <main className="grid flex-1 pt-16 grid-cols-3 xl:grid-cols-4">
        <div className="col-span-1 border-r flex flex-col min-w-[350px]">
          <ChatPanel
            messages={messages}
            isLoading={isPending}
            onSubmit={handleChatSubmit}
          />
        </div>
        <div className="relative col-span-2 xl:col-span-3">
            <Tabs defaultValue="preview" className="h-full w-full flex flex-col">
                <div className="p-2 border-b">
                    <TabsList>
                        <TabsTrigger value="preview">Preview</TabsTrigger>
                        <TabsTrigger value="code">Code</TabsTrigger>
                    </TabsList>
                </div>
                <TabsContent value="preview" className="flex-1 overflow-auto">
                    <PreviewPanel
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