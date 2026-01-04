import wikipediaapi
from typing import Tuple
from utils.validation import is_valid_wikipedia_url, extract_title_from_url

class WikipediaFetcher:
    def __init__(self):
        # User-Agent is required by Wikipedia API
        self.wiki = wikipediaapi.Wikipedia(
            user_agent='WikipediaRAGSystem/1.0 (riku-miura@example.com)',
            language='en',
            extract_format=wikipediaapi.ExtractFormat.WIKI
        )

    def fetch_article(self, url: str) -> Tuple[str, str]:
        """
        Fetches article content from Wikipedia.
        
        Args:
            url (str): Wikipedia URL
            
        Returns:
            Tuple[str, str]: (title, content)
            
        Raises:
            ValueError: If URL is invalid
            Exception: If fetching fails or page does not exist
        """
        if not is_valid_wikipedia_url(url):
            raise ValueError("Invalid Wikipedia URL")
            
        title = extract_title_from_url(url)
        page = self.wiki.page(title)
        
        if not page.exists():
            raise Exception(f"Page '{title}' does not exist on English Wikipedia")
            
        return page.title, page.text
