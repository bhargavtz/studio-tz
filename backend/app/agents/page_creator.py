"""
NCD INAI - Page Creator Agent

Dynamically creates new website pages based on user chat requests.
"""

from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.config import settings


PAGE_CREATOR_PROMPT = """You are a PROFESSIONAL WEB PAGE GENERATOR.

User Request: {user_request}

Existing Website Theme:
- Primary Color: {primary_color}
- Background: {background_color}
- Text Color: {text_color}
- Font: {font_family}
- Style: {style}

Your task is to create a COMPLETE, PRODUCTION-READY HTML page that:

1. **Matches Existing Design**: Use the same colors, fonts, and style
2. **Includes Tailwind CDN**: Must have `<script src="https://cdn.tailwindcss.com"></script>`
3. **Links CSS**: Must have `<link rel="stylesheet" href="styles/main.css">`
4. **Has Navigation**: Copy this nav structure and add it to your page
5. **Relevant Content**: Generate appropriate content for the page type
6. **Professional Quality**: High-quality, realistic content

**CRITICAL REQUIREMENTS:**
- Use Tailwind CSS classes matching the theme colors
- Include proper meta tags
- Semantic HTML5 (`<section>`, `<article>`, `<nav>`)
- Mobile responsive design
- Proper forms if it's a contact/form page
- Hero section for visual appeal

**Output JSON Format:**
{{
    "filename": "contact.html",
    "page_title": "Contact Us",
    "nav_link_text": "Contact",
    "html_content": "<!DOCTYPE html>\\n<html lang=\\"en\\">\\n<head>...</head>\\n<body>...</body>\\n</html>"
}}

**Page Type Guidelines:**

**Contact Page**: Include
- Hero with "Get In Touch" heading
- Contact form (name, email, message fields)
- Contact info (address, phone, email placeholders)
- Map placeholder or office hours

**Pricing Page**: Include
- Hero with "Pricing Plans" heading
- 3 pricing tiers (Basic, Pro, Enterprise)
- Feature comparison
- CTA buttons

**About Page**: Include
- Hero with company story
- Mission/Vision
- Team section (placeholder profiles)
- Values or timeline

**FAQ Page**: Include
- Hero with "Frequently Asked Questions"
- Accordion-style Q&A (minimum 6 questions)
- Search bar placeholder
- Contact link

**Gallery/Portfolio**: Include
- Hero with "Our Work"
- Grid of placeholder images (6-12 items)
- Filter/category tabs
- Lightbox-ready structure

Respond ONLY with valid JSON. NO markdown blocks.
"""


class PageCreatorAgent:
    """Agent that creates new website pages from user requests."""
    
    def __init__(self):
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        if self._llm is None:
            self._llm = ChatGroq(
                api_key=settings.groq_api_key,
                model_name=settings.llm_model,
                temperature=0.6
            )
        return self._llm
    
    def _get_chain(self):
        if self._chain is None:
            prompt = ChatPromptTemplate.from_template(PAGE_CREATOR_PROMPT)
            parser = JsonOutputParser()
            self._chain = prompt | self._get_llm() | parser
        return self._chain
    
    async def create_page(
        self,
        user_request: str,
        theme: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create a new page based on user request and existing theme."""
        try:
            result = await self._get_chain().ainvoke({
                "user_request": user_request,
                "primary_color": theme.get("primaryColor", "#3B82F6"),
                "background_color": theme.get("backgroundColor", "#FFFFFF"),
                "text_color": theme.get("textColor", "#1F2937"),
                "font_family": theme.get("fontFamily", "Inter"),
                "style": theme.get("style", "modern")
            })
            
            return result
        except Exception as e:
            print(f"Page creation error: {e}")
            # Fallback: create basic page
            return self._create_fallback_page(user_request, theme)
    
    def _create_fallback_page(
        self,
        user_request: str,
        theme: Dict[str, Any]
    ) -> Dict[str, str]:
        """Create a basic fallback page if AI fails."""
        # Determine page type from request
        request_lower = user_request.lower()
        
        if "contact" in request_lower or "form" in request_lower:
            return self._create_contact_page(theme)
        elif "pricing" in request_lower or "price" in request_lower:
            return self._create_pricing_page(theme)
        elif "about" in request_lower:
            return self._create_about_page(theme)
        else:
            return self._create_generic_page(user_request, theme)
    
    def _create_contact_page(self, theme: Dict[str, Any]) -> Dict[str, str]:
        """Create a simple contact form page."""
        primary = theme.get("primaryColor", "#3B82F6")
        font = theme.get("fontFamily", "Inter")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles/main.css">
    <link href="https://fonts.googleapis.com/css2?family={font}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 font-['{font}']">
    <section class="min-h-screen flex items-center justify-center py-20">
        <div class="max-w-2xl mx-auto px-6 w-full">
            <h1 class="text-4xl font-bold text-center mb-4" style="color: {primary}">Get In Touch</h1>
            <p class="text-center text-gray-600 mb-12">We'd love to hear from you. Send us a message!</p>
            
            <form class="bg-white rounded-2xl shadow-lg p-8 space-y-6">
                <div>
                    <label class="block text-sm font-medium mb-2">Name</label>
                    <input type="text" required class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Email</label>
                    <input type="email" required class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">Message</label>
                    <textarea rows="5" required class="w-full px-4 py-3 rounded-lg border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none"></textarea>
                </div>
                <button type="submit" class="w-full py-3 rounded-lg text-white font-semibold hover:opacity-90 transition" style="background-color: {primary}">Send Message</button>
            </form>
        </div>
    </section>
    <script src="scripts/main.js"></script>
</body>
</html>"""
        
        return {
            "filename": "contact.html",
            "page_title": "Contact Us",
            "nav_link_text": "Contact",
            "html_content": html
        }
    
    def _create_pricing_page(self, theme: Dict[str, Any]) -> Dict[str, str]:
        """Create a simple pricing page."""
        primary = theme.get("primaryColor", "#3B82F6")
        font = theme.get("fontFamily", "Inter")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pricing</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles/main.css">
    <link href="https://fonts.googleapis.com/css2?family={font}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 font-['{font}']">
    <section class="py-20">
        <div class="max-w-6xl mx-auto px-6">
            <h1 class="text-4xl font-bold text-center mb-4" style="color: {primary}">Pricing Plans</h1>
            <p class="text-center text-gray-600 mb-16">Choose the perfect plan for your needs</p>
            
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white rounded-2xl shadow-lg p-8">
                    <h3 class="text-2xl font-bold mb-4">Basic</h3>
                    <div class="text-4xl font-bold mb-6" style="color: {primary}">$29<span class="text-lg text-gray-600">/mo</span></div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center gap-2">✓ Feature 1</li>
                        <li class="flex items-center gap-2">✓ Feature 2</li>
                        <li class="flex items-center gap-2">✓ Feature 3</li>
                    </ul>
                    <button class="w-full py-3 rounded-lg border-2 font-semibold hover:opacity-80 transition" style="border-color: {primary}; color: {primary}">Get Started</button>
                </div>
                
                <div class="bg-white rounded-2xl shadow-xl p-8 scale-105">
                    <div class="text-sm font-semibold text-center mb-2" style="color: {primary}">POPULAR</div>
                    <h3 class="text-2xl font-bold mb-4">Pro</h3>
                    <div class="text-4xl font-bold mb-6" style="color: {primary}">$79<span class="text-lg text-gray-600">/mo</span></div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center gap-2">✓ All Basic features</li>
                        <li class="flex items-center gap-2">✓ Advanced Feature 1</li>
                        <li class="flex items-center gap-2">✓ Advanced Feature 2</li>
                        <li class="flex items-center gap-2">✓ Priority Support</li>
                    </ul>
                    <button class="w-full py-3 rounded-lg text-white font-semibold hover:opacity-90 transition" style="background-color: {primary}">Get Started</button>
                </div>
                
                <div class="bg-white rounded-2xl shadow-lg p-8">
                    <h3 class="text-2xl font-bold mb-4">Enterprise</h3>
                    <div class="text-4xl font-bold mb-6" style="color: {primary}">$199<span class="text-lg text-gray-600">/mo</span></div>
                    <ul class="space-y-3 mb-8">
                        <li class="flex items-center gap-2">✓ All Pro features</li>
                        <li class="flex items-center gap-2">✓ Custom Integration</li>
                        <li class="flex items-center gap-2">✓ Dedicated Support</li>
                        <li class="flex items-center gap-2">✓ SLA Guarantee</li>
                    </ul>
                    <button class="w-full py-3 rounded-lg border-2 font-semibold hover:opacity-80 transition" style="border-color: {primary}; color: {primary}">Contact Sales</button>
                </div>
            </div>
        </div>
    </section>
    <script src="scripts/main.js"></script>
</body>
</html>"""
        
        return {
            "filename": "pricing.html",
            "page_title": "Pricing",
            "nav_link_text": "Pricing",
            "html_content": html
        }
    
    def _create_about_page(self, theme: Dict[str, Any]) -> Dict[str, str]:
        """Create a simple about page."""
        primary = theme.get("primaryColor", "#3B82F6")
        font = theme.get("fontFamily", "Inter")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>About Us</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="styles/main.css">
    <link href="https://fonts.googleapis.com/css2?family={font}:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-gray-50 font-['{font}']">
    <section class="py-20">
        <div class="max-w-4xl mx-auto px-6">
            <h1 class="text-4xl font-bold text-center mb-8" style="color: {primary}">About Us</h1>
            <div class="prose prose-lg max-w-none">
                <p class="text-gray-700 mb-6">We are dedicated to providing exceptional service and innovative solutions to our clients.</p>
                <p class="text-gray-700 mb-6">With years of experience and a passionate team, we've helped countless businesses achieve their goals.</p>
                
                <h2 class="text-2xl font-bold mb-4 mt-12" style="color: {primary}">Our Mission</h2>
                <p class="text-gray-700 mb-6">To deliver outstanding value and exceed expectations through quality, innovation, and customer focus.</p>
                
                <h2 class="text-2xl font-bold mb-4 mt-12" style="color: {primary}">Our Values</h2>
                <ul class="space-y-3 text-gray-700">
                    <li><strong>Excellence:</strong> We strive for the highest quality in everything we do</li>
                    <li><strong>Innovation:</strong> We embrace new ideas and technologies</li>
                    <li><strong>Integrity:</strong> We operate with transparency and honesty</li>
                    <li><strong>  Customer Focus:</strong> Your success is our success</li>
                </ul>
            </div>
        </div>
    </section>
    <script src="scripts/main.js"></script>
</body>
</html>"""
        
        return {
            "filename": "about.html",
            "page_title": "About Us",
            "nav_link_text": "About",
            "html_content": html
        }
    
    def _create_generic_page(self, request: str, theme: Dict[str, Any]) -> Dict[str, str]:
        """Create a generic page."""
        return self._create_about_page(theme)


# Singleton instance
page_creator = PageCreatorAgent()
