"""
NCD INAI - Code Generator Agent

Generates HTML, CSS, and JavaScript from blueprints.
"""

from typing import Dict, Any
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings


CODE_GENERATOR_PROMPT = """You are an expert frontend developer.
Your task is to generate production-ready HTML, CSS, and JavaScript code from a website blueprint.

Blueprint:
{blueprint}

Generate clean, semantic, responsive code following these rules:

HTML:
- Use semantic HTML5 elements (header, nav, main, section, footer)
- Include proper meta tags for SEO
- Add meaningful class names for styling
- MUST link CSS exactly as: <link rel="stylesheet" href="styles/main.css">
- MUST link JS exactly as: <script src="scripts/main.js"></script>
- Use relative paths for images: src="assets/image.jpg" (NOT /assets/)
- Make it accessible (alt tags, aria labels where needed)

CSS:
- Use CSS custom properties for theme colors
- Mobile-first responsive design
- Smooth animations and transitions
- Modern layout with flexbox/grid
- Clean, organized structure with comments

JavaScript:
- Vanilla JavaScript only (no frameworks)
- Handle form submissions
- Add smooth scrolling
- Mobile menu toggle
- Any interactive features needed

Theme to apply:
- Primary: {primaryColor}
- Secondary: {secondaryColor}
- Background: {backgroundColor}
- Text: {textColor}
- Accent: {accentColor}
- Font: {fontFamily}
- Style: {style}

Generate code as a JSON object:
{{
    "html": "<!DOCTYPE html>...",
    "css": "/* styles */...",
    "js": "// scripts..."
}}

Requirements:
1. The website must look professional and polished
2. All sections from the blueprint must be included
3. Use real content from the blueprint (not lorem ipsum)
4. Make sure colors and fonts match the theme
5. Add subtle hover effects and transitions

Respond ONLY with valid JSON containing the complete code."""


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
                temperature=0.7
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
            result = await self._get_chain().ainvoke({
                "blueprint": self._format_blueprint(blueprint),
                "primaryColor": theme.get("primaryColor", "#3B82F6"),
                "secondaryColor": theme.get("secondaryColor", "#1E40AF"),
                "backgroundColor": theme.get("backgroundColor", "#FFFFFF"),
                "textColor": theme.get("textColor", "#1F2937"),
                "accentColor": theme.get("accentColor", "#10B981"),
                "fontFamily": theme.get("fontFamily", "Inter"),
                "style": theme.get("style", "modern")
            })
            
            # Post-process: Inject NCD attributes
            result = self._inject_ncd_attributes(result, blueprint)
            return result
        except Exception as e:
            print(f"Code generation error: {e}")
            fallback = self._generate_fallback_code(blueprint)
            return self._inject_ncd_attributes(fallback, blueprint)
    
    def _inject_ncd_attributes(self, code: Dict[str, str], blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Inject data-ncd-* attributes into HTML and create scoped CSS."""
        from bs4 import BeautifulSoup
        import uuid
        
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
        scoped_css = "\n\n/* NCD Scoped Styles */\n"
        for ncd_id in ncd_ids:
            scoped_css += f"[data-ncd-id=\"{ncd_id}\"] {{\n  /* Editable element */\n}}\n\n"
        
        code['css'] = css + scoped_css
        
        return code
    
    def _format_blueprint(self, blueprint: Dict[str, Any]) -> str:
        """Format blueprint for the prompt."""
        import json
        return json.dumps(blueprint, indent=2)
    
    def _generate_fallback_code(self, blueprint: Dict[str, Any]) -> Dict[str, str]:
        """Generate fallback code if AI fails."""
        name = blueprint.get("name", "My Website")
        theme = blueprint.get("theme", {})
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <link rel="stylesheet" href="styles/main.css">
    <link href="https://fonts.googleapis.com/css2?family={theme.get('fontFamily', 'Inter')}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <header class="header">
        <nav class="nav container">
            <a href="/" class="logo">{name}</a>
            <button class="mobile-menu-btn" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
            <ul class="nav-links">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#services">Services</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section id="home" class="hero">
            <div class="container">
                <h1>Welcome to {name}</h1>
                <p>Your trusted partner for excellence</p>
                <a href="#contact" class="btn btn-primary">Get Started</a>
            </div>
        </section>

        <section id="about" class="about">
            <div class="container">
                <h2>About Us</h2>
                <p>We are dedicated to providing the best service possible.</p>
            </div>
        </section>

        <section id="services" class="services">
            <div class="container">
                <h2>Our Services</h2>
                <div class="services-grid">
                    <div class="service-card">
                        <h3>Service One</h3>
                        <p>Description of our first service.</p>
                    </div>
                    <div class="service-card">
                        <h3>Service Two</h3>
                        <p>Description of our second service.</p>
                    </div>
                    <div class="service-card">
                        <h3>Service Three</h3>
                        <p>Description of our third service.</p>
                    </div>
                </div>
            </div>
        </section>

        <section id="contact" class="contact">
            <div class="container">
                <h2>Contact Us</h2>
                <form class="contact-form" id="contactForm">
                    <div class="form-group">
                        <label for="name">Name</label>
                        <input type="text" id="name" name="name" required>
                    </div>
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea id="message" name="message" rows="5" required></textarea>
                    </div>
                    <button type="submit" class="btn btn-primary">Send Message</button>
                </form>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2024 {name}. All rights reserved.</p>
        </div>
    </footer>

    <script src="scripts/main.js"></script>
</body>
</html>"""

        css = f"""/* NCD INAI Generated Styles */

:root {{
    --primary: {theme.get('primaryColor', '#3B82F6')};
    --secondary: {theme.get('secondaryColor', '#1E40AF')};
    --background: {theme.get('backgroundColor', '#FFFFFF')};
    --text: {theme.get('textColor', '#1F2937')};
    --accent: {theme.get('accentColor', '#10B981')};
    --font-family: '{theme.get('fontFamily', 'Inter')}', sans-serif;
}}

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    font-family: var(--font-family);
    background: var(--background);
    color: var(--text);
    line-height: 1.6;
}}

.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header */
.header {{
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: var(--background);
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    z-index: 1000;
}}

.nav {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 20px;
}}

.logo {{
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--primary);
    text-decoration: none;
}}

.nav-links {{
    display: flex;
    list-style: none;
    gap: 2rem;
}}

.nav-links a {{
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.3s ease;
}}

.nav-links a:hover {{
    color: var(--primary);
}}

.mobile-menu-btn {{
    display: none;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: none;
    cursor: pointer;
}}

.mobile-menu-btn span {{
    width: 25px;
    height: 3px;
    background: var(--text);
    transition: 0.3s;
}}

/* Hero Section */
.hero {{
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
    color: white;
    padding-top: 80px;
}}

.hero h1 {{
    font-size: 3.5rem;
    margin-bottom: 1rem;
    animation: fadeInUp 0.8s ease;
}}

.hero p {{
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}}

/* Buttons */
.btn {{
    display: inline-block;
    padding: 0.875rem 2rem;
    border-radius: 8px;
    font-weight: 600;
    text-decoration: none;
    transition: all 0.3s ease;
    cursor: pointer;
    border: none;
    font-size: 1rem;
}}

.btn-primary {{
    background: white;
    color: var(--primary);
}}

.btn-primary:hover {{
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}}

/* Sections */
section {{
    padding: 5rem 0;
}}

section h2 {{
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 3rem;
    color: var(--text);
}}

/* About */
.about {{
    background: #f8fafc;
}}

.about p {{
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
    font-size: 1.125rem;
}}

/* Services */
.services-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}}

.service-card {{
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: transform 0.3s ease;
}}

.service-card:hover {{
    transform: translateY(-5px);
}}

.service-card h3 {{
    color: var(--primary);
    margin-bottom: 1rem;
}}

/* Contact */
.contact {{
    background: #f8fafc;
}}

.contact-form {{
    max-width: 600px;
    margin: 0 auto;
    background: white;
    padding: 2rem;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}}

.form-group {{
    margin-bottom: 1.5rem;
}}

.form-group label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}}

.form-group input,
.form-group textarea {{
    width: 100%;
    padding: 0.875rem;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.3s ease;
}}

.form-group input:focus,
.form-group textarea:focus {{
    outline: none;
    border-color: var(--primary);
}}

/* Footer */
.footer {{
    background: var(--text);
    color: white;
    padding: 2rem 0;
    text-align: center;
}}

/* Animations */
@keyframes fadeInUp {{
    from {{
        opacity: 0;
        transform: translateY(30px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

/* Mobile Responsive */
@media (max-width: 768px) {{
    .mobile-menu-btn {{
        display: flex;
    }}
    
    .nav-links {{
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--background);
        flex-direction: column;
        padding: 1rem;
        gap: 1rem;
        display: none;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }}
    
    .nav-links.active {{
        display: flex;
    }}
    
    .hero h1 {{
        font-size: 2.5rem;
    }}
    
    section {{
        padding: 3rem 0;
    }}
}}"""

        js = """// NCD INAI Generated Scripts

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', function() {
            navLinks.classList.toggle('active');
        });
    }
    
    // Close mobile menu when clicking a link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks.classList.remove('active');
        });
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Contact form handling
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }
    
    // Header scroll effect
    const header = document.querySelector('.header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 100) {
                header.style.background = 'rgba(255, 255, 255, 0.95)';
                header.style.backdropFilter = 'blur(10px)';
            } else {
                header.style.background = 'var(--background)';
                header.style.backdropFilter = 'none';
            }
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
