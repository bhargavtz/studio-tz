import os
import json
import asyncio
from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Configure Groq API
groq_api_key = os.getenv("GROQ_API_KEY")
groq_model = os.getenv("GROQ_MODEL") or "llama-3.3-70b-versatile"

if not groq_api_key:
    # Try to look in parent directory .env if not found in current
    env_path_parent = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(dotenv_path=env_path_parent)
    groq_api_key = os.getenv("GROQ_API_KEY")

if groq_api_key:
    print(f"✅ Groq API configured")
    print(f"Using model: {groq_model}")
else:
    print("⚠️ Warning: GROQ_API_KEY not found in environment variables")

# Groq API configuration
GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_HEADERS = {
    "Authorization": f"Bearer {groq_api_key}",
    "Content-Type": "application/json"
}

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
        "type": {"type": "string", "description": "File type (html, css, javascript, vue, json, md, other) - optional"},
        "description": {"type": "string", "description": "Brief description - optional"}
    },
    "required": ["path", "content"]
}

PROJECT_STRUCTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": PROJECT_FILE_SCHEMA,
            "description": "All files in the project"
        },
        "mainEntry": {"type": "string", "description": "Main entry point file path (optional)"},
        "description": {"type": "string", "description": "Project description and setup instructions (optional)"}
    },
    "required": ["files"]
}

# Prompts
HTML_PROMPT_TEMPLATE = """You are Next Inai — a world-class front-end engineer and product designer focused on creating modern, high-conversion, visually stunning websites with cutting-edge 3D graphics and smooth animations.

⚠️ CRITICAL: Keep JavaScript CONCISE (max 100-150 lines total). Use minimal, focused code. Avoid verbose comments. This prevents JSON generation failures.

Think deeply about the user's request and translate it into a clean, responsive, professional website with WOW-factor visuals. Do NOT include any explanation or internal reasoning. Only output the final code.

User request: {prompt}

REQUIREMENTS (STRICT)
1. PRIMARY STYLING: Tailwind CSS loaded via CDN is the primary styling layer. Use Tailwind utility classes heavily for layout, spacing, typography, and colors.
2. SUPPLEMENTARY CSS: You may include CSS in the "css" output for custom classes, keyframes, @layer overrides, 3D transforms, animations, and visual polish.
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
      * <link rel="preconnect" href="https://fonts.googleapis.com">
      * <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
      * <link href="https://fonts.googleapis.com/css2?family=[FONT_NAMES]&display=swap" rel="stylesheet"> for Google Fonts
      * <script src="https://cdn.tailwindcss.com"></script> for Tailwind CSS
      * <link rel="stylesheet" href="styles.css"> for shared custom CSS
    - <body> section with the page content
    - <script src="script.js"></script> at the end of body for shared JavaScript
  * Ensure navigation links in each page use relative paths (href="about.html", href="index.html") to link between pages
- css: Shared CSS including custom classes, keyframes, 3D transforms, gradient definitions, and animations.
- js: Shared JavaScript for interactivity and animations. Use progressive enhancement with tasteful motion.

RESPONSIVE + LAYOUT RULES
4. Mobile-first and responsive down to 360px. Use fluid spacing: max-w, mx-auto, px-4. Stack sections vertically on small screens.
5. Avoid giant hero gaps: no min-height larger than viewport minus header. Keep hero vertically centered with balanced padding (e.g., py-12 to py-20).
6. No blank space taller than ~25% of the viewport prior to meaningful content.
7. Use semantic HTML elements and accessible attributes (aria-* where appropriate).

UI / DESIGN / INTERACTIONS - MAKE IT STUNNING!
8. PREMIUM VISUAL DESIGN (CRITICAL):
   - Use modern gradient backgrounds (mesh gradients, radial gradients, animated gradients)
   - Glassmorphism effects where appropriate (backdrop-blur, semi-transparent backgrounds)
   - Professional color palettes using HSL values for harmony
   - PREMIUM TYPOGRAPHY (MANDATORY):
     * Use Google Fonts CDN for beautiful, professional fonts
     * Choose 2-3 complementary fonts: one for headings, one for body, optional one for accents
     * Popular premium combinations:
       - Headings: Inter, Poppins, Montserrat, Outfit, Space Grotesk, Playfair Display
       - Body: Inter, Open Sans, Roboto, Lato, Work Sans, Source Sans Pro
       - Accent/Display: Righteous, Bebas Neue, Russo One, Orbitron (for tech/modern)
     * Set fonts in CSS using font-family with fallbacks
     * Use varied font weights (300, 400, 500, 600, 700, 800) for hierarchy
     * Perfect letter-spacing and line-height for readability
   - Consistent spacing and visual rhythm

9. 2D ANIMATIONS & MICRO-INTERACTIONS (REQUIRED):
   - Icon animations: scale, rotate, color transitions on hover
   - Smooth scroll-triggered reveal animations (fade-in, slide-up)
   - Parallax scrolling effects for depth
   - Smooth page transitions
   - Loading animations and skeleton screens
   - Button hover effects (glow, lift, color shift)
   - Card hover effects (lift, shadow, border glow)
   - Use CSS transforms, transitions, and @keyframes
   - Implement IntersectionObserver for scroll animations

10. 3D ELEMENTS & EFFECTS (USE WHEN APPROPRIATE):
   - CSS 3D transforms for cards, images, and UI elements (transform: rotateX(), rotateY(), translateZ())
   - Animated 3D backgrounds using CSS or Canvas
   - Floating 3D shapes and geometric patterns
   - 3D hover effects on cards and buttons
   - Perspective effects for depth
   - Use transform-style: preserve-3d for nested 3D elements
   - Create 3D particle effects with Canvas API when requested
   - Implement mouse-tracking 3D tilt effects

11. ADVANCED ANIMATIONS:
   - SVG path animations for icons and illustrations
   - Morphing shapes and transitions
   - Staggered animations for lists and grids
   - Smooth easing functions (cubic-bezier)
   - Keyframe-based complex animations
   - Interactive cursor effects (custom cursors, magnetic effects)

12. Navigation: Provide a modern navigation with smooth transitions, links to all pages, mobile menu with smooth slide/fade animation. Use smooth scrolling for anchor links.

TECHNICAL CONSTRAINTS & ALLOWED LIBRARIES
13. ALLOWED LIBRARIES (load via CDN in <head>):
   - Tailwind CSS: https://cdn.tailwindcss.com (REQUIRED - ALWAYS include this)
   - Three.js: https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js (USE for advanced 3D scenes, particle systems, 3D models)

14. WHEN TO USE EACH TECHNOLOGY:
   - Three.js: For 3D backgrounds, floating geometric shapes, particle systems, animated 3D objects, complex 3D scenes
   - CSS Animations: For hover effects, transitions, basic animations, scroll reveals
   - Canvas API: For custom particle effects, generative art, 2D animations, interactive graphics
   - IntersectionObserver: For scroll-triggered animations and lazy loading
   - Vanilla JavaScript: For interactivity, DOM manipulation, and event handling

15. No server-side code, no API keys, no external API calls. Self-contained static content only.

16. Progressive enhancement: Basic content and layout work without JS; JS adds interactivity and animations.

ANIMATION IMPLEMENTATION GUIDELINES
17. For scroll-triggered animations:
   - Use IntersectionObserver API or GSAP ScrollTrigger
   - Fade in elements as they enter viewport
   - Stagger animations for lists/grids
   - Parallax effects with different scroll speeds

18. For 3D effects:
   - Use CSS 3D transforms for simple card/button effects
   - Use Three.js for complex 3D scenes (backgrounds, particle systems)
   - Add mouse-tracking for interactive 3D tilt effects
   - Ensure 3D effects are subtle and enhance UX

19. For icon animations:
   - Scale, rotate, color transitions on hover
   - Bounce, pulse, or wiggle effects on interaction
   - SVG path animations for line drawings
   - Use CSS transforms for performance

QUALITY STANDARDS
20. Every website must feel PREMIUM and MODERN:
   - Smooth 60fps animations
   - Professional color palettes
   - Consistent design language
   - Clear visual hierarchy
   - Accessible and responsive
   - Fast loading (optimize animations)

DELIVERABLE FORMAT (EXACT)
22. Return ONLY the JSON object. Do NOT include any surrounding commentary, analysis, or extra fields.
23. Each page's "body" field must contain the COMPLETE HTML document from <!DOCTYPE html> to </html>.
24. Include necessary CDN scripts (Tailwind is REQUIRED, Three.js if using 3D) in the <head> section of each page.
25. KEEP CODE CONCISE: Avoid overly long JavaScript files. Keep scripts focused and efficient to prevent JSON generation failures.
26. Make it STUNNING. Make it PREMIUM. Make it PIXEL-PERFECT. This is your masterpiece.
"""

MULTI_FILE_PROMPT_TEMPLATE = """You are Next Inai - an expert full-stack developer specializing in creating complete, production-ready web projects with stunning 3D graphics, smooth animations, and premium visual design.

⚠️ CRITICAL: Keep ALL JavaScript files CONCISE (max 100-150 lines each). Use minimal, focused code. Avoid verbose comments or unnecessary complexity. This prevents JSON generation failures.

Your task: Create a complete multi-file website/project based on the user's request. Generate all necessary files with proper folder organization and modern visual effects.

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
   - Configuration files (.json)
   - Documentation files (.md)
   - Any other necessary file types

3. **Technology Stack**
   - **Frontend**: HTML5, CSS3, JavaScript (ES6+)
   - **Styling**: Tailwind CSS CDN (REQUIRED) or custom CSS with gradients, glassmorphism
   - **Typography**: Google Fonts CDN for premium, professional fonts
   - **3D Graphics**: Three.js for 3D scenes and animations
   - **Animations**: CSS animations, transitions, keyframes, IntersectionObserver
   - **Canvas**: For particle effects, generative art, 2D animations
   - **Build Tools**: No complex build tools needed - keep it simple
   - **No Backend**: Static files only

4. **Content Requirements**
   - Each file must be complete and functional
   - Include proper DOCTYPE, meta tags, and structure for HTML files
   - Include Google Fonts preconnect and font link tags in <head> for premium typography
   - Choose 2-3 complementary Google Fonts (headings + body + optional accent)
   - CSS should include custom animations, 3D transforms, gradients, and font-family declarations
   - JavaScript should be modular, error-free, concise, and include animation logic

5. **Multi-page Support**
   - For multi-page websites, create separate HTML files
   - Include smooth navigation between pages with transitions
   - Shared CSS/JS files should be properly linked across all pages
   - Consistent design and animations across pages

6. **PREMIUM VISUAL DESIGN (REQUIRED)**
   - Modern gradient backgrounds (mesh gradients, animated gradients)
   - Glassmorphism effects (backdrop-blur, semi-transparent cards)
   - Professional HSL-based color palettes
   - Premium typography with proper hierarchy
   - Smooth 60fps animations
   - Micro-interactions on all interactive elements

7. **3D ELEMENTS & ANIMATIONS**
   - Use Three.js for complex 3D scenes (geometric shapes, particle systems)
   - CSS 3D transforms for cards and UI elements (rotateX, rotateY, translateZ)
   - Animated 3D backgrounds with floating shapes
   - Mouse-tracking 3D tilt effects
   - Perspective effects for depth
   - Use transform-style: preserve-3d for nested elements

8. **2D ANIMATIONS & INTERACTIONS**
   - IntersectionObserver for scroll-triggered reveal animations
   - Icon animations: scale, rotate, color transitions on hover using CSS
   - Parallax scrolling effects with different speeds using CSS transforms
   - SVG path animations for illustrations
   - Smooth page transitions and loading states
   - Staggered animations for lists and grids using animation-delay
   - Custom cursor effects (magnetic, glow) with JavaScript

9. **ALLOWED LIBRARIES (via CDN)**
   - Tailwind CSS: https://cdn.tailwindcss.com (REQUIRED)
   - Three.js: https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.min.js

10. **WHEN TO USE LIBRARIES**
   - Three.js: 3D backgrounds, floating objects, particle effects, 3D models
   - GSAP + ScrollTrigger: Scroll animations, parallax, timeline animations
   - Lottie: Complex icon animations
   - CSS: Simple hover effects, basic transitions
   - Canvas: Particle effects, generative art

11. **RESPONSIVE DESIGN**
   - Mobile-first approach down to 360px
   - Responsive animations (reduce motion on mobile if needed)
   - Touch-friendly interactions
   - Optimized performance on all devices

12. **ACCESSIBILITY & PERFORMANCE**
   - Semantic HTML with ARIA attributes
   - Keyboard navigation support
   - Prefers-reduced-motion media query support
   - Optimized animations for 60fps
   - Fast loading times

13. **Output Format**
   Return a JSON object with:
   - files: Array of all project files with path, content, type, and description
   - mainEntry: Path to the main entry point (usually index.html)
   - description: Project overview and setup instructions

Create a complete, professional, ABSOLUTELY STUNNING project with PREMIUM visuals, SMOOTH animations, and modern 3D effects that WOW users! Make it PIXEL-PERFECT!

14. **PREMIUM QUALITY CHECKLIST**
    - PIXEL-PERFECT spacing and alignment
    - RICH color palettes with gradients (no flat colors)
    - Smooth hover states on ALL interactive elements
    - Loading states and skeleton screens
    - 60fps smooth animations (use transform and opacity)
    - Attention to micro-details (shadows, borders, focus states)
    - Professional typography pairing
    - Accessible and responsive (360px to desktop)
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
            
            # Use configured Groq model
            model_name = groq_model
            print(f"Using Groq model: {model_name}")
            
            response_data = None
            is_multi_file = False
            
            # Select schema and prompt based on request type
            if is_multi_file_request:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating multi-file project structure...', 'stage': 'generating'})}\n\n"
                full_prompt = MULTI_FILE_PROMPT_TEMPLATE.format(prompt=prompt)
                schema = PROJECT_STRUCTURE_SCHEMA
                is_multi_file = True
            else:
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating HTML, CSS, and JavaScript...', 'stage': 'generating'})}\n\n"
                full_prompt = HTML_PROMPT_TEMPLATE.format(prompt=prompt)
                schema = GENERATE_HTML_SCHEMA
            
            # Call Groq API
            groq_payload = {
                "model": model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "website_schema",
                        "strict": True,
                        "schema": schema
                    }
                }
            }
            
            # Make API call to Groq
            response = requests.post(
                GROQ_BASE_URL,
                headers=GROQ_HEADERS,
                json=groq_payload,
                timeout=120
            )
            
            if response.status_code != 200:
                error_msg = f"Groq API error: {response.status_code} - {response.text}"
                print(error_msg)
                yield f"data: {json.dumps({'type': 'error', 'error': error_msg, 'success': False})}\n\n"
                return
            
            # Parse response
            api_response = response.json()
            
            if 'choices' in api_response and len(api_response['choices']) > 0:
                content = api_response['choices'][0]['message']['content']
                response_data = json.loads(content)
            else:
                yield f"data: {json.dumps({'type': 'error', 'error': 'No response from model', 'success': False})}\n\n"
                return
            
            # Process and send the response based on type
            if is_multi_file:
                # Send file-by-file updates with typing animation
                if "files" in response_data and isinstance(response_data["files"], list):
                    for file in response_data["files"]:
                        file_content = file['content']
                        file_name = file['path']
                        
                        # Auto-detect file type if not provided
                        file_type = file.get('type', '')
                        if not file_type:
                            # Detect from extension
                            if file_name.endswith('.html') or file_name.endswith('.htm'):
                                file_type = 'html'
                            elif file_name.endswith('.css'):
                                file_type = 'css'
                            elif file_name.endswith('.js') or file_name.endswith('.mjs'):
                                file_type = 'javascript'
                            elif file_name.endswith('.vue'):
                                file_type = 'vue'
                            elif file_name.endswith('.json'):
                                file_type = 'json'
                            elif file_name.endswith('.md'):
                                file_type = 'md'
                            else:
                                file_type = 'other'
                        
                        # Stream code chunks for typing animation
                        chunk_size = 40  # characters per chunk
                        for i in range(0, len(file_content), chunk_size):
                            chunk = file_content[i:i+chunk_size]
                            yield f"data: {json.dumps({'type': 'code_chunk', 'chunk': chunk, 'file_name': file_name})}\n\n"
                            await asyncio.sleep(0.015)  # 15ms delay for smooth typing
                        
                        # Send complete file after typing animation
                        yield f"data: {json.dumps({'type': 'file', 'file': {'name': file_name, 'content': file_content, 'type': file_type}})}\n\n"
            else:
                # Send all pages as separate HTML files with typing animation
                if "pages" in response_data and len(response_data["pages"]) > 0:
                    for page in response_data["pages"]:
                        filename = page.get("filename", "index.html")
                        content = page.get("body", "")
                        
                        # Stream HTML chunks for typing animation
                        chunk_size = 40
                        for i in range(0, len(content), chunk_size):
                            chunk = content[i:i+chunk_size]
                            yield f"data: {json.dumps({'type': 'code_chunk', 'chunk': chunk, 'file_name': filename})}\n\n"
                            await asyncio.sleep(0.015)
                        
                        # Send complete file
                        yield f"data: {json.dumps({'type': 'file', 'file': {'name': filename, 'content': content, 'type': 'html'}})}\n\n"
                
                # Send shared CSS file with typing animation
                if "css" in response_data and response_data["css"]:
                    css_content = response_data["css"]
                    chunk_size = 40
                    for i in range(0, len(css_content), chunk_size):
                        chunk = css_content[i:i+chunk_size]
                        yield f"data: {json.dumps({'type': 'code_chunk', 'chunk': chunk, 'file_name': 'styles.css'})}\n\n"
                        await asyncio.sleep(0.015)
                    
                    yield f"data: {json.dumps({'type': 'file', 'file': {'name': 'styles.css', 'content': css_content, 'type': 'css'}})}\n\n"
                    
                # Send shared JS file with typing animation
                if "js" in response_data and response_data["js"]:
                    js_content = response_data["js"]
                    chunk_size = 40
                    for i in range(0, len(js_content), chunk_size):
                        chunk = js_content[i:i+chunk_size]
                        yield f"data: {json.dumps({'type': 'code_chunk', 'chunk': chunk, 'file_name': 'script.js'})}\n\n"
                        await asyncio.sleep(0.015)
                    
                    yield f"data: {json.dumps({'type': 'file', 'file': {'name': 'script.js', 'content': js_content, 'type': 'javascript'}})}\n\n"
            
            # Send completion message
            yield f"data: {json.dumps({'type': 'complete', 'response': response_data, 'isMultiFile': is_multi_file, 'success': True})}\n\n"
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            yield f"data: {json.dumps({'type': 'error', 'error': str(e), 'success': False})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
