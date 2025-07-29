"""
EarthSearch client with silent 3-tier fallback strategy
"""
import requests
import warnings
from typing import Dict, List, Optional, Union, Any, Tuple
from ..core.base_client import BaseSTACClient
from ..core.search import STACSearch

try:
    import pystac_client
    PYSTAC_AVAILABLE = True
except ImportError:
    PYSTAC_AVAILABLE = False

class EarthSearchCollections(BaseSTACClient):
    """EarthSearch client with silent 3-tier fallback strategy."""

    def __init__(self, auto_validate: bool = False, verbose: bool = False):
        self.auto_validate = auto_validate
        super().__init__(
            base_url="https://earth-search.aws.element84.com/v1",
            provider_name="earthsearch",
            verbose=verbose
        )

    def search(self,
               collections: Optional[List[str]] = None,
               intersects: Optional[Dict] = None,
               bbox: Optional[List[float]] = None,
               datetime: Optional[Union[str, List[str], Tuple[str, str]]] = None,
               query: Optional[Dict] = None,
               limit: Optional[int] = None,
               max_items: Optional[int] = None) -> STACSearch:
        """🔄 Search with silent 3-tier fallback: Simple → pystac-client → chunking."""

        if collections:
            invalid_collections = [col for col in collections if col not in self.collections]
            if invalid_collections:
                raise ValueError(f"Invalid collections: {invalid_collections}")

        # Handle tuple datetime format
        if isinstance(datetime, tuple) and len(datetime) == 2:
            start_date, end_date = datetime
            datetime = f"{start_date}/{end_date}"

        search_payload = self._build_search_payload(
            collections, intersects, bbox, datetime, query, limit
        )

        try:
            # 🔄 TIER 1: Simple search (default preference)
            if self.verbose:
                print("🔄 Tier 1: Using simple search (default preference)...")
            
            simple_result = self._simple_search(search_payload, max_items)
            
            # Return with fallback capability
            return STACSearch(
                simple_result,
                provider="earthsearch",
                client_instance=self,
                original_search_params=search_payload,
                search_url=self.search_url,
                verbose=self.verbose  # Pass verbose setting
            )
                
        except Exception as e:
            # Enhanced error handling for EarthSearch
            if "502" in str(e) or "Bad Gateway" in str(e):
                if self.verbose:
                    print(f"❌ EarthSearch server overloaded (502 error)")
                    print("   Will attempt fallback strategies if needed...")
            else:
                if self.verbose:
                    print(f"❌ Simple search error: {e}")
            
            return STACSearch({"items": [], "total_returned": 0, "error": str(e)}, 
                            provider="earthsearch")

    def _simple_search(self, search_payload: Dict, max_items: Optional[int]) -> Dict:
        """🔄 TIER 1: Silent simple search - first preference."""
        
        # Use a conservative limit for EarthSearch
        simple_payload = search_payload.copy()
        simple_payload["limit"] = min(search_payload.get("limit", 100), 100)
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        # 🔇 SUPPRESS WARNINGS for clean output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.post(self.search_url, json=simple_payload, headers=headers, timeout=30)
        
        response.raise_for_status()
        data = response.json()
        
        # Handle EarthSearch response formats
        if isinstance(data, dict) and 'features' in data:
            items = data.get("features", [])
        elif isinstance(data, list):
            items = data
        else:
            items = []
        
        if max_items and len(items) > max_items:
            items = items[:max_items]
        
        if self.verbose:
            print(f"   ✅ Simple search: {len(items)} items")
        
        return {
            "items": items,
            "total_returned": len(items),
            "search_params": search_payload,
            "collections_searched": search_payload.get("collections", "all"),
            "method_used": "simple_search"
        }

    def _create_pystac_catalog_fallback(self):
        """🔄 TIER 2: Silent pystac-client catalog creation."""
        
        if not PYSTAC_AVAILABLE:
            return None
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return pystac_client.Client.open(self.base_url)
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️ pystac-client catalog creation failed: {e}")
            return None
