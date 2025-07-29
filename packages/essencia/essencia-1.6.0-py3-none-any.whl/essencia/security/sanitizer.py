"""
HTML and Content Sanitization Module.
Provides protection against XSS attacks by sanitizing user input.
"""

import re
import html
import logging
from typing import Optional, Set, Dict, List, Pattern
from functools import lru_cache

logger = logging.getLogger(__name__)


class HTMLSanitizer:
    """
    Sanitize HTML/text content to prevent XSS attacks.
    
    This class provides comprehensive sanitization for user-generated content
    while preserving safe formatting and structure.
    """
    
    # Safe HTML tags that can be preserved
    ALLOWED_TAGS: Set[str] = {
        'p', 'br', 'strong', 'em', 'u', 'i', 'b',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'a', 'img', 'hr', 'span', 'div'
    }
    
    # Safe attributes for specific tags
    ALLOWED_ATTRIBUTES: Dict[str, Set[str]] = {
        'a': {'href', 'title', 'target'},
        'img': {'src', 'alt', 'width', 'height'},
        'blockquote': {'cite'},
        'code': {'class'},
        'span': {'class'},
        'div': {'class'}
    }
    
    # Dangerous patterns that must be removed
    FORBIDDEN_PATTERNS: List[Pattern] = [
        re.compile(r'<script[^>]*?>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<iframe[^>]*?>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<object[^>]*?>.*?</object>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<embed[^>]*?>', re.IGNORECASE),
        re.compile(r'<link[^>]*?>', re.IGNORECASE),
        re.compile(r'<meta[^>]*?>', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
        re.compile(r'data:text/html', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
        re.compile(r'style\s*=\s*["\'].*?(expression|javascript|vbscript)', re.IGNORECASE)
    ]
    
    # URL validation pattern
    SAFE_URL_PATTERN = re.compile(
        r'^(https?://|mailto:|tel:|#|/|\.\.?/)',
        re.IGNORECASE
    )
    
    @classmethod
    @lru_cache(maxsize=1000)
    def sanitize(cls, content: Optional[str], 
                 allow_html: bool = False,
                 max_length: Optional[int] = None) -> str:
        """
        Sanitize content to prevent XSS attacks.
        
        Args:
            content: The content to sanitize
            allow_html: Whether to preserve safe HTML tags
            max_length: Maximum allowed length (None for no limit)
            
        Returns:
            Sanitized content safe for display
        """
        if not content:
            return ""
            
        # Enforce maximum length if specified
        if max_length and len(content) > max_length:
            content = content[:max_length]
            logger.warning(f"Content truncated to {max_length} characters")
        
        # Remove dangerous patterns first
        sanitized = cls._remove_dangerous_patterns(content)
        
        if not allow_html:
            # Escape all HTML entities
            return html.escape(sanitized)
        else:
            # Clean HTML while preserving safe tags
            return cls._clean_html(sanitized)
    
    @classmethod
    def _remove_dangerous_patterns(cls, content: str) -> str:
        """Remove patterns that could lead to XSS."""
        for pattern in cls.FORBIDDEN_PATTERNS:
            content = pattern.sub('', content)
        return content
    
    @classmethod
    def _clean_html(cls, content: str) -> str:
        """
        Clean HTML content by removing unsafe tags and attributes.
        This is a simplified implementation - in production, consider
        using a library like bleach or html-sanitizer.
        """
        # Remove all tags not in allowed list
        tag_pattern = re.compile(r'<(/?)(\w+)([^>]*?)>', re.IGNORECASE)
        
        def clean_tag(match):
            closing = match.group(1)
            tag_name = match.group(2).lower()
            attributes = match.group(3)
            
            if tag_name not in cls.ALLOWED_TAGS:
                return ''
            
            if closing:
                return f'</{tag_name}>'
            
            # Clean attributes
            cleaned_attrs = cls._clean_attributes(tag_name, attributes)
            return f'<{tag_name}{cleaned_attrs}>'
        
        return tag_pattern.sub(clean_tag, content)
    
    @classmethod
    def _clean_attributes(cls, tag_name: str, attributes: str) -> str:
        """Clean attributes for a specific tag."""
        if tag_name not in cls.ALLOWED_ATTRIBUTES:
            return ''
        
        allowed = cls.ALLOWED_ATTRIBUTES[tag_name]
        attr_pattern = re.compile(r'(\w+)\s*=\s*["\']([^"\']*)["\']')
        
        cleaned_attrs = []
        for match in attr_pattern.finditer(attributes):
            attr_name = match.group(1).lower()
            attr_value = match.group(2)
            
            if attr_name in allowed:
                # Additional validation for specific attributes
                if attr_name == 'href' and not cls._is_safe_url(attr_value):
                    continue
                if attr_name == 'src' and not cls._is_safe_url(attr_value):
                    continue
                    
                cleaned_attrs.append(f'{attr_name}="{html.escape(attr_value)}"')
        
        return ' ' + ' '.join(cleaned_attrs) if cleaned_attrs else ''
    
    @classmethod
    def _is_safe_url(cls, url: str) -> bool:
        """Check if a URL is safe to use."""
        return bool(cls.SAFE_URL_PATTERN.match(url))
    
    @classmethod
    def sanitize_for_display(cls, content: Optional[str]) -> str:
        """
        Sanitize content specifically for display in Flet Text components.
        This escapes all HTML and limits length for safety.
        """
        return cls.sanitize(content, allow_html=False, max_length=10000)


class MarkdownSanitizer:
    """
    Sanitize Markdown content to prevent XSS while preserving formatting.
    """
    
    # Dangerous markdown patterns
    DANGEROUS_PATTERNS: List[Pattern] = [
        re.compile(r'<script[^>]*?>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'\[([^\]]+)\]\(javascript:[^)]+\)', re.IGNORECASE),
        re.compile(r'!\[([^\]]*)\]\(javascript:[^)]+\)', re.IGNORECASE),
        re.compile(r'\[([^\]]+)\]\(data:text/html[^)]+\)', re.IGNORECASE),
        re.compile(r'<[^>]+on\w+\s*=', re.IGNORECASE)
    ]
    
    @classmethod
    def sanitize(cls, content: Optional[str], 
                 max_length: Optional[int] = None) -> str:
        """
        Sanitize Markdown content for safe rendering.
        
        Args:
            content: Markdown content to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized markdown content
        """
        if not content:
            return ""
        
        # Enforce maximum length
        if max_length and len(content) > max_length:
            content = content[:max_length]
        
        # Remove dangerous patterns
        sanitized = content
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = pattern.sub('', sanitized)
        
        # Clean HTML within markdown
        html_pattern = re.compile(r'<[^>]+>')
        
        def clean_html_tag(match):
            tag = match.group(0)
            # Only allow basic formatting tags in markdown
            safe_tags = ['br', 'hr', 'strong', 'em', 'code', 'pre']
            tag_name_match = re.match(r'</?(\w+)', tag)
            if tag_name_match and tag_name_match.group(1).lower() in safe_tags:
                return tag
            return html.escape(tag)
        
        sanitized = html_pattern.sub(clean_html_tag, sanitized)
        
        return sanitized


def sanitize_input(content: Optional[str], 
                   input_type: str = 'text',
                   max_length: Optional[int] = None) -> str:
    """
    Convenience function to sanitize different types of input.
    
    Args:
        content: Content to sanitize
        input_type: Type of input ('text', 'html', 'markdown')
        max_length: Maximum allowed length
        
    Returns:
        Sanitized content appropriate for the input type
    """
    if input_type == 'html':
        return HTMLSanitizer.sanitize(content, allow_html=True, max_length=max_length)
    elif input_type == 'markdown':
        return MarkdownSanitizer.sanitize(content, max_length=max_length)
    else:  # Default to text
        return HTMLSanitizer.sanitize(content, allow_html=False, max_length=max_length)


# Field-specific sanitizers for common use cases

def sanitize_name(name: Optional[str]) -> str:
    """Sanitize person names - allow only letters, spaces, hyphens, apostrophes."""
    if not name:
        return ""
    # Remove any HTML/special characters
    sanitized = HTMLSanitizer.sanitize(name, allow_html=False)
    # Allow only specific characters for names
    return re.sub(r'[^a-zA-ZÀ-ÿ\s\-\']', '', sanitized)[:100]


def sanitize_email(email: Optional[str]) -> str:
    """Sanitize email addresses."""
    if not email:
        return ""
    # Basic email sanitization
    sanitized = HTMLSanitizer.sanitize(email, allow_html=False)
    # Remove spaces and limit length
    return sanitized.strip().lower()[:254]


def sanitize_phone(phone: Optional[str]) -> str:
    """Sanitize phone numbers."""
    if not phone:
        return ""
    # Remove everything except numbers, spaces, hyphens, parentheses, and +
    sanitized = re.sub(r'[^\d\s\-\(\)\+]', '', phone)
    return sanitized[:20]


def sanitize_cpf(cpf: Optional[str]) -> str:
    """Sanitize CPF - keep only numbers."""
    if not cpf:
        return ""
    # Keep only digits
    return re.sub(r'\D', '', cpf)[:11]


def sanitize_multiline_text(text: Optional[str], max_length: int = 5000) -> str:
    """Sanitize multiline text fields like notes, observations."""
    return HTMLSanitizer.sanitize(text, allow_html=False, max_length=max_length)