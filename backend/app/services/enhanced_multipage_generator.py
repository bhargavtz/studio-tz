"""
NCD INAI - Enhanced Multi-Page Code Generator

Generates unique HTML for each page in a multi-page website.
"""

from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings


MULTI_PAGE_PROMPT = """You are an ELITE WEB DEVELOPER generating a multi-page website.

⚠️ CRITICAL RULE: The HEADER, NAVIGATION, and FOOTER must be ABSOLUTELY IDENTICAL on EVERY page!
Only the MAIN CONTENT inside <main> should be different per page.

Page to Generate: {page_title} ({page_slug})
Brand Name: {brand_name}
Theme: Primary={primary_color}, Font={font_family}, Style={style}

All Pages in Site: {all_pages}

## YOUR TASK:
Generate a COMPLETE, UNIQUE HTML page for "{page_title}" that:

1. **Has IDENTICAL header/nav/footer** (use EXACT same brand name: "{brand_name}")
2. **Has DIFFERENT main content** specific to this page type
3. **Links to shared files**: styles/main.css and scripts/main.js
4. **Matches the design theme** perfectly

## MANDATORY HEADER (MUST BE IDENTICAL ON ALL PAGES):

```html
<!-- HEADER - DO NOT CHANGE ACROSS PAGES -->
<nav class="fixed top-0 w-full bg-white/90 backdrop-blur-md z-50 shadow-sm">
    <div class="container mx-auto px-6 py-4 flex justify-between items-center">
        <a href="index.html" class="text-2xl font-bold" style="color: {primary_color}">{brand_name}</a>
        <button class="md:hidden mobile-menu-btn">☰</button>
        <ul class="hidden md:flex gap-8 nav-links">
            {nav_links}
        </ul>
    </div>
</nav>
```

## MANDATORY FOOTER (MUST BE IDENTICAL ON ALL PAGES):

```html
<!-- FOOTER - DO NOT CHANGE ACROSS PAGES -->
<footer class="bg-gray-900 text-white py-12">
    <div class="container mx-auto px-6 text-center">
        <p class="text-2xl font-bold mb-4" style="color: {primary_color}">{brand_name}</p>
        <p>© 2024 {brand_name}. All rights reserved.</p>
    </div>
</footer>
```

## CONTENT GUIDELINES BY PAGE TYPE (UNIQUE CONTENT ONLY):

**Home/Index Page**:
- Hero: Main value proposition with brand name
- Features: 3-6 key benefits/features
- Social proof: Stats, testimonials, or client logos
- CTA: Strong call-to-action

**About Page**:
- Hero: Company story headline
- Mission/Vision sections
- Team: 3-6 team member cards with photos
- Values or timeline
- NO repetition of home content!

**Services Page**:
- Hero: "Our Services" headline
- Service Cards: 4-6 detailed service blocks
- Each service: Icon, title, 3+ sentences, CTA
- Pricing/packages if relevant

**Contact Page**:
- Hero: "Get In Touch"
- Contact Form: name, email, subject, message
- Contact Info: phone, email, address (use placeholders)
- Map or office hours section

**Portfolio/Work**:
- Hero: "Our Work"
- Project Grid: 6-12 project cards
- Filters/categories
- Each project: image placeholder, title, description

## MANDATORY STRUCTURE:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - {brand_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles/main.css">
    <link href="https://fonts.googleapis.com/css2?family={font_family}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-['{font_family}']">
    <!-- NAVIGATION (USE EXACT HEADER TEMPLATE ABOVE) -->
    
    <!-- MAIN CONTENT (THIS IS THE ONLY PART THAT CHANGES) -->
    <main class="pt-20">
        <!-- YOUR UNIQUE PAGE-SPECIFIC SECTIONS HERE -->
    </main>

    <!-- FOOTER (USE EXACT FOOTER TEMPLATE ABOVE) -->
    
    <script src="scripts/main.js"></script>
</body>
</html>
```

## DESIGN REQUIREMENTS:
- Use Tailwind: `bg-gradient-to-r`, `hover:scale-105`, `transition-all`
- Glassmorphism: `backdrop-filter: blur(12px)`, `bg-white/10`
- Responsive: `grid-cols-1 md:grid-cols-2 lg:grid-cols-3`
- Animations: Smooth transitions on all interactive elements

⚠️ CRITICAL REMINDER:
- Brand name "{brand_name}" must be EXACTLY the same on all pages
- Header navigation must be EXACTLY the same on all pages
- Footer must be EXACTLY the same on all pages
- ONLY the <main> content should be unique per page!

OUTPUT: Return ONLY the complete HTML as a string. NO JSON. NO markdown.
"""


class EnhancedMultiPageGenerator:
    """Generates unique HTML for each page."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                temperature=0.7  # Higher creativity for unique content
            )
        return self._llm
    
    def _get_chain(self):
        if self._chain is None:
            prompt = ChatPromptTemplate.from_template(MULTI_PAGE_PROMPT)
            self._chain = prompt | self._get_llm()
        return self._chain
    
    async def generate_page(
        self,
        page: Dict[str, Any],
        all_pages: List[Dict[str, Any]],
        theme: Dict[str, Any],
        brand_name: str = "YourBrand"
    ) -> str:
        """Generate unique HTML for a specific page."""
        
        # Build navigation links
        nav_links_html = ""
        for p in all_pages:
            slug = p.get("slug", "/")
            title = p.get("title", "Page")
            
            if slug == "/" or slug == "index":
                filename = "index.html"
            else:
                filename = f"{slug.strip('/').replace('/', '-')}.html"
            
            # Mark current page as active
            is_current = (p.get("slug") == page.get("slug"))
            active_class = "text-primary font-semibold" if is_current else "hover:text-primary transition"
            
            nav_links_html += f'<li><a href="{filename}" class="{active_class}">{title}</a></li>\n'
        
        try:
            result = await self._get_chain().ainvoke({
                "page_title": page.get("title", "Page"),
                "page_slug": page.get("slug", "/"),
                "brand_name": brand_name,
                "all_pages": ", ".join([p.get("title", "") for p in all_pages]),
                "primary_color": theme.get("primaryColor", "#3B82F6"),
                "font_family": theme.get("fontFamily", "Inter"),
                "style": theme.get("style", "modern"),
                "nav_links": nav_links_html
            })
            
            return result.content
        except Exception as e:
            print(f"Error generating page {page.get('title')}: {e}")
            return self._fallback_page(page, all_pages, theme, brand_name)
    
    def _fallback_page(
        self,
        page: Dict[str, Any],
        all_pages: List[Dict[str, Any]],
        theme: Dict[str, Any],
        brand_name: str = "YourBrand"
    ) -> str:
        """Simple fallback page if AI fails."""
        title = page.get("title", "Page")
        primary = theme.get("primaryColor", "#3B82F6")
        font = theme.get("fontFamily", "Inter")
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - {brand_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles/main.css">
    <link href="https://fonts.googleapis.com/css2?family={font}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="font-['{font}'] bg-gray-50">
    <main class="min-h-screen flex items-center justify-center">
        <div class="text-center">
            <h1 class="text-4xl font-bold mb-4" style="color: {primary}">{brand_name}</h1>
            <h2 class="text-2xl mb-4">{title}</h2>
            <p class="text-gray-600">Content for this page is being generated...</p>
        </div>
    </main>
    <script src="scripts/main.js"></script>
</body>
</html>"""


# Singleton
enhanced_multi_page_generator = EnhancedMultiPageGenerator()
