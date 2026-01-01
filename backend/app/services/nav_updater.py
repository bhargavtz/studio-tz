"""
NCD INAI - Navigation Updater Service

Updates navigation links across all HTML pages in a session.
"""

import logging
from typing import List, Dict, Any
from pathlib import Path
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class NavigationUpdater:
    """Service to update navigation links across all pages."""
    
    def update_all_pages(
        self,
        session_dir: Path,
        new_page: Dict[str, str]
    ) -> int:
        """
        Update navigation in all HTML files to include new page link.
        
        Args:
            session_dir: Path to session directory
            new_page: Dict with keys 'filename', 'nav_link_text'
        
        Returns:
            Number of files updated
        """
        html_files = list(session_dir.glob("*.html"))
        updated_count = 0
        
        for html_file in html_files:
            try:
                # Skip the newly created page itself
                if html_file.name == new_page['filename']:
                    continue
                
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find navigation element
                nav = self._find_nav_element(soup)
                
                if nav:
                    # Check if link already exists
                    if not self._link_exists(nav, new_page['filename']):
                        # Add new link
                        self._add_nav_link(soup, nav, new_page)
                        
                        # Save updated file
                        with open(html_file, 'w', encoding='utf-8') as f:
                            f.write(str(soup.prettify()))
                        
                        updated_count += 1
            
            except Exception as e:
                logger.warning(f"Error updating {html_file.name}: {e}")
                continue
        
        return updated_count
    
    def _find_nav_element(self, soup: BeautifulSoup) -> Any:
        """Find the main navigation element in the page."""
        # Try common navigation patterns
        patterns = [
            soup.find('ul', class_='nav-links'),
            soup.find('ul', id='nav-links'),
            soup.find('div', id='nav-links'),
            soup.find('nav').find('ul') if soup.find('nav') else None,
            soup.find('div', class_=re.compile(r'nav-links|navigation|menu')),
        ]
        
        for pattern in patterns:
            if pattern:
                return pattern
        
        return None
    
    def _link_exists(self, nav: Any, filename: str) -> bool:
        """Check if a link to this page already exists."""
        links = nav.find_all('a')
        
        for link in links:
            href = link.get('href', '')
            if filename in href:
                return True
        
        return False
    
    def _add_nav_link(
        self,
        soup: BeautifulSoup,
        nav: Any,
        new_page: Dict[str, str]
    ):
        """Add a new navigation link to the nav element."""
        # Get existing links to match style
        existing_links = nav.find_all('a')
        
        if existing_links:
            # Clone style from first link
            first_link = existing_links[0]
            link_classes = first_link.get('class', [])
            
            # Create new link
            new_link = soup.new_tag('a', href=new_page['filename'])
            new_link['class'] = link_classes
            new_link.string = new_page['nav_link_text']
            
            # Add data attributes if present
            if first_link.get('data-ncd-file'):
                new_link['data-ncd-file'] = 'index.html'
                new_link['data-ncd-type'] = 'link'
                # Generate unique ID
                import random
                new_link['data-ncd-id'] = f"ncd-{random.randint(1000, 9999):04d}"
        else:
            # No existing links - create basic link
            new_link = soup.new_tag('a', href=new_page['filename'])
            new_link.string = new_page['nav_link_text']
        
        # Wrap in <li> if nav is a <ul>
        if nav.name == 'ul':
            li = soup.new_tag('li')
            li.append(new_link)
            nav.append(li)
        else:
            nav.append(new_link)
    
    def remove_page_link(
        self,
        session_dir: Path,
        filename: str
    ) -> int:
        """Remove a page link from all navigations."""
        html_files = list(session_dir.glob("*.html"))
        updated_count = 0
        
        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find all links to this file
                links = soup.find_all('a', href=filename)
                
                if links:
                    for link in links:
                        # Remove the link (and parent <li> if exists)
                        parent = link.parent
                        if parent and parent.name == 'li':
                            parent.decompose()
                        else:
                            link.decompose()
                    
                    # Save updated file
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(str(soup.prettify()))
                    
                    updated_count += 1
            
            except Exception as e:
                logger.warning(f"Error removing link from {html_file.name}: {e}")
                continue
        
        return updated_count


# Singleton instance
nav_updater = NavigationUpdater()
