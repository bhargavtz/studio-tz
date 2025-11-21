import os
import json
import asyncio
from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    # Try to look in parent directory .env if not found in current
    env_path_parent = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path_parent)
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    try:
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")
else:
    print("Warning: GOOGLE_API_KEY or GEMINI_API_KEY not found in environment variables")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    prompt: str

# Schemas
HTML_PAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "string", "description": "Unique identifier for the page (kebab-case)."},
        "filename": {"type": "string", "description": "HTML filename such as index.html or about.html."},
        "label": {"type": "string", "description": "Human-friendly name (Home, About, Pricing, etc.)."},
        "body": {"type": "string", "description": "Full BODY CONTENT for that page (no <html> or <body> tags)."}
    },
    "required": ["id", "filename", "label", "body"]
}

GENERATE_HTML_SCHEMA = {
    "type": "object",
    "properties": {
        "pages": {
            "type": "array",
            "items": HTML_PAGE_SCHEMA,
            "description": "One or more HTML pages that reference each other."
        },
        "css": {"type": "string", "description": "Shared CSS for all pages."},
        "js": {"type": "string", "description": "Shared JavaScript for all pages."}
    },
    "required": ["pages", "css", "js"]
}

PROJECT_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "path": {"type": "string", "description": "File path including folders"},
        "content": {"type": "string", "description": "Complete file content"},
        "type": {"type": "string", "description": "File type (html, css, javascript, vue, json, md, other)"},
        "description": {"type": "string", "description": "Brief description"}
    },
    "required": ["path", "content", "type"]
}

PROJECT_STRUCTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": PROJECT_FILE_SCHEMA,
            "description": "All files in the project"
        },
        "mainEntry": {"type": "string", "description": "Main entry point file path"},
        "description": {"type": "string", "description": "Project description and setup instructions"}
    },
    "required": ["files", "mainEntry", "description"]
}

# Prompts
HTML_PROMPT_TEMPLATE = """You are Next Inai — a world-class front-end engineer and product designer focused on creating modern, high-conversion, visually polished websites.

Think deeply about the user's request and translate it into a clean, responsive, professional website. Do NOT include any explanation or internal reasoning. Only output the final code.

User request: {prompt}

REQUIREMENTS (STRICT)
1. PRIMARY STYLING: Tailwind CSS loaded via CDN is the primary styling layer. Use Tailwind utility classes heavily for layout, spacing, typography, and colors.
2. SUPPLEMENTARY CSS: You may include simple standard CSS in the "css" output for custom classes, keyframes, @layer overrides, and edge-case polish. Keep normal CSS minimal and focused.
3. OUTPUT FORMAT: Return a JSON object with code for multiple pages that work together:
- pages: Array of 1-6 objects describing each HTML page. For every page provide:
  * id: unique identifier (kebab-case)
  * filename: the HTML filename (e.g., index.html, about.html, contact.html)
  * label: human-friendly name (e.g., Home, About, Contact)
  * body: COMPLETE HTML PAGE CONTENT including:
    - <!DOCTYPE html> declaration
    - <html lang="en"> tag
    - <head> section with:
      * <meta charset="UTF-8">
      * <meta name="viewport" content="width=device-width, initial-scale=1.0">
      * <title> tag with page-specific title
      * <script src="https://cdn.tailwindcss.com"></script> for Tailwind CSS
      * <link rel="stylesheet" href="styles.css"> for shared custom CSS
    - <body> section with the page content
    - <script src="script.js"></script> at the end of body for shared JavaScript
  * Ensure navigation links in each page use relative paths (href="about.html", href="index.html") to link between pages
- css: Shared Tailwind layer overrides or custom CSS that should live in styles.css (loaded by every page).
- js: Shared JavaScript for interactivity. Prefer progressive enhancement with tasteful motion. You may use Vue 3's global build (available as window.Vue) to structure components/state when it improves the experience, or stick to vanilla JS where simpler.

RESPONSIVE + LAYOUT RULES
4. Mobile-first and responsive down to 360px. Use fluid spacing: max-w, mx-auto, px-4. Stack sections vertically on small screens.
5. Avoid giant hero gaps: no min-height larger than viewport minus header. Keep hero vertically centered with balanced padding (e.g., py-12 to py-20).
6. No blank space taller than ~25% of the viewport prior to meaningful content.
7. Use semantic HTML elements and accessible attributes (aria-* where appropriate).

UI / DESIGN / INTERACTIONS
8. Visual polish: clean typography, balanced spacing, professional color palette with Tailwind classes, clear CTAs, and consistent UI scales.
9. Micro-interactions: subtle hover/focus states, reveal-on-scroll or fade-in animations, and tasteful motion. Prefer CSS keyframes or Tailwind keyframes; use Vue transitions only when reactive state or components materially improve UX.
10. Navigation: provide a simple top navigation with links to all pages. Navigation should be consistent across all pages. Use smooth scrolling for anchor links within the same page.

TECHNICAL CONSTRAINTS
11. Allowed external resources: Tailwind CDN (https://cdn.tailwindcss.com) and Vue 3 global build (https://unpkg.com/vue@3/dist/vue.global.js) only. No other external libraries or APIs.
12. No server-side code, no API keys, no references to backend endpoints. The result must be self-contained static content.
13. Keep JavaScript minimal and progressive: the page must work without JS for basic content and layout; JS enhances interactivity.

DELIVERABLE FORMAT (EXACT)
14. Return ONLY the JSON object. Do NOT include any surrounding commentary, analysis, or extra fields.
15. Each page's "body" field must contain the COMPLETE HTML document from <!DOCTYPE html> to </html>.
"""

MULTI_FILE_PROMPT_TEMPLATE = """You are Next Inai - an expert full-stack developer specializing in creating complete, production-ready web projects with multiple files and proper folder structure.

Your task: Create a complete multi-file website/project based on the user's request. Generate all necessary files with proper folder organization.

User Request: {prompt}

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

Create a complete, professional project that showcases modern web development capabilities.
"""

@app.post("/chat")
async def chat(request: ChatRequest):
    prompt = request.prompt
    
    # Detect if this is a multi-file request
    is_multi_file_request = any(keyword in prompt.lower() for keyword in ['multi', 'project', 'website', 'create multiple', 'folder'])
    
    async def event_generator():
        try:
            # Send initial status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Thinking...', 'stage': 'init'})}\n\n"
            
            # Dynamically select model
            model_name = 'gemini-2.0-flash'
            try:
                available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                
                # Check for specific requested model first
                if 'models/gemini-2.0-flash' in available_models:
                    model_name = 'models/gemini-2.0-flash'
                elif 'models/gemini-1.5-flash' in available_models:
                    model_name = 'models/gemini-1.5-flash'
                elif any('flash' in m.lower() for m in available_models):
                    # Fallback to any flash model
                    model_name = next(m for m in available_models if 'flash' in m.lower())
                elif 'models/gemini-1.5-pro' in available_models:
                    model_name = 'models/gemini-1.5-pro'
            except Exception as e:
                print(f"Error selecting model: {e}")
            
            print(f"Using model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            response_data = None
            is_multi_file = False
            
            if is_multi_file_request:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating multi-file project structure...', 'stage': 'generating'})}\n\n"
                
                full_prompt = MULTI_FILE_PROMPT_TEMPLATE.format(prompt=prompt)
                
                result = await model.generate_content_async(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=PROJECT_STRUCTURE_SCHEMA
                    )
                )
                
                response_data = json.loads(result.text)
                is_multi_file = True
                
                # Send file-by-file updates
                if "files" in response_data and isinstance(response_data["files"], list):
                    for file in response_data["files"]:
                        yield f"data: {json.dumps({'type': 'file', 'file': {'name': file['path'], 'content': file['content'], 'type': file['type']}})}\n\n"
            
            else:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating HTML, CSS, and JavaScript...', 'stage': 'generating'})}\n\n"
                
                full_prompt = HTML_PROMPT_TEMPLATE.format(prompt=prompt)
                
                result = await model.generate_content_async(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        response_schema=GENERATE_HTML_SCHEMA
                    )
                )
                
                response_data = json.loads(result.text)
                
                # Send all pages as separate HTML files
                if "pages" in response_data and len(response_data["pages"]) > 0:
                    for page in response_data["pages"]:
                        filename = page.get("filename", "index.html")
                        content = page.get("body", "")
                        yield f"data: {json.dumps({'type': 'file', 'file': {'name': filename, 'content': content, 'type': 'html'}})}\n\n"
                
                # Send shared CSS file
                if "css" in response_data and response_data["css"]:
                    yield f"data: {json.dumps({'type': 'file', 'file': {'name': 'styles.css', 'content': response_data['css'], 'type': 'css'}})}\n\n"
                    
                # Send shared JS file
                if "js" in response_data and response_data["js"]:
                    yield f"data: {json.dumps({'type': 'file', 'file': {'name': 'script.js', 'content': response_data['js'], 'type': 'javascript'}})}\n\n"
            
            # Send completion message
            yield f"data: {json.dumps({'type': 'complete', 'response': response_data, 'isMultiFile': is_multi_file, 'success': True})}\n\n"
            
        except Exception as e:
            print(f"Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'success': False})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
