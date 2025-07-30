"""
Comprehensive security headers system for web security protection.

Provides security headers management including:
- HTTPS enforcement
- Content Security Policy (CSP)
- HTTP Strict Transport Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options
- X-XSS-Protection
- Referrer-Policy
"""

import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class CSPDirective(str, Enum):
    """Content Security Policy directives."""
    DEFAULT_SRC = "default-src"
    SCRIPT_SRC = "script-src"
    STYLE_SRC = "style-src"
    IMG_SRC = "img-src"
    FONT_SRC = "font-src"
    CONNECT_SRC = "connect-src"
    MEDIA_SRC = "media-src"
    OBJECT_SRC = "object-src"
    CHILD_SRC = "child-src"
    FRAME_SRC = "frame-src"
    WORKER_SRC = "worker-src"
    MANIFEST_SRC = "manifest-src"
    BASE_URI = "base-uri"
    FORM_ACTION = "form-action"
    FRAME_ANCESTORS = "frame-ancestors"
    UPGRADE_INSECURE_REQUESTS = "upgrade-insecure-requests"
    BLOCK_ALL_MIXED_CONTENT = "block-all-mixed-content"


class ReferrerPolicy(str, Enum):
    """Referrer policy options."""
    NO_REFERRER = "no-referrer"
    NO_REFERRER_WHEN_DOWNGRADE = "no-referrer-when-downgrade"
    ORIGIN = "origin"
    ORIGIN_WHEN_CROSS_ORIGIN = "origin-when-cross-origin"
    SAME_ORIGIN = "same-origin"
    STRICT_ORIGIN = "strict-origin"
    STRICT_ORIGIN_WHEN_CROSS_ORIGIN = "strict-origin-when-cross-origin"
    UNSAFE_URL = "unsafe-url"


@dataclass
class ContentSecurityPolicyConfig:
    """Content Security Policy configuration."""
    directives: Dict[CSPDirective, List[str]] = field(default_factory=dict)
    report_only: bool = False
    report_uri: Optional[str] = None
    
    def add_directive(self, directive: CSPDirective, sources: Union[str, List[str]]):
        """Add or update a CSP directive."""
        if directive not in self.directives:
            self.directives[directive] = []
        
        if isinstance(sources, str):
            sources = [sources]
        
        self.directives[directive].extend(sources)
    
    def to_header_value(self) -> str:
        """Convert CSP config to header value."""
        policy_parts = []
        
        for directive, sources in self.directives.items():
            if sources:
                policy_parts.append(f"{directive.value} {' '.join(sources)}")
            else:
                # Some directives don't need sources (like upgrade-insecure-requests)
                policy_parts.append(directive.value)
        
        if self.report_uri:
            policy_parts.append(f"report-uri {self.report_uri}")
        
        return "; ".join(policy_parts)


@dataclass
class HSTSConfig:
    """HTTP Strict Transport Security configuration."""
    max_age: int = 31536000  # 1 year in seconds
    include_subdomains: bool = True
    preload: bool = False
    
    def to_header_value(self) -> str:
        """Convert HSTS config to header value."""
        parts = [f"max-age={self.max_age}"]
        
        if self.include_subdomains:
            parts.append("includeSubDomains")
        
        if self.preload:
            parts.append("preload")
        
        return "; ".join(parts)


@dataclass
class SecurityHeadersConfig:
    """Comprehensive security headers configuration."""
    # HTTPS enforcement
    enforce_https: bool = True
    https_redirect_permanent: bool = True
    
    # HSTS configuration
    hsts: Optional[HSTSConfig] = field(default_factory=lambda: HSTSConfig())
    
    # CSP configuration
    csp: Optional[ContentSecurityPolicyConfig] = field(default_factory=lambda: ContentSecurityPolicyConfig())
    
    # Other security headers
    x_content_type_options: str = "nosniff"
    x_frame_options: str = "DENY"
    x_xss_protection: str = "1; mode=block"
    referrer_policy: ReferrerPolicy = ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN
    
    # Custom headers
    custom_headers: Dict[str, str] = field(default_factory=dict)
    
    # Environment-specific settings
    development_mode: bool = False
    allowed_hosts: List[str] = field(default_factory=list)


class SecurityHeaders:
    """
    Comprehensive security headers management system.
    
    Provides centralized configuration and application of security headers
    for web security protection.
    
    Example:
        >>> headers = SecurityHeaders()
        >>> headers.update_for_flet()  # Configure for Flet apps
        >>> 
        >>> # Get headers for response
        >>> security_headers = headers.get_headers()
        >>> 
        >>> # Check if HTTPS should be enforced
        >>> if headers.should_enforce_https(request_info):
        >>>     redirect_url = headers.get_https_redirect_url(request_info)
    """
    
    def __init__(self, config: Optional[SecurityHeadersConfig] = None, development_mode: bool = False):
        """
        Initialize security headers manager.
        
        Args:
            config: Security headers configuration
            development_mode: Whether running in development mode
        """
        self.config = config or SecurityHeadersConfig()
        self.config.development_mode = development_mode
        
        # Setup CSP defaults if not configured
        if self.config.csp and not self.config.csp.directives:
            self._setup_default_csp()
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def _setup_default_csp(self):
        """Setup default Content Security Policy."""
        if not self.config.csp:
            self.config.csp = ContentSecurityPolicyConfig()
        
        csp = self.config.csp
        
        if self.config.development_mode:
            # More permissive CSP for development
            csp.add_directive(CSPDirective.DEFAULT_SRC, ["'self'", "'unsafe-inline'", "'unsafe-eval'"])
            csp.add_directive(CSPDirective.SCRIPT_SRC, ["'self'", "'unsafe-inline'", "'unsafe-eval'"])
            csp.add_directive(CSPDirective.STYLE_SRC, ["'self'", "'unsafe-inline'"])
            csp.add_directive(CSPDirective.IMG_SRC, ["'self'", "data:", "blob:"])
            csp.add_directive(CSPDirective.FONT_SRC, ["'self'", "data:"])
            csp.add_directive(CSPDirective.CONNECT_SRC, ["'self'"])
        else:
            # Strict CSP for production
            csp.add_directive(CSPDirective.DEFAULT_SRC, ["'self'"])
            csp.add_directive(CSPDirective.SCRIPT_SRC, ["'self'"])
            csp.add_directive(CSPDirective.STYLE_SRC, ["'self'", "'unsafe-inline'"])  # Many frameworks need inline styles
            csp.add_directive(CSPDirective.IMG_SRC, ["'self'", "data:"])
            csp.add_directive(CSPDirective.FONT_SRC, ["'self'"])
            csp.add_directive(CSPDirective.CONNECT_SRC, ["'self'"])
            csp.add_directive(CSPDirective.OBJECT_SRC, ["'none'"])
            csp.add_directive(CSPDirective.BASE_URI, ["'self'"])
            csp.add_directive(CSPDirective.FORM_ACTION, ["'self'"])
            csp.add_directive(CSPDirective.FRAME_ANCESTORS, ["'none'"])
        
        # Always upgrade insecure requests in production
        if not self.config.development_mode:
            csp.directives[CSPDirective.UPGRADE_INSECURE_REQUESTS] = []
    
    def get_headers(self, request_info: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """
        Get all security headers as a dictionary.
        
        Args:
            request_info: Optional request information for context-aware headers
            
        Returns:
            Dictionary of header names and values
        """
        headers = {}
        
        # HSTS header (only for HTTPS)
        if self.config.hsts and self._should_include_hsts(request_info):
            headers["Strict-Transport-Security"] = self.config.hsts.to_header_value()
        
        # Content Security Policy
        if self.config.csp:
            header_name = "Content-Security-Policy"
            if self.config.csp.report_only:
                header_name = "Content-Security-Policy-Report-Only"
            headers[header_name] = self.config.csp.to_header_value()
        
        # X-Content-Type-Options
        if self.config.x_content_type_options:
            headers["X-Content-Type-Options"] = self.config.x_content_type_options
        
        # X-Frame-Options
        if self.config.x_frame_options:
            headers["X-Frame-Options"] = self.config.x_frame_options
        
        # X-XSS-Protection
        if self.config.x_xss_protection:
            headers["X-XSS-Protection"] = self.config.x_xss_protection
        
        # Referrer-Policy
        if self.config.referrer_policy:
            headers["Referrer-Policy"] = self.config.referrer_policy.value
        
        # Custom headers
        headers.update(self.config.custom_headers)
        
        return headers
    
    def _should_include_hsts(self, request_info: Optional[Dict[str, Any]]) -> bool:
        """Determine if HSTS header should be included."""
        if not request_info:
            return not self.config.development_mode
        
        # Only include HSTS for HTTPS requests
        return request_info.get('scheme') == 'https' or request_info.get('secure', False)
    
    def should_enforce_https(self, request_info: Dict[str, Any]) -> bool:
        """
        Determine if HTTPS should be enforced for this request.
        
        Args:
            request_info: Request information including scheme, host, etc.
            
        Returns:
            True if HTTPS should be enforced
        """
        if not self.config.enforce_https:
            return False
        
        # Don't enforce HTTPS in development mode
        if self.config.development_mode:
            return False
        
        # Already HTTPS
        if request_info.get('scheme') == 'https' or request_info.get('secure', False):
            return False
        
        # Check if host is in allowed list for HTTP
        host = request_info.get('host', '')
        if host in ['localhost', '127.0.0.1'] or host.startswith('192.168.'):
            return False
        
        return True
    
    def get_https_redirect_url(self, request_info: Dict[str, Any]) -> str:
        """
        Get HTTPS redirect URL for HTTP request.
        
        Args:
            request_info: Request information
            
        Returns:
            HTTPS URL to redirect to
        """
        host = request_info.get('host', 'localhost')
        path = request_info.get('path', '/')
        query = request_info.get('query', '')
        
        url = f"https://{host}{path}"
        if query:
            url += f"?{query}"
        
        return url
    
    def validate_csp_violation(self, violation_report: Dict[str, Any]) -> bool:
        """
        Validate and log CSP violation report.
        
        Args:
            violation_report: CSP violation report data
            
        Returns:
            True if violation is valid and logged
        """
        try:
            # Extract key information from violation report
            document_uri = violation_report.get('document-uri', '')
            violated_directive = violation_report.get('violated-directive', '')
            blocked_uri = violation_report.get('blocked-uri', '')
            source_file = violation_report.get('source-file', '')
            line_number = violation_report.get('line-number', 0)
            
            # Log the violation
            self.logger.warning(
                f"CSP Violation: {violated_directive} blocked {blocked_uri} "
                f"on {document_uri} (source: {source_file}:{line_number})"
            )
            
            # Store violation for analysis (could be stored in database)
            self._store_csp_violation(violation_report)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process CSP violation report: {e}")
            return False
    
    def _store_csp_violation(self, violation_report: Dict[str, Any]):
        """Store CSP violation for security analysis."""
        # In a production system, this would store violations in a database
        # For now, we'll just log it with structured data
        violation_data = {
            'timestamp': violation_report.get('timestamp'),
            'document_uri': violation_report.get('document-uri'),
            'violated_directive': violation_report.get('violated-directive'),
            'blocked_uri': violation_report.get('blocked-uri'),
            'source_file': violation_report.get('source-file'),
            'line_number': violation_report.get('line-number'),
            'column_number': violation_report.get('column-number'),
            'status_code': violation_report.get('status-code')
        }
        
        self.logger.info(f"CSP violation stored: {json.dumps(violation_data)}")
    
    def update_for_flet(self):
        """Update CSP configuration for Flet application requirements."""
        if not self.config.csp:
            self.config.csp = ContentSecurityPolicyConfig()
        
        csp = self.config.csp
        
        # Flet-specific CSP requirements
        # Allow WebSocket connections for Flet
        csp.add_directive(CSPDirective.CONNECT_SRC, ["'self'", "ws:", "wss:"])
        
        # Allow inline styles (Flet generates inline styles)
        if CSPDirective.STYLE_SRC in csp.directives:
            if "'unsafe-inline'" not in csp.directives[CSPDirective.STYLE_SRC]:
                csp.add_directive(CSPDirective.STYLE_SRC, ["'unsafe-inline'"])
        else:
            csp.add_directive(CSPDirective.STYLE_SRC, ["'self'", "'unsafe-inline'"])
        
        # Allow data URIs for images (Flet might use them)
        if CSPDirective.IMG_SRC in csp.directives:
            if "data:" not in csp.directives[CSPDirective.IMG_SRC]:
                csp.add_directive(CSPDirective.IMG_SRC, ["data:"])
        else:
            csp.add_directive(CSPDirective.IMG_SRC, ["'self'", "data:"])
        
        # Allow blob URLs for dynamic content
        csp.add_directive(CSPDirective.IMG_SRC, ["blob:"])
        csp.add_directive(CSPDirective.MEDIA_SRC, ["blob:"])
        
        self.logger.info("CSP configuration updated for Flet compatibility")
    
    def get_security_report(self) -> Dict[str, Any]:
        """
        Get security headers configuration report.
        
        Returns:
            Security configuration report
        """
        return {
            "https_enforcement": {
                "enabled": self.config.enforce_https,
                "permanent_redirect": self.config.https_redirect_permanent,
                "development_mode": self.config.development_mode
            },
            "hsts": {
                "enabled": self.config.hsts is not None,
                "max_age": self.config.hsts.max_age if self.config.hsts else 0,
                "include_subdomains": self.config.hsts.include_subdomains if self.config.hsts else False,
                "preload": self.config.hsts.preload if self.config.hsts else False
            },
            "content_security_policy": {
                "enabled": self.config.csp is not None,
                "report_only": self.config.csp.report_only if self.config.csp else False,
                "directives_count": len(self.config.csp.directives) if self.config.csp else 0,
                "report_uri": self.config.csp.report_uri if self.config.csp else None
            },
            "other_headers": {
                "x_content_type_options": self.config.x_content_type_options,
                "x_frame_options": self.config.x_frame_options,
                "x_xss_protection": self.config.x_xss_protection,
                "referrer_policy": self.config.referrer_policy.value
            },
            "custom_headers_count": len(self.config.custom_headers),
            "allowed_hosts": self.config.allowed_hosts
        }


# Global security headers instance storage
_security_headers = None


def get_security_headers(development_mode: bool = False) -> SecurityHeaders:
    """Get global security headers instance."""
    global _security_headers
    if _security_headers is None:
        _security_headers = SecurityHeaders(development_mode=development_mode)
    return _security_headers


def create_secure_csp(application_type: str = "web") -> ContentSecurityPolicyConfig:
    """
    Create CSP configuration for different application types.
    
    Args:
        application_type: Type of application ("web", "api", "admin")
    
    Returns:
        CSP configuration
    """
    csp = ContentSecurityPolicyConfig()
    
    if application_type == "api":
        # Minimal CSP for API endpoints
        csp.add_directive(CSPDirective.DEFAULT_SRC, ["'none'"])
        csp.add_directive(CSPDirective.FRAME_ANCESTORS, ["'none'"])
        csp.directives[CSPDirective.UPGRADE_INSECURE_REQUESTS] = []
        
    elif application_type == "admin":
        # Stricter CSP for admin interfaces
        csp.add_directive(CSPDirective.DEFAULT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.SCRIPT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.STYLE_SRC, ["'self'", "'unsafe-inline'"])
        csp.add_directive(CSPDirective.IMG_SRC, ["'self'", "data:"])
        csp.add_directive(CSPDirective.FONT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.CONNECT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.OBJECT_SRC, ["'none'"])
        csp.add_directive(CSPDirective.BASE_URI, ["'self'"])
        csp.add_directive(CSPDirective.FORM_ACTION, ["'self'"])
        csp.add_directive(CSPDirective.FRAME_ANCESTORS, ["'none'"])
        csp.directives[CSPDirective.UPGRADE_INSECURE_REQUESTS] = []
        csp.directives[CSPDirective.BLOCK_ALL_MIXED_CONTENT] = []
        
    else:  # web
        # Standard web application CSP
        csp.add_directive(CSPDirective.DEFAULT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.SCRIPT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.STYLE_SRC, ["'self'", "'unsafe-inline'"])
        csp.add_directive(CSPDirective.IMG_SRC, ["'self'", "data:", "https:"])
        csp.add_directive(CSPDirective.FONT_SRC, ["'self'", "data:"])
        csp.add_directive(CSPDirective.CONNECT_SRC, ["'self'"])
        csp.add_directive(CSPDirective.MEDIA_SRC, ["'self'"])
        csp.add_directive(CSPDirective.OBJECT_SRC, ["'none'"])
        csp.add_directive(CSPDirective.BASE_URI, ["'self'"])
        csp.add_directive(CSPDirective.FORM_ACTION, ["'self'"])
        csp.add_directive(CSPDirective.FRAME_ANCESTORS, ["'self'"])
        csp.directives[CSPDirective.UPGRADE_INSECURE_REQUESTS] = []
    
    return csp


def create_production_config() -> SecurityHeadersConfig:
    """Create production-ready security headers configuration."""
    config = SecurityHeadersConfig()
    
    # HTTPS enforcement
    config.enforce_https = True
    config.https_redirect_permanent = True
    
    # HSTS with preload
    config.hsts = HSTSConfig(
        max_age=31536000,  # 1 year
        include_subdomains=True,
        preload=True
    )
    
    # Secure CSP
    config.csp = create_secure_csp("web")
    
    # Security headers
    config.x_content_type_options = "nosniff"
    config.x_frame_options = "DENY"
    config.x_xss_protection = "1; mode=block"
    config.referrer_policy = ReferrerPolicy.STRICT_ORIGIN_WHEN_CROSS_ORIGIN
    
    # Additional security headers
    config.custom_headers = {
        "X-Permitted-Cross-Domain-Policies": "none",
        "X-Download-Options": "noopen",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    
    return config


# Export security headers components
__all__ = [
    'CSPDirective',
    'ReferrerPolicy',
    'ContentSecurityPolicyConfig',
    'HSTSConfig',
    'SecurityHeadersConfig',
    'SecurityHeaders',
    'get_security_headers',
    'create_secure_csp',
    'create_production_config'
]