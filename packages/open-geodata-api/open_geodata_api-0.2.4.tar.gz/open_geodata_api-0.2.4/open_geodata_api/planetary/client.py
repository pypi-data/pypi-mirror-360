"""
Planetary Computer client with silent 3-tier fallback strategy
"""
import requests
import warnings
from typing import Dict, List, Optional, Union, Any
from ..core.base_client import BaseSTACClient
from ..core.search import STACSearch

try:
    import pystac_client
    import planetary_computer
    PYSTAC_AVAILABLE = True
except ImportError:
    PYSTAC_AVAILABLE = False

class PlanetaryComputerCollections(BaseSTACClient):
    """Planetary Computer client with silent 3-tier fallback strategy."""

    def __init__(self, auto_sign: bool = False, verbose: bool = False):
        self.auto_sign = auto_sign
        super().__init__(
            base_url="https://planetarycomputer.microsoft.com/api/stac/v1",
            provider_name="planetary_computer",
            verbose=verbose
        )

    def search(self, 
               collections: Optional[List[str]] = None,
               intersects: Optional[Dict] = None,
               bbox: Optional[List[float]] = None,
               datetime: Optional[Union[str, List[str]]] = None,
               query: Optional[Dict] = None,
               limit: Optional[int] = None,
               max_items: Optional[int] = None) -> STACSearch:
        """🔄 Search with silent 3-tier fallback: Simple → pystac-client → chunking."""
        
        if collections:
            invalid_collections = [col for col in collections if col not in self.collections]
            if invalid_collections:
                raise ValueError(f"Invalid collections: {invalid_collections}")

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
                provider="planetary_computer",
                client_instance=self,
                original_search_params=search_payload,
                search_url=self.search_url,
                verbose=self.verbose  # Pass verbose setting
            )
                
        except Exception as e:
            if self.verbose:
                print(f"❌ Simple search error: {e}")
            return STACSearch({"items": [], "total_returned": 0, "error": str(e)}, 
                            provider="planetary_computer")

    def _simple_search(self, search_payload: Dict, max_items: Optional[int]) -> Dict:
        """🔄 TIER 1: Silent simple search - first preference."""
        
        # Use a reasonable limit for simple search
        simple_payload = search_payload.copy()
        simple_payload["limit"] = min(search_payload.get("limit", 100), 100)
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        # 🔇 SUPPRESS WARNINGS for clean output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            response = requests.post(self.search_url, json=simple_payload, headers=headers, timeout=30)
        
        response.raise_for_status()
        data = response.json()
        
        items = data.get("features", [])
        
        # Sign items if needed
        if self.auto_sign and PYSTAC_AVAILABLE:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    signed_items = []
                    for item in items:
                        signed_item = planetary_computer.sign(item)
                        signed_items.append(signed_item)
                    items = signed_items
            except Exception as e:
                if self.verbose:
                    print(f"⚠️ Auto-signing failed: {e}")
        
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
                modifier = planetary_computer.sign_inplace if self.auto_sign else None
                return pystac_client.Client.open(self.base_url, modifier=modifier)
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️ pystac-client catalog creation failed: {e}")
            return None
