"""
URL management utilities for open-geodata-api
"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from .download import is_url_expired, is_signed_url
import warnings


def validate_urls(urls_dict: Dict[str, Any], check_expiry: bool = True, 
                 check_access: bool = False, timeout: int = 30) -> Dict[str, Any]:
    """
    Validate a collection of URLs for accessibility and expiration.
    
    Args:
        urls_dict: Dictionary of URLs to validate
        check_expiry: Whether to check URL expiration
        check_access: Whether to test HTTP accessibility
        timeout: Request timeout for access checks
    
    Returns:
        Validation results with detailed status
    """
    
    def flatten_urls(data, prefix=""):
        """Flatten nested URL structure."""
        flat_urls = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{prefix}/{key}" if prefix else key
                
                if isinstance(value, str) and value.startswith(('http://', 'https://')):
                    flat_urls[new_key] = value
                elif isinstance(value, dict):
                    flat_urls.update(flatten_urls(value, new_key))
        
        return flat_urls
    
    # Flatten the URL structure
    flat_urls = flatten_urls(urls_dict)
    
    results = {
        'total_count': len(flat_urls),
        'valid_count': 0,
        'expired_count': 0,
        'inaccessible_count': 0,
        'accessible_count': 0,
        'failed_urls': {},
        'success_rate': 0.0
    }
    
    for url_key, url in flat_urls.items():
        try:
            url_valid = True
            
            # Check expiry if requested
            if check_expiry and is_url_expired(url):
                results['expired_count'] += 1
                results['failed_urls'][url_key] = 'URL expired'
                url_valid = False
            
            # Check HTTP access if requested
            if check_access and url_valid:
                try:
                    response = requests.head(url, timeout=timeout, allow_redirects=True)
                    if response.status_code >= 400:
                        results['inaccessible_count'] += 1
                        results['failed_urls'][url_key] = f'HTTP {response.status_code}'
                        url_valid = False
                    else:
                        results['accessible_count'] += 1
                except requests.RequestException as e:
                    results['inaccessible_count'] += 1
                    results['failed_urls'][url_key] = str(e)
                    url_valid = False
            
            if url_valid:
                results['valid_count'] += 1
                
        except Exception as e:
            results['failed_urls'][url_key] = f'Validation error: {e}'
    
    # Calculate success rate
    if results['total_count'] > 0:
        results['success_rate'] = (results['valid_count'] / results['total_count']) * 100
    
    return results
