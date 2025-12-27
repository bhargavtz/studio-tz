"""
NCD INAI - Code Generator Agent

Generates HTML, CSS, and JavaScript from blueprints.
"""

from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings


CODE_GENERATOR_PROMPT = """You are an **AWARD-WINNING FRONTEND ENGINEER & MOTION DESIGNER**.
Your task is to take a blueprint and transform it into a **Production-Ready, High-Performance, and visually STUNNING website**.

Blueprint:
{blueprint}

### 🏆 EXPERT STANDARDS (STRICT):
1.  **Tech Stack**:
    - HTML5 (Semantic, Accessible, SEO-optimized). usage of `<section>`, `<article>`, `<nav>` is MANDATORY.
    - **Tailwind CSS (CDN) - MANDATORY**: You MUST include `<script src="https://cdn.tailwindcss.com"></script>` in <head>
    - **Custom CSS** is REQUIRED for animations, glassmorphism, and unique polish.
    - Vanilla JS (ES6+) for smooth interactions. NO JQuery. NO React.

2.  **Zero-Boredom Policy**:
    - EVERY interactive element (buttons, cards, links) MUST have a `:hover` and `:active` state.
    - Use `transition-all duration-300` for smooth effects.
    - Elements should "fade in" or "slide up" on scroll (using IntersectionObserver in JS).

3.  **Visual Excellence**:
    - **Glassmorphism**: Use `backdrop-filter: blur(12px)` and semi-transparent backgrounds for modern cards/navbars.
    - **Typography**: Use the requested font, but ensure proper `line-height`, `letter-spacing`, and hierarchy.
    - **Whitespace**: Use generous padding/margin. Do not cram content.
    - **Hero Section**: Must be `min-h-screen`, vertically centered, with a compelling background (gradient or placeholder image).

4.  **Content Intelligence**:
    - **NEVER** output raw data structures (e.g., `['a', 'b']`). Always render as Lists or Grids.
    - If no image is provided, use a stylish CSS Gradient placeholder, not a broken link.
    - Navbar: Must be `fixed` top, glassmorphism style, with mobile hamburger menu functioning perfectly.

### 🎨 DESIGN SYSTEM:
- **Theme**:
  * Primary: {primaryColor}
  * Background: {backgroundColor}
  * Text: {textColor}
  * Font: {fontFamily}
- **Style**: Execute the "{style}" look with precision.
  - If "Minimal": Use lots of white space, thin borders.
  - If "Bold": Use large text, high contrast, solid shadows.

### 📂 OUTPUT FORMAT (JSON ONLY):
Return a single JSON object. NO markdown.
{{
    "html": "<!DOCTYPE html>...<head>...<script src='https://cdn.tailwindcss.com'></script><link rel='stylesheet' href='styles/main.css'>...</head>...<script src='scripts/main.js'></script>...",
    "css": "/* styles/main.css */\n:root {{ ... }} \n/* Custom Animations */\n@keyframes fadeInUp {{ ... }} ...",
    "js": "// scripts/main.js \n// Mobile Menu Logic \n// Scroll Animations ..."
}}

### 🚀 FINAL CHECKS:
1.  **Mobile Responsive**: Grid columns must collapse to 1 on mobile (`grid-cols-1 md:grid-cols-3`).
2.  **Navigation Links**: 
    - MULTI-PAGE SITES: Use page links (href="about.html", href="contact.html") - See {{pages_list}}
    - SINGLE-PAGE SITES: Use anchor links (href="#about", href="#contact")
    - CRITICAL: If {{pages_list}} has multiple items, navigation MUST use .html links!
3.  **Console-Free**: Write robust JS that doesn't error if an element is missing.

### ⚠️ CRITICAL COMPLETENESS RULES (MUST FOLLOW):
1.  **NO EMPTY SECTIONS**: Every section must have complete, visible content
2.  **NO BROKEN LAYOUTS**: All grid items must have proper content (no empty yellow/beige boxes!)
3.  **NO RAW DATA**: Never output arrays like ['item1', 'item2'] - render as proper lists/grids
4.  **NO PLACEHOLDERS**: If blueprint data is missing, generate realistic content instead
5.  **VISUAL QUALITY TEST**: Before submitting, ask yourself: "Would this impress a client?"
6.  **COMPLETE GRIDS**: If using grid-cols-3, ensure exactly 3 (or 6, 9, etc.) items with full content
7.  **PROPER BACKGROUNDS**: Card backgrounds must contrast with section backgrounds
8.  **MINIMUM CONTENT**: Each feature card needs: icon, heading, 2+ sentence description
9.  **REALISTIC TEXT**: Use industry-appropriate, professional copy - not generic filler
10. **BALANCED LAYOUT**: Sections should have proper padding (min 5rem top/bottom)

### 🔴 MANDATORY HTML STRUCTURE:
Your HTML <head> MUST include in this exact order:
1. <meta charset="UTF-8">
2. <meta name="viewport" content="width=device-width, initial-scale=1.0">
3. <title>...</title>
4. <script src="https://cdn.tailwindcss.com"></script>
5. <link rel="stylesheet" href="styles/main.css">
6. <link href="https://fonts.googleapis.com/css2?family={{fontFamily}}...">

Build it like you are trying to win an Awwwards Site of the Day.
Respond ONLY with valid JSON."""


class CodeGeneratorAgent:
    """Agent that generates website code from blueprints."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                temperature=0.6  # Balanced: creative but consistent
            )
        return self._llm
    
    def _get_chain(self):
        if self._chain is None:
            prompt = ChatPromptTemplate.from_template(CODE_GENERATOR_PROMPT)
            parser = JsonOutputParser()
            self._chain = prompt | self._get_llm() | parser
        return self._chain
    
    async def generate(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate HTML, CSS, and JS from blueprint."""
        # Sanitize blueprint data to prevent XSS
        from app.utils.sanitize import sanitize_blueprint_data
        blueprint = sanitize_blueprint_data(blueprint)
        
        theme = blueprint.get("theme", {})
        
        try:
            pages_list = self._format_pages_list(blueprint)
            
            result = await self._get_chain().ainvoke({
                "blueprint": self._format_blueprint(blueprint),
                "pages_list": pages_list,
                "primaryColor": theme.get("primaryColor", "#3B82F6"),
                "secondaryColor": theme.get("secondaryColor", "#1E40AF"),
                "backgroundColor": theme.get("backgroundColor", "#FFFFFF"),
                "textColor": theme.get("textColor", "#1F2937"),
                "accentColor": theme.get("accentColor", "#10B981"),
                "fontFamily": theme.get("fontFamily", "Inter"),
                "style": theme.get("style", "modern")
            })
            
            # Post-process: Inject NCD attributes
            return self._inject_ncd_attributes(result, blueprint)
        except Exception as e:
            print(f"Code generation error: {e}")
            fallback = self._generate_fallback_code(blueprint)
            return self._inject_ncd_attributes(fallback, blueprint)
    
    def _inject_ncd_attributes(self, code: Dict[str, str], blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Inject data-ncd-* attributes into HTML and create scoped CSS."""
        from bs4 import BeautifulSoup
        
        html = code.get("html", "")
        css = code.get("css", "")
        
        soup = BeautifulSoup(html, 'html.parser')
        component_counter = 0
        
        # Track components for CSS scoping
        ncd_ids = []
        
        # Inject into editable elements
        editable_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'button', 'span', 'div', 'section', 'article']
        
        for tag in soup.find_all(editable_tags):
            # Skip if already has ncd-id
            if tag.get('data-ncd-id'):
                ncd_ids.append(tag.get('data-ncd-id'))
                continue
            
            component_counter += 1
            ncd_id = f"ncd-{component_counter:04d}"
            
            # Determine edit type
            if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'span']:
                edit_type = "text"
            elif tag.name == 'a':
                edit_type = "link"
            elif tag.name == 'button':
                edit_type = "button"
            elif tag.name == 'img':
                edit_type = "image"
            else:
                edit_type = "element"
            
            # Add attributes
            tag['data-ncd-id'] = ncd_id
            tag['data-ncd-file'] = "index.html"
            tag['data-ncd-type'] = edit_type
            
            ncd_ids.append(ncd_id)
        
        # Update HTML
        code['html'] = str(soup.prettify())
        
        # Add scoped CSS rules for each NCD ID
        # Only add if not already present to avoid duplication
        if "/* NCD Scoped Styles */" not in css:
            scoped_css = "\n\n/* NCD Scoped Styles */\n"
            for ncd_id in ncd_ids:
                scoped_css += f"[data-ncd-id=\"{ncd_id}\"] {{\n  /* Editable element */\n}}\n\n"
            
            # Append scoped CSS to main CSS file instead of inline
            code['css'] = css + scoped_css
        
        return code
    
    def _format_blueprint(self, blueprint: Dict[str, Any]) -> str:
        """Format blueprint for the prompt."""
        import json
        return json.dumps(blueprint, indent=2)
    
    def _format_pages_list(self, blueprint: Dict[str, Any]) -> str:
        """Format pages list for navigation generation."""
        pages = blueprint.get("pages", [])
        
        if not pages or len(pages) <= 1:
            return "SINGLE PAGE - Use anchor links (#)"
        
        # Multiple pages - list them
        page_links = []
        for page in pages:
            title = page.get("title", "Page")
            slug = page.get("slug", "/").strip("/")
            
            if slug == "" or slug == "index":
                filename = "index.html"  
            else:
                filename = f"{slug}.html"
            
            page_links.append(f"- {title}: {filename}")
        
        return "MULTIPLE PAGES - Use .html links:\n" + "\n".join(page_links)
    
    def _generate_fallback_code(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback code if AI fails."""
        name = blueprint.get("name", "My Website")
        theme = blueprint.get("theme", {})
        
        # HTML Content
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Main CSS -->
    <link rel="stylesheet" href="styles/main.css">
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family={theme.get('fontFamily', 'Inter')}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 text-gray-900">
    <header class="header fixed w-full top-0 z-50 transition-all duration-300">
        <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
            <a href="/" class="text-2xl font-bold text-primary">{name}</a>
            <button class="mobile-menu-btn md:hidden" aria-label="Toggle menu">
                <span class="block w-6 h-0.5 bg-current mb-1"></span>
                <span class="block w-6 h-0.5 bg-current mb-1"></span>
                <span class="block w-6 h-0.5 bg-current"></span>
            </button>
            <ul class="nav-links hidden md:flex space-x-8">
                <li><a href="#home" class="hover:text-primary transition-colors">Home</a></li>
                <li><a href="#about" class="hover:text-primary transition-colors">About</a></li>
                <li><a href="#services" class="hover:text-primary transition-colors">Services</a></li>
                <li><a href="#contact" class="hover:text-primary transition-colors">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home" class="hero min-h-screen flex items-center justify-center text-center pt-20 bg-gradient-to-br from-primary to-secondary text-white">
            <div class="container mx-auto px-6">
                <h1 class="text-5xl md:text-6xl font-bold mb-6 animate-fade-up">Welcome to {name}</h1>
                <p class="text-xl md:text-2xl mb-8 opacity-90">Your trusted partner for excellence</p>
                <a href="#contact" class="btn btn-primary bg-white text-primary px-8 py-3 rounded-lg font-semibold hover:shadow-lg transform hover:-translate-y-1 transition-all">Get Started</a>
            </div>
        </section>

        <section id="about" class="about py-20 bg-white">
            <div class="container mx-auto px-6">
                <h2 class="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-800">About Us</h2>
                <p class="text-center text-gray-600 mb-12 max-w-2xl mx-auto">Delivering excellence through innovation and expertise</p>
                <div class="grid md:grid-cols-2 gap-12 items-center max-w-5xl mx-auto">
                    <div>
                        <p class="text-lg text-gray-700 mb-6">We are dedicated to providing the best service possible. Our team of experts brings years of experience and cutting-edge knowledge to every project.</p>
                        <p class="text-lg text-gray-700">Through innovation, dedication, and a customer-first approach, we help businesses achieve their goals and exceed expectations.</p>
                    </div>
                    <div class="grid grid-cols-2 gap-6">
                        <div class="text-center p-6 bg-blue-50 rounded-lg">
                            <div class="text-4xl font-bold text-primary mb-2">500+</div>
                            <div class="text-gray-600">Happy Clients</div>
                        </div>
                        <div class="text-center p-6 bg-blue-50 rounded-lg">
                            <div class="text-4xl font-bold text-primary mb-2">10+</div>
                            <div class="text-gray-600">Years Experience</div>
                        </div>
                        <div class="text-center p-6 bg-blue-50 rounded-lg">
                            <div class="text-4xl font-bold text-primary mb-2">1000+</div>
                            <div class="text-gray-600">Projects Done</div>
                        </div>
                        <div class="text-center p-6 bg-blue-50 rounded-lg">
                            <div class="text-4xl font-bold text-primary mb-2">98%</div>
                            <div class="text-gray-600">Satisfaction</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section id="services" class="services py-20 bg-gray-50">
            <div class="container mx-auto px-6">
                <h2 class="text-3xl md:text-4xl font-bold text-center mb-4 text-gray-800">Our Services</h2>
                <p class="text-center text-gray-600 mb-12 max-w-2xl mx-auto">We provide comprehensive solutions tailored to your needs</p>
                <div class="grid md:grid-cols-3 gap-8">
                    <div class="service-card bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
                        <div class="text-4xl mb-4">🚀</div>
                        <h3 class="text-xl font-bold mb-4 text-primary">Fast & Reliable</h3>
                        <p class="text-gray-600">Experience lightning-fast performance with our optimized solutions. We ensure your success with proven reliability and cutting-edge technology.</p>
                    </div>
                    <div class="service-card bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
                        <div class="text-4xl mb-4">💎</div>
                        <h3 class="text-xl font-bold mb-4 text-primary">Premium Quality</h3>
                        <p class="text-gray-600">We deliver exceptional quality in every project. Our attention to detail and commitment to excellence sets us apart from the competition.</p>
                    </div>
                    <div class="service-card bg-white p-8 rounded-xl shadow-sm hover:shadow-md transition-all hover:-translate-y-1">
                        <div class="text-4xl mb-4">🎯</div>
                        <h3 class="text-xl font-bold mb-4 text-primary">Results Driven</h3>
                        <p class="text-gray-600">Our data-driven approach ensures measurable results. We focus on what matters most - helping you achieve your business goals and objectives.</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="contact" class="contact py-20 bg-white">
            <div class="container mx-auto px-6">
                <h2 class="text-3xl md:text-4xl font-bold text-center mb-12 text-gray-800">Contact Us</h2>
                <form class="contact-form max-w-lg mx-auto space-y-6" id="contactForm">
                    <div class="form-group">
                        <label for="name" class="block mb-2 font-medium">Name</label>
                        <input type="text" id="name" name="name" required class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all">
                    </div>
                    <div class="form-group">
                        <label for="email" class="block mb-2 font-medium">Email</label>
                        <input type="email" id="email" name="email" required class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all">
                    </div>
                    <div class="form-group">
                        <label for="message" class="block mb-2 font-medium">Message</label>
                        <textarea id="message" name="message" rows="5" required class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"></textarea>
                    </div>
                    <button type="submit" class="w-full btn btn-primary bg-primary text-white py-3 rounded-lg font-semibold hover:bg-secondary transition-colors">Send Message</button>
                </form>
            </div>
        </section>
    </main>

    <footer class="footer bg-gray-900 text-white py-8 text-center">
        <div class="container mx-auto px-6">
            <p>&copy; 2024 {name}. All rights reserved.</p>
        </div>
    </footer>

    <!-- Main JS -->
    <script src="scripts/main.js"></script>
</body>
</html>"""

        # CSS Content
        css = f"""/* NCD INAI Generated Styles */
:root {{
    --primary: {theme.get('primaryColor', '#3B82F6')};
    --secondary: {theme.get('secondaryColor', '#1E40AF')};
    --background: {theme.get('backgroundColor', '#FFFFFF')};
    --text: {theme.get('textColor', '#1F2937')};
    --accent: {theme.get('accentColor', '#10B981')};
    --font-family: '{theme.get('fontFamily', 'Inter')}', sans-serif;
}}

body {{
    font-family: var(--font-family);
}}

/* Custom styles complementing Tailwind */
.header.scrolled {{
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}}

@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(20px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.animate-fade-up {{
    animation: fadeInUp 0.8s ease-out forwards;
}}
"""

        # JS Content
        js = """document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('hidden');
            navLinks.classList.toggle('flex');
            navLinks.classList.toggle('flex-col');
            navLinks.classList.toggle('absolute');
            navLinks.classList.toggle('top-full');
            navLinks.classList.toggle('left-0');
            navLinks.classList.toggle('w-full');
            navLinks.classList.toggle('bg-white');
            navLinks.classList.toggle('p-6');
            navLinks.classList.toggle('shadow-lg');
            
            // Hamburger to X animation
            const spans = mobileMenuBtn.querySelectorAll('span');
            if (spans.length === 3) {
                 // Simple toggle implementation can be improved
            }
        });
    }

    // Header scroll effect
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 20) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }

    // Smooth scroll
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                // Close mobile menu if open
                if (navLinks && !navLinks.classList.contains('hidden')) {
                    mobileMenuBtn.click();
                }
            }
        });
    });

    // Contact form
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }
});"""

        return {
            "html": html,
            "css": css,
            "js": js
        }


# Singleton instance
code_generator = CodeGeneratorAgent()
