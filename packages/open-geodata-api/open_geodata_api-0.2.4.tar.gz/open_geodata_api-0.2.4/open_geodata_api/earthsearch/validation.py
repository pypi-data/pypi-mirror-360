"""
EarthSearch specific validation functions
"""
from typing import Dict

def validate_url(url: str) -> str:
    """Validate URL for EarthSearch assets."""
    if not url:
        raise ValueError("URL cannot be empty")
    if not url.startswith(('http://', 'https://', 's3://')):
        raise ValueError("URL must start with http://, https://, or s3://")
    return url

def validate_item(item_dict: Dict) -> Dict:
    """Validate STAC item dictionary."""
    if not isinstance(item_dict, dict):
        raise ValueError("Item must be a dictionary")
    if 'assets' not in item_dict:
        raise ValueError("Item must contain 'assets' field")
    return item_dict

def validate_asset_urls(asset_urls: Dict[str, str]) -> Dict[str, str]:
    """Validate a dictionary of asset URLs."""
    validated_urls = {}
    for asset_key, url in asset_urls.items():
        try:
            validated_urls[asset_key] = validate_url(url)
        except Exception as e:
            print(f"Warning: Invalid URL for asset {asset_key}: {e}")
            validated_urls[asset_key] = url
    return validated_urls
