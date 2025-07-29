"""
Open Geodata API: Unified Python client for open geospatial data APIs
Supports Microsoft Planetary Computer, AWS EarthSearch, and more
"""

__version__ = "0.2.4"
__author__ = "Mirjan Ali Sha"
__email__ = "mastools.help@gmail.com"

# Core imports - always available
from .planetary.client import PlanetaryComputerCollections
from .earthsearch.client import EarthSearchCollections
from .core.items import STACItem
from .core.assets import STACAsset, STACAssets
from .core.collections import STACItemCollection
from .core.search import STACSearch
from datetime import datetime as dt, timedelta  # 🔥 FIX: Use alias to avoid conflict
from typing import Dict, List, Optional, Union, Any

# Signing and validation - core functionality
from .planetary.signing import sign_url, sign_item, sign_asset_urls
from .earthsearch.validation import validate_url, validate_item, validate_asset_urls

# Basic utilities
from .utils.filters import filter_by_cloud_cover

# Factory functions
def planetary_computer(auto_sign: bool = False, verbose: bool = False):
    """Create Planetary Computer client with enhanced pagination."""
    return PlanetaryComputerCollections(auto_sign=auto_sign, verbose=verbose)

def earth_search(auto_validate: bool = False, verbose: bool = False):
    """Create EarthSearch client with enhanced pagination."""
    return EarthSearchCollections(auto_validate=auto_validate, verbose=verbose)


def get_clients(pc_auto_sign: bool = False, es_auto_validate: bool = False):
    """Get both clients for unified access."""
    return {
        'planetary_computer': planetary_computer(auto_sign=pc_auto_sign),
        'earth_search': earth_search(auto_validate=es_auto_validate)
    }

def info():
    """Display package capabilities."""
    print(f"📦 Open Geodata API v{__version__}")
    print(f"🎯 Core Focus: API access, search, and URL management")
    print(f"")
    print(f"📡 Supported APIs:")
    print(f"   🌍 Microsoft Planetary Computer (with URL signing)")
    print(f"   🔗 AWS Element84 EarthSearch (with URL validation)")
    print(f"")
    print(f"🛠️ Core Capabilities:")
    print(f"   ✅ STAC API search and discovery")
    print(f"   ✅ Asset URL management (automatic signing/validation)")
    print(f"   ✅ DataFrame conversion (pandas/geopandas)")
    print(f"   ✅ Flexible data access (use any raster package you prefer)")
    print(f"")
    print(f"💡 Data Reading Philosophy:")
    print(f"   🔗 We provide URLs - you choose how to read them!")
    print(f"   📦 Use rioxarray, rasterio, GDAL, or any package you prefer")
    print(f"   🚀 Maximum flexibility, zero restrictions")

__all__ = [
    # Client classes
    'PlanetaryComputerCollections', 'EarthSearchCollections',
    # Core STAC classes  
    'STACItem', 'STACAsset', 'STACAssets', 'STACItemCollection', 'STACSearch',
    # URL management
    'sign_url', 'sign_item', 'sign_asset_urls',
    'validate_url', 'validate_item', 'validate_asset_urls',
    # Utilities
    'filter_by_cloud_cover',
    # Factory functions
    'planetary_computer', 'earth_search', 'get_clients', 'info'
]

def compare_providers(collections: List[str],
                     bbox: List[float],
                     datetime: Optional[Union[str, int]] = None,  # Parameter name stays same
                     query: Optional[Dict] = None,
                     cloud_cover: Optional[float] = None,
                     verbose: bool = False) -> Dict:
    """
    🔄 Compare data availability between Planetary Computer and EarthSearch.
    
    Args:
        collections: List of collection names to search
        bbox: Bounding box as [west, south, east, north]
        datetime: Date range as "YYYY-MM-DD/YYYY-MM-DD" or days back as integer
        query: Additional query filters
        cloud_cover: Maximum cloud cover percentage
        verbose: Show detailed progress
    
    Returns:
        Dictionary with comparison results
    
    Examples:
        # Compare last 500 days
        result = ogapi.compare_providers(
            collections=["sentinel-2-l2a"],
            bbox=[-122.5, 47.5, -122.0, 48.0],
            datetime=500,
            cloud_cover=100
        )
        
        # Compare specific date range
        result = ogapi.compare_providers(
            collections=["sentinel-2-l2a"],
            bbox=[-122.5, 47.5, -122.0, 48.0],
            datetime="2023-01-01/2023-12-31",
            cloud_cover=30
        )
    """
    
    # Process datetime parameter
    processed_datetime = datetime
    if isinstance(datetime, int):
        # 🔥 FIX: Use dt.now() instead of datetime.now()
        end_date = dt.now()
        start_date = end_date - timedelta(days=datetime)
        processed_datetime = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        if verbose:
            print(f"🔄 Converted {datetime} days to date range: {processed_datetime}")
    
    # Build query
    search_query = query or {}
    if cloud_cover is not None:
        search_query['eo:cloud_cover'] = {'lt': cloud_cover}
    
    search_params = {
        'collections': collections,
        'bbox': bbox,
        'datetime': processed_datetime,
        'query': search_query if search_query else None
    }
    
    results = {}
    
    # Search Planetary Computer
    try:
        if verbose:
            print("🌍 Searching Planetary Computer...")
        
        pc = planetary_computer(auto_sign=True, verbose=verbose)
        pc_results = pc.search(**search_params)
        pc_items = pc_results.get_all_items()
        
        results['planetary_computer'] = {
            'items_found': len(pc_items),
            'items': [item.to_dict() for item in pc_items],
            'success': True
        }
        
        if verbose:
            print(f"🌍 PC: {len(pc_items)} items found")
            
    except Exception as e:
        results['planetary_computer'] = {
            'items_found': 0,
            'items': [],
            'success': False,
            'error': str(e)
        }
        if verbose:
            print(f"❌ PC error: {e}")
    
    # Search EarthSearch
    try:
        if verbose:
            print("🔗 Searching EarthSearch...")
        
        es = earth_search(verbose=verbose)
        es_results = es.search(**search_params)
        es_items = es_results.get_all_items()
        
        results['earthsearch'] = {
            'items_found': len(es_items),
            'items': [item.to_dict() for item in es_items],
            'success': True
        }
        
        if verbose:
            print(f"🔗 ES: {len(es_items)} items found")
            
    except Exception as e:
        results['earthsearch'] = {
            'items_found': 0,
            'items': [],
            'success': False,
            'error': str(e)
        }
        if verbose:
            print(f"❌ ES error: {e}")
    
    # Generate comparison summary
    pc_count = results['planetary_computer']['items_found']
    es_count = results['earthsearch']['items_found']
    
    summary = {
        'pc_items': pc_count,
        'es_items': es_count,
        'total_items': pc_count + es_count,
        'difference': abs(pc_count - es_count),
        'percentage_difference': abs(pc_count - es_count) / max(pc_count, es_count, 1) * 100,
        'best_provider': 'planetary_computer' if pc_count > es_count else 'earthsearch' if es_count > pc_count else 'equal',
        'recommendation': None
    }
    
    # Generate recommendation
    if pc_count > es_count:
        summary['recommendation'] = f"Use Planetary Computer - {pc_count - es_count} more items available"
    elif es_count > pc_count:
        summary['recommendation'] = f"Use EarthSearch - {es_count - pc_count} more items available"
    else:
        summary['recommendation'] = "Both providers offer equal coverage"
    
    if verbose:
        print(f"\n📊 Comparison Summary:")
        print(f"   🌍 Planetary Computer: {pc_count} items")
        print(f"   🔗 EarthSearch: {es_count} items")
        print(f"   💡 {summary['recommendation']}")
    
    return {
        'search_params': search_params,
        'original_datetime': datetime,
        'processed_datetime': processed_datetime,
        'results': results,
        'summary': summary,
        'timestamp': dt.now().isoformat()  # 🔥 FIX: Use dt.now() here too
    }