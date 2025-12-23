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
        
        # Generate page content
        main_tag = soup.find('main')
        if main_tag:
            main_tag.clear()
            
            # Add sections for this page
            for section in page.get("sections", []):
                section_html = self._generate_section(section)
                main_tag.append(BeautifulSoup(section_html, 'html.parser'))
        
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
            src = properties.get("src", "/assets/placeholder.jpg")
            alt = properties.get("alt", content)
            return f'    <img src="{src}" alt="{alt}" data-ncd-id="{comp_id}" data-ncd-type="image">\n'
        
        else:
            return f'    <div data-ncd-id="{comp_id}" data-ncd-type="element">{content}</div>\n'


# Singleton
multi_page_generator = MultiPageGenerator()
