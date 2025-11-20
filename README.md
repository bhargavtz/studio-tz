# Next Inai

Next Inai is an AI-powered website builder that helps you create modern, high-conversion, visually polished websites with ease. Built with Next.js, React, and Tailwind CSS, it provides an intuitive interface for designing and developing web projects through AI assistance.

## Features

- **AI-Powered Generation**: Generate complete HTML/CSS/JS projects from natural language prompts
- **Interactive Preview**: Real-time preview with element selection and editing capabilities
- **Multi-File Support**: Create complex projects with proper folder structure and multiple files
- **Modern Tech Stack**: Built with Next.js, React, TypeScript, and Tailwind CSS
- **Responsive Design**: Fully responsive interface that works on all devices
- **Live Preview**: See your changes instantly in the built-in preview panel

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd studio-tz
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Run the development server:
```bash
npm run dev
```

5. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

1. **Start a New Project**: Begin by describing the website you want to create
2. **AI Generation**: Use natural language to generate HTML, CSS, and JavaScript
3. **Interactive Editing**: Click on elements in the preview to select and modify them
4. **Real-time Preview**: See changes instantly as you make them
5. **Export**: Download your completed project as a ZIP file

## Project Structure

```
src/
├── app/                 # Next.js app directory
│   ├── layout.tsx      # Root layout component
│   └── page.tsx        # Main page component
├── components/         # React components
│   ├── chat/          # Chat panel components
│   ├── layout/        # Layout components
│   └── preview/       # Preview panel components
├── ai/                # AI flows and configurations
│   └── flows/         # Generation flows
└── lib/               # Utility libraries
    ├── initial-content.ts
    └── zip.ts
```

## Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **AI**: Google Genkit for AI-powered generation
- **Build Tools**: Vite, SWC
- **Code Quality**: ESLint, Prettier

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue on the GitHub repository.
