import { type Message } from '@/components/chat/chat-message';

export type HtmlPageFile = {
  id: string;
  filename: string;
  label: string;
  body: string;
};

export const initialPages: HtmlPageFile[] = [
  {
    id: 'home',
    filename: 'index.html',
    label: 'Home',
    body: `<div class="bg-gray-900 text-white font-sans">
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
</div>`,
  },
];

export const initialHtml = initialPages[0]?.body ?? '';

export const initialCss = `/* Custom styles can go here */`;

export const initialJs = `console.log("Welcome to your Next Inai project!");`;

export const initialMessages: Message[] = [
  {
    role: 'assistant',
    content: "Hi, I'm Next Inai. Describe the experience you want—playful micro-interactions or premium motion?",
  },
];
