import re
from urllib.parse import urlparse

def is_valid_wikipedia_url(url: str) -> bool:
    """
    Validates if the provided URL is a valid English Wikipedia article URL.
    
    Args:
        url (str): The URL to validate.
        
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False
            
        # Pattern for en.wikipedia.org/wiki/Article_Title
        # Also accepts wikipedia.org/wiki/Article_Title (redirects usually)
        # Limiting to 'en' subdomain for Phase 1 as per spec
        domain_pattern = r'^(en\.)?wikipedia\.org$'
        if not re.match(domain_pattern, parsed.netloc):
            return False
            
        if not parsed.path.startswith('/wiki/'):
            return False
            
        # Check if article title exists
        if len(parsed.path) <= 6:  # /wiki/ is 6 chars
            return False
            
        return True
    except Exception:
        return False

def extract_title_from_url(url: str) -> str:
    """
    Extracts the article title from a Wikipedia URL.
    
    Args:
        url (str): The Wikipedia URL.
        
    Returns:
        str: The article title (URL decoded).
    """
    parsed = urlparse(url)
    # /wiki/Title -> Title
    path_parts = parsed.path.split('/')
    if len(path_parts) >= 3 and path_parts[1] == 'wiki':
        return path_parts[2].replace('_', ' ')
    return ""
