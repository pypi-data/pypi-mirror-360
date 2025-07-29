"""
Planetary Computer specific signing functions
"""
from typing import Dict

try:
    import planetary_computer as pc
    SIGNING_AVAILABLE = True
except ImportError:
    SIGNING_AVAILABLE = False

def sign_url(url: str) -> str:
    """Sign a single URL using planetary-computer SDK."""
    if not SIGNING_AVAILABLE:
        raise ImportError("planetary-computer is required for URL signing. Install with: pip install planetary-computer")
    
    try:
        return pc.sign(url)
    except Exception as e:
        raise RuntimeError(f"Failed to sign URL: {e}")

def sign_item(item_dict: Dict) -> Dict:
    """Sign all assets in a STAC item dictionary."""
    if not SIGNING_AVAILABLE:
        raise ImportError("planetary-computer is required for item signing. Install with: pip install planetary-computer")
    
    try:
        return pc.sign(item_dict)
    except Exception as e:
        raise RuntimeError(f"Failed to sign item: {e}")

def sign_asset_urls(asset_urls: Dict[str, str]) -> Dict[str, str]:
    """Sign a dictionary of band/asset URLs."""
    if not SIGNING_AVAILABLE:
        raise ImportError("planetary-computer is required for URL signing. Install with: pip install planetary-computer")
    
    signed_urls = {}
    for band, url in asset_urls.items():
        try:
            signed_urls[band] = pc.sign(url)
        except Exception as e:
            print(f"Warning: Failed to sign URL for band {band}: {e}")
            signed_urls[band] = url
    return signed_urls
