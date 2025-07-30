#!/usr/bin/env python3
"""
🔗 LinkTune Content Extractor
Universal content extraction from any web source

Simplified and cleaned version of the G.Music Assembly extractor system.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class ExtractedContent:
    """Container for extracted content"""
    title: str
    content: str
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    platform: str = "unknown"
    url: str = ""

class ContentExtractor:
    """
    🔗 Universal content extractor for LinkTune
    
    Extracts meaningful content from any web URL for music generation.
    Supports ChatGPT shares, blogs, articles, and generic web content.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        
        # User agent to avoid blocking
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Platform detectors
        self.platform_patterns = {
            'chatgpt': [r'chatgpt\.com', r'chat\.openai\.com'],
            'claude': [r'claude\.ai'],
            'simplenote': [r'simplenote\.com'],
            'medium': [r'medium\.com'],
            'substack': [r'substack\.com'],
            'github': [r'github\.com'],
            'reddit': [r'reddit\.com'],
            'hackernews': [r'news\.ycombinator\.com'],
        }
    
    def extract(self, url: str) -> ExtractedContent:
        """
        🎯 Extract content from any URL
        
        Args:
            url: URL to extract content from
            
        Returns:
            ExtractedContent: Extracted content with metadata
        """
        try:
            # Detect platform
            platform = self._detect_platform(url)
            
            # Fetch content
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract using platform-specific logic
            if platform == 'chatgpt':
                return self._extract_chatgpt(soup, url, platform)
            elif platform == 'claude':
                return self._extract_claude(soup, url, platform)
            elif platform == 'simplenote':
                return self._extract_simplenote(soup, url, platform)
            else:
                return self._extract_generic(soup, url, platform)
                
        except requests.RequestException as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={},
                success=False,
                error_message=f"Network error: {str(e)}",
                platform=platform,
                url=url
            )
        except Exception as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={},
                success=False,
                error_message=f"Extraction error: {str(e)}",
                platform=platform,
                url=url
            )
    
    def _detect_platform(self, url: str) -> str:
        """Detect platform from URL"""
        parsed_url = urlparse(url).netloc.lower()
        
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, parsed_url):
                    return platform
        
        return "generic"
    
    def _extract_chatgpt(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from ChatGPT share links"""
        try:
            # Try to find conversation content
            messages = []
            
            # Look for message containers
            message_selectors = [
                'div[data-message-author-role]',
                '.message',
                '[class*="message"]',
                'div.group',
                'div[role="group"]'
            ]
            
            for selector in message_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        text = element.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out short/empty messages
                            messages.append(text)
                    break
            
            # Fallback to general text extraction
            if not messages:
                content = self._extract_text_content(soup)
            else:
                content = '\n\n'.join(messages)
            
            # Extract title
            title = self._extract_title(soup) or "ChatGPT Conversation"
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    'platform': platform,
                    'message_count': len(messages),
                    'extraction_method': 'chatgpt_specific'
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_claude(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Claude.ai conversations"""
        try:
            # Look for Claude conversation elements
            content_selectors = [
                '[data-testid="conversation"]',
                '.conversation',
                '[class*="message"]',
                'main',
                'article'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Claude Conversation"
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    'platform': platform,
                    'extraction_method': 'claude_specific'
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_simplenote(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Extract content from Simplenote public links"""
        try:
            # Look for Simplenote content
            content_selectors = [
                '.note-content',
                '.simplenote-content',
                '.content',
                'pre',
                'main'
            ]
            
            content = ""
            for selector in content_selectors:
                element = soup.select_one(selector)
                if element:
                    content = element.get_text(strip=True)
                    if content:
                        break
            
            if not content:
                content = self._extract_text_content(soup)
            
            title = self._extract_title(soup) or "Simplenote"
            
            return ExtractedContent(
                title=title,
                content=content,
                metadata={
                    'platform': platform,
                    'extraction_method': 'simplenote_specific'
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return self._extract_generic(soup, url, platform)
    
    def _extract_generic(self, soup: BeautifulSoup, url: str, platform: str) -> ExtractedContent:
        """Generic content extraction for any website"""
        try:
            # Extract title
            title = self._extract_title(soup)
            
            # Extract main content
            content = self._extract_text_content(soup)
            
            return ExtractedContent(
                title=title or "Web Content",
                content=content,
                metadata={
                    'platform': platform,
                    'extraction_method': 'generic',
                    'content_length': len(content)
                },
                success=bool(content),
                platform=platform,
                url=url
            )
            
        except Exception as e:
            return ExtractedContent(
                title="",
                content="",
                metadata={'platform': platform},
                success=False,
                error_message=f"Generic extraction failed: {str(e)}",
                platform=platform,
                url=url
            )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        # Try multiple title sources
        title_selectors = [
            'h1',
            'title', 
            '[property="og:title"]',
            '[name="twitter:title"]',
            '.title',
            '#title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    title = element.get('content', '').strip()
                else:
                    title = element.get_text(strip=True)
                
                if title:
                    return title[:200]  # Limit title length
        
        return ""
    
    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from page"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Try main content selectors
        content_selectors = [
            'main',
            'article', 
            '[role="main"]',
            '.content',
            '.post-content',
            '.entry-content',
            '.article-content',
            '#content',
            'body'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(separator=' ', strip=True)
                if text and len(text) > 100:  # Ensure meaningful content
                    return text
        
        # Fallback: extract all text
        return soup.get_text(separator=' ', strip=True)
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self.session.close()