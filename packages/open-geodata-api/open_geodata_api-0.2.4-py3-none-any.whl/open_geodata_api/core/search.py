"""
STAC Search with silent 3-tier fallback strategy
"""

import warnings
from typing import Dict, Optional, Any, List, Union
from .collections import STACItemCollection

try:
    import pystac_client
    import planetary_computer
    PYSTAC_AVAILABLE = True
except ImportError:
    PYSTAC_AVAILABLE = False

class STACSearch:
    """Enhanced STAC Search with silent 3-tier fallback strategy."""

    def __init__(self, search_results: Dict, provider: str = "unknown", 
                 client_instance=None, original_search_params: Optional[Dict] = None,
                 search_url: str = None, verbose: bool = False):
        self._results = search_results
        self._items = search_results.get('items', search_results.get('features', []))
        self.provider = provider
        self._client = client_instance
        self._original_params = original_search_params or {}
        self._search_url = search_url
        self._verbose = verbose  # Store verbose setting
        
        # Fallback strategy tracking
        self._fallback_attempted = False
        self._pystac_attempted = False
        self._chunking_attempted = False
        
        # Check if all items are already cached
        self._all_items_cached = search_results.get('all_items_cached', False)
        self._all_items_cache = None
        
        # If all items are already cached, set them up immediately
        if self._all_items_cached:
            self._all_items_cache = STACItemCollection(self._items, provider=self.provider)

    def get_all_items(self) -> STACItemCollection:
        """🔄 3-TIER FALLBACK: Simple → pystac-client → chunking (silent by default)."""
        
        # If all items are already cached, return immediately
        if self._all_items_cache:
            return self._all_items_cache
        
        # If items were already fetched during search, use them
        if self._all_items_cached:
            self._all_items_cache = STACItemCollection(self._items, provider=self.provider)
            return self._all_items_cache
        
        # Start fallback strategy if not already attempted
        if not self._fallback_attempted and self._client:
            self._fallback_attempted = True
            
            # 🔄 STEP 1: Check if we need fallback (exactly 100 items = likely truncated)
            if len(self._items) == 100:
                if self._verbose:
                    print(f"🔄 Detected {len(self._items)} items - attempting fallback strategies...")
                
                # 🔄 STEP 2: Try pystac-client first
                pystac_result = self._try_pystac_fallback()
                if pystac_result:
                    return pystac_result
                
                # 🔄 STEP 3: Try chunking search as last resort
                chunking_result = self._try_chunking_fallback()
                if chunking_result:
                    return chunking_result
                
                if self._verbose:
                    print("⚠️ All fallback strategies failed, returning simple search results")
            else:
                if self._verbose:
                    print(f"✅ Simple search returned {len(self._items)} items (no fallback needed)")
        
        # Return simple search results
        return STACItemCollection(self._items, provider=self.provider)

    def _try_pystac_fallback(self) -> Optional[STACItemCollection]:
        """🔄 FALLBACK TIER 2: Try pystac-client pagination (silent)."""
        
        if self._pystac_attempted or not PYSTAC_AVAILABLE:
            return None
        
        self._pystac_attempted = True
        
        try:
            if self._verbose:
                print("🔄 Tier 2: Trying pystac-client fallback...")
            
            # Create pystac-client catalog for this provider
            pystac_catalog = self._client._create_pystac_catalog_fallback()
            if not pystac_catalog:
                if self._verbose:
                    print("   ❌ pystac-client catalog creation failed")
                return None
            
            # Create pystac-client search
            pystac_search = pystac_catalog.search(**self._original_params)
            
            # 🔇 SUPPRESS DEPRECATION WARNING
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=FutureWarning, module="pystac_client")
                warnings.filterwarnings("ignore", message=".*get_all_items.*deprecated.*")
                
                # Get all items using pystac-client's magic (suppressed warnings)
                pystac_items = pystac_search.get_all_items()
            
            all_items_dicts = [item.to_dict() for item in pystac_items]
            
            if self._verbose:
                print(f"   ✅ pystac-client retrieved {len(all_items_dicts)} total items")
            
            # Cache and return
            self._all_items_cache = STACItemCollection(all_items_dicts, provider=self.provider)
            self._all_items_cached = True
            return self._all_items_cache
            
        except Exception as e:
            if self._verbose:
                print(f"   ❌ pystac-client fallback failed: {e}")
            return None

    def _try_chunking_fallback(self) -> Optional[STACItemCollection]:
        """🔄 FALLBACK TIER 3: Try own chunking search (silent)."""
        
        if self._chunking_attempted:
            return None
        
        self._chunking_attempted = True
        
        try:
            if self._verbose:
                print("🔄 Tier 3: Trying chunking fallback...")
            
            # Use client's chunking method if available
            if hasattr(self._client, '_fallback_chunking_search'):
                chunked_items = self._client._fallback_chunking_search(
                    self._original_params, 
                    self._search_url,
                    verbose=self._verbose
                )
                
                if self._verbose:
                    print(f"   ✅ Chunking retrieved {len(chunked_items)} total items")
                
                # Cache and return
                self._all_items_cache = STACItemCollection(chunked_items, provider=self.provider)
                self._all_items_cached = True
                return self._all_items_cache
            else:
                if self._verbose:
                    print("   ❌ Chunking method not available")
                return None
                
        except Exception as e:
            if self._verbose:
                print(f"   ❌ Chunking fallback failed: {e}")
            return None

    def item_collection(self) -> STACItemCollection:
        """Alias for get_all_items()."""
        return self.get_all_items()
    
    def items(self):
        """Return iterator over current items."""
        for item_data in self._items:
            from .items import STACItem
            yield STACItem(item_data, provider=self.provider)

    def matched(self) -> Optional[int]:
        """Return total number of matched items if available."""
        return self._results.get('numberMatched', self._results.get('matched'))

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return f"STACSearch({len(self._items)} items found, provider='{self.provider}')"
