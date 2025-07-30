import httpx
import json
import time
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CBUAEWebScraper:
    """
    Web scraper for CBUAE Rulebook website with robust error handling and caching.
    """
    
    def __init__(self, base_url: str = "https://rulebook.centralbank.ae", cache_duration: int = 3600):
        self.base_url = base_url
        self.cache_duration = cache_duration
        self.cache = {}
        self.session = httpx.Client(
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            },
            timeout=30.0,
            follow_redirects=True
        )
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return f"url:{url}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return time.time() - cached_time < self.cache_duration
    
    def _fetch_page(self, url: str) -> Optional[str]:
        """
        Fetch a webpage with error handling and caching.
        """
        cache_key = self._get_cache_key(url)
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            logger.info(f"Using cached data for {url}")
            return self.cache[cache_key]['content']
        
        try:
            logger.info(f"Fetching {url}")
            response = self.session.get(url)
            
            if response.status_code == 200:
                content = response.text
                # Cache the content
                self.cache[cache_key] = {
                    'content': content,
                    'timestamp': time.time()
                }
                return content
            elif response.status_code == 403:
                logger.warning(f"Access denied (403) for {url}")
                return None
            else:
                logger.error(f"Failed to fetch {url}: HTTP {response.status_code}")
                return None
                
        except httpx.RequestError as e:
            logger.error(f"Request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching {url}: {e}")
            return None
    
    def search_policies(self, query: str) -> List[Dict]:
        """
        Search for policies on the CBUAE website.
        Since direct access is restricted, this provides a framework for when access is available.
        """
        results = []
        
        # Try different search approaches
        search_urls = [
            f"{self.base_url}/search?q={query}",
            f"{self.base_url}/en/search?query={query}",
            f"{self.base_url}/regulations?search={query}"
        ]
        
        for search_url in search_urls:
            content = self._fetch_page(search_url)
            if content:
                results.extend(self._parse_search_results(content, query))
                break
        
        return results
    
    def _parse_search_results(self, html_content: str, query: str) -> List[Dict]:
        """Parse search results from HTML content."""
        results = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for common search result patterns
            search_containers = soup.find_all(['div', 'li', 'article'], class_=lambda x: x and any(
                term in x.lower() for term in ['result', 'policy', 'regulation', 'document']
            ))
            
            for container in search_containers:
                title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'a'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href') if title_elem.name == 'a' else None
                    
                    if link and not link.startswith('http'):
                        link = f"{self.base_url}{link}"
                    
                    # Extract description/summary
                    desc_elem = container.find(['p', 'div'], class_=lambda x: x and 'summary' in x.lower())
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if title and len(title) > 10:  # Filter out very short titles
                        results.append({
                            'title': title,
                            'url': link,
                            'description': description,
                            'source': 'CBUAE Website'
                        })
            
        except Exception as e:
            logger.error(f"Error parsing search results: {e}")
        
        return results
    
    def get_policy_content(self, policy_url: str) -> Optional[Dict]:
        """
        Fetch full content of a specific policy document.
        """
        content = self._fetch_page(policy_url)
        if not content:
            return None
        
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract policy content
            policy_data = {
                'url': policy_url,
                'title': '',
                'content': '',
                'sections': [],
                'metadata': {}
            }
            
            # Extract title
            title_elem = soup.find(['h1', 'h2'], class_=lambda x: x and 'title' in x.lower())
            if not title_elem:
                title_elem = soup.find(['h1', 'h2'])
            
            if title_elem:
                policy_data['title'] = title_elem.get_text(strip=True)
            
            # Extract main content
            content_elem = soup.find(['div', 'article', 'main'], class_=lambda x: x and any(
                term in x.lower() for term in ['content', 'policy', 'regulation', 'document']
            ))
            
            if content_elem:
                # Remove navigation and footer elements
                for elem in content_elem.find_all(['nav', 'footer', 'aside']):
                    elem.decompose()
                
                policy_data['content'] = content_elem.get_text(strip=True)
                
                # Extract sections
                sections = content_elem.find_all(['h2', 'h3', 'h4'])
                for section in sections:
                    section_title = section.get_text(strip=True)
                    section_content = ""
                    
                    # Get content until next section
                    for sibling in section.next_siblings:
                        if hasattr(sibling, 'name') and sibling.name in ['h2', 'h3', 'h4']:
                            break
                        if hasattr(sibling, 'get_text'):
                            section_content += sibling.get_text(strip=True) + " "
                    
                    if section_title and section_content.strip():
                        policy_data['sections'].append({
                            'title': section_title,
                            'content': section_content.strip()
                        })
            
            return policy_data
            
        except Exception as e:
            logger.error(f"Error parsing policy content: {e}")
            return None
    
    def get_policy_categories(self) -> List[Dict]:
        """
        Get available policy categories from the website.
        """
        categories = []
        
        # Try different category pages
        category_urls = [
            f"{self.base_url}/categories",
            f"{self.base_url}/regulations",
            f"{self.base_url}/policies",
            f"{self.base_url}/en/regulations"
        ]
        
        for url in category_urls:
            content = self._fetch_page(url)
            if content:
                categories.extend(self._parse_categories(content))
                break
        
        return categories
    
    def _parse_categories(self, html_content: str) -> List[Dict]:
        """Parse policy categories from HTML content."""
        categories = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for navigation links or category listings
            category_links = soup.find_all('a', href=True)
            
            for link in category_links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # Filter for policy-related links
                if text and len(text) > 3 and any(
                    term in text.lower() for term in ['policy', 'regulation', 'standard', 'rule', 'guideline']
                ):
                    if not href.startswith('http'):
                        href = f"{self.base_url}{href}"
                    
                    categories.append({
                        'name': text,
                        'url': href
                    })
        
        except Exception as e:
            logger.error(f"Error parsing categories: {e}")
        
        return categories
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()