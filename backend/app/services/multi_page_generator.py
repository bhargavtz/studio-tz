"""
NCD INAI - Multi-Page Website Generator

Generates multiple HTML pages from blueprint.
"""

from typing import Dict, Any, List
from pathlib import Path
from bs4 import BeautifulSoup


class MultiPageGenerator:
    """Handles generation of multi-page websites using AI."""
    
    async def generate_pages(
        self,
        blueprint: Dict[str, Any],
        base_html: str,
        base_css: str,
        base_js: str
    ) -> Dict[str, str]:
        """Generate multiple HTML pages from blueprint using AI."""
        pages = blueprint.get("pages", [])
        
        if len(pages) <= 1:
            # Single page site
            return {"index.html": base_html}
        
        from app.agents.code_generator import code_generator
        generated_pages = {}
        
        for page in pages:
            page_slug = page.get("slug", "/")
            page_id = page.get("id", "home")
            
            # Determine filename
            if page_slug == "/" or page_slug == "index":
                filename = "index.html"
                # Use base_html for index, but update navigation
                page_html = await self._post_process_navigation(base_html, pages, page_slug)
            else:
                filename = f"{page_slug.strip('/').replace('/', '-')}.html"
                # Generate new page content using AI
                print(f"✨ Generating high-quality page: {filename}")
                page_html = await code_generator.generate_page(
                    blueprint=blueprint,
                    page_id=page_id,
                    base_css=base_css,
                    base_js=base_js
                )
                
                # If generation failed, fallback to a basic update
                if not page_html:
                    page_html = self._generate_fallback_page(page, base_html, pages, blueprint)
                else:
                    # Update navigation in the AI-generated HTML
                    page_html = await self._post_process_navigation(page_html, pages, page_slug)
            
            generated_pages[filename] = page_html
        
        return generated_pages

    async def _post_process_navigation(self, html: str, all_pages: List[Dict[str, Any]], current_slug: str) -> str:
        """Ensure navigation links are correct in AI-generated HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Match all internal links
        for a in soup.find_all('a', href=True):
            href = a['href']
            # Skip external, anchor, or root
            if href.startswith('http') or href.startswith('#'):
                continue
            
            # Find the corresponding page in blueprint
            target_slug = href.strip('/')
            if not target_slug or target_slug == "index":
                a['href'] = "index.html"
            else:
                # Add .html if missing
                if not target_slug.endswith('.html'):
                    a['href'] = f"{target_slug.replace('/', '-')}.html"
            
            # Mark active link
            if href == current_slug or (href == "/" and current_slug == "/"):
                classes = a.get('class', [])
                if isinstance(classes, str):
                    classes = [classes]
                if 'active' not in classes:
                    classes.append('active')
                a['class'] = classes
        
        return str(soup.prettify())

    def _generate_fallback_page(self, page, base_html, all_pages, blueprint):
        """Fallback to basic page generation if AI fails."""
        soup = BeautifulSoup(base_html, 'html.parser')
        main_tag = soup.find('main')
        if main_tag:
            main_tag.clear()
            # Simple content for fallback
            main_tag.append(BeautifulSoup(f"<section class='py-20'><div class='container mx-auto px-6'><h1>{page.get('title')}</h1><p>Content for {page.get('title')} coming soon.</p></div></section>", 'html.parser'))
        return str(soup.prettify())


# Singleton
multi_page_generator = MultiPageGenerator()
