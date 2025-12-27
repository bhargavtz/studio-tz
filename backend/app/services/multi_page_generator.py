"""
NCD INAI - Multi-Page Website Generator

Generates multiple HTML pages from blueprint.
"""

from typing import Dict, Any, List
from pathlib import Path
from bs4 import BeautifulSoup


class MultiPageGenerator:
    """Handles generation of multi-page websites."""
    
    def generate_pages(
        self,
        blueprint: Dict[str, Any],
        base_html: str,
        base_css: str,
        base_js: str
    ) -> Dict[str, str]:
        """Generate multiple HTML pages from blueprint."""
        pages = blueprint.get("pages", [])
        
        if len(pages) <= 1:
            # Single page site
            return {"index.html": base_html}
        
        generated_pages = {}
        
        for page in pages:
            page_slug = page.get("slug", "/")
            page_title = page.get("title", "Page")
            
            # Determine filename
            if page_slug == "/" or page_slug == "index":
                filename = "index.html"
            else:
                filename = f"{page_slug.strip('/').replace('/', '-')}.html"
            
            # Generate page HTML
            page_html = self._generate_page_html(
                page=page,
                base_html=base_html,
                all_pages=pages,
                blueprint=blueprint
            )
            
            generated_pages[filename] = page_html
        
        return generated_pages
    
    def _generate_page_html(
        self,
        page: Dict[str, Any],
        base_html: str,
        all_pages: List[Dict[str, Any]],
        blueprint: Dict[str, Any]
    ) -> str:
        """Generate HTML for a specific page."""
        soup = BeautifulSoup(base_html, 'html.parser')
        
        # CRITICAL: Ensure Tailwind CDN is present
        import re
        head = soup.find('head')
        if head:
            tailwind_script = soup.find('script', src=re.compile(r'cdn\.tailwindcss\.com'))
            if not tailwind_script:
                # Add Tailwind CDN
                new_tailwind = soup.new_tag('script', src='https://cdn.tailwindcss.com')
                # Insert after last meta tag
                last_meta = head.find_all('meta')
                if last_meta:
                    last_meta[-1].insert_after(new_tailwind)
                else:
                    head.insert(0, new_tailwind)
        
        # Update title
        title_tag = soup.find('title')
        if title_tag:
            title_tag.string = page.get("meta", {}).get("title", page.get("title", "Page"))
        
        # Update meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            meta_desc['content'] = page.get("meta", {}).get("description", "")
        
        # Update navigation links
        self._update_navigation(soup, all_pages, page.get("slug", "/"))
        
        # Generate page content intelligently
        main_tag = soup.find('main')
        if main_tag:
            # Extract sections from page blueprint
            page_sections = page.get("sections", [])
            
            if page_sections:
                # Blueprint has specific sections for this page - use them
                main_tag.clear()
                for section in page_sections:
                    section_html = self._generate_section(section)
                    main_tag.append(BeautifulSoup(section_html, 'html.parser'))
            else:
                # No blueprint sections - intelligently extract from base HTML
                self._extract_relevant_content_for_page(soup, main_tag, page, blueprint)
        
        return str(soup.prettify())
    
    def _update_navigation(
        self,
        soup: BeautifulSoup,
        all_pages: List[Dict[str, Any]],
        current_slug: str
    ):
        """Update navigation links."""
        nav = soup.find('nav')
        if not nav:
            return
        
        # Find nav links container
        nav_links = nav.find('ul', class_='nav-links')
        if nav_links:
            nav_links.clear()
            
            for page in all_pages:
                slug = page.get("slug", "/")
                title = page.get("title", "Page")
                
                # Determine href
                if slug == "/":
                    href = "index.html"
                else:
                    href = f"{slug.strip('/').replace('/', '-')}.html"
                
                # Create link
                li = soup.new_tag('li')
                a = soup.new_tag('a', href=href)
                a.string = title
                
                # Mark active
                if slug == current_slug:
                    a['class'] = a.get('class', []) + ['active']
                
                li.append(a)
                nav_links.append(li)
    
    def _extract_relevant_content_for_page(
        self,
        soup: BeautifulSoup,
        main_tag: Any,
        page: Dict[str, Any],
        blueprint: Dict[str, Any]
    ):
        """Intelligently extract and keep only relevant content for this page type."""
        page_slug = page.get("slug", "/").strip("/").lower()
        page_title = page.get("title", "").lower()
        
        # Map page types to relevant section IDs/classes
        page_type_mapping = {
            "about": ["about", "team", "history", "mission", "legacy", "story"],
            "services": ["services", "features", "offerings", "what-we-do", "expertise"],
            "contact": ["contact", "get-in-touch", "reach-us", "contact-form"],
            "portfolio": ["portfolio", "work", "projects", "gallery", "showcase"],
            "products": ["products", "shop", "store", "catalog"],
            "blog": ["blog", "articles", "news", "posts"],
            "pricing": ["pricing", "plans", "packages"],
        }
        
        # Determine page type
        page_type = None
        for ptype, keywords in page_type_mapping.items():
            if any(keyword in page_slug or keyword in page_title for keyword in keywords):
                page_type = ptype
                break
        
        # If it's index/home, keep all sections
        if page_slug in ["", "index", "home"]:
            return  # Keep everything
        
        # If we identified a page type, filter sections
        if page_type and page_type in page_type_mapping:
            relevant_keywords = page_type_mapping[page_type]
            
            # Find all sections in main
            sections = main_tag.find_all('section', recursive=False)
            
            for section in sections:
                section_id = section.get('id', '').lower()
                section_class = ' '.join(section.get('class', [])).lower()
                
                # Check if this section is relevant to the page type
                is_relevant = any(
                    keyword in section_id or keyword in section_class
                    for keyword in relevant_keywords
                )
                
                # Keep hero section always, remove irrelevant ones
                if section_id != 'hero' and not is_relevant:
                    section.decompose()
        else:
            # Unknown page type - keep first 2 sections (usually hero + main content)
            sections = main_tag.find_all('section', recursive=False)
            for i, section in enumerate(sections):
                if i > 1:  # Keep only first 2 sections
                    section.decompose()
    
    def _generate_section(self, section: Dict[str, Any]) -> str:
        """Generate HTML for a section."""
        section_type = section.get("type", "content")
        section_id = section.get("id", "")
        section_title = section.get("title", "")
        
        html = f'<section id="{section_id}" class="{section_type}">\n'
        html += '  <div class="container">\n'
        
        if section_title:
            html += f'    <h2>{section_title}</h2>\n'
        
        # Add components
        for component in section.get("components", []):
            html += self._generate_component(component)
        
        html += '  </div>\n'
        html += '</section>\n'
        
        return html
    
    def _generate_component(self, component: Dict[str, Any]) -> str:
        """Generate HTML for a component."""
        comp_type = component.get("type", "paragraph")
        comp_id = component.get("id", "")
        content = component.get("content", "")
        properties = component.get("properties", {})
        
        if comp_type == "heading":
            level = properties.get("level", "h2")
            return f'    <{level} data-ncd-id="{comp_id}" data-ncd-type="text">{content}</{level}>\n'
        
        elif comp_type == "paragraph":
            return f'    <p data-ncd-id="{comp_id}" data-ncd-type="text">{content}</p>\n'
        
        elif comp_type == "button":
            variant = properties.get("variant", "primary")
            return f'    <a href="#" class="btn btn-{variant}" data-ncd-id="{comp_id}" data-ncd-type="button">{content}</a>\n'
        
        elif comp_type == "image":
            src = properties.get("src", "assets/placeholder.jpg")
            alt = properties.get("alt", content)
            return f'    <img src="{src}" alt="{alt}" data-ncd-id="{comp_id}" data-ncd-type="image">\n'
        
        else:
            return f'    <div data-ncd-id="{comp_id}" data-ncd-type="element">{content}</div>\n'


# Singleton
multi_page_generator = MultiPageGenerator()
