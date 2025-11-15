# **App Name**: WebForgeAI

## Core Features:

- Chat Interface: Conversational UI in the left sidebar for users to input instructions and receive updates. Message history is maintained in the local state.
- Live Preview: IFrame-based real-time website preview reflecting the current state of index.html, styles.css and script.js.
- Element Highlighting and Editing: Clicking an element in the preview highlights it and opens an editing panel with options to modify text, Tailwind classes, and element-specific actions.
- Download Project: Generates and offers a zip file containing index.html, styles.css, and script.js.
- Contextual HTML Generation: AI tool generates HTML code snippets based on chat inputs and updates the index.html.
- Minimal-Diff Code Updates: The application uses AI to selectively update lines/blocks of code based on chat inputs, ensuring minimal code changes to index.html, styles.css and script.js.
- Export to Tailwind CSS: Export of CSS styles that work with tailwind.

## Style Guidelines:

- Primary color: Deep Indigo (#3F51B5) to give a corporate, trustworthy feel.
- Background color: Light Gray (#F5F5F5), nearly white, but not pure white.
- Accent color: Orange (#FF9800) to draw attention to buttons and interactive elements.
- Headline font: 'Space Grotesk', sans-serif. Body font: 'Inter', sans-serif. Space Grotesk will be used for headlines and Inter for body text.
- Two-panel layout: Left sidebar for chat, right side for website preview. Fixed header with project title and export button. Use Tailwind CSS grid for responsive design.
- Use Font Awesome or similar icon library for UI elements. Icons should be simple and convey their purpose clearly.
- Subtle transitions for UI updates (e.g., chat messages appearing). Use Tailwind CSS transition classes for smooth animations.