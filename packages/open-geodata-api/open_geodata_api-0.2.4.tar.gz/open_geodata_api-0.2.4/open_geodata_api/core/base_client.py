"""
Base client with silent 3-tier fallback strategy
"""

import requests
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from abc import ABC, abstractmethod
from ..core.search import STACSearch

try:
    import pystac_client
    import planetary_computer
    PYSTAC_AVAILABLE = True
except ImportError:
    PYSTAC_AVAILABLE = False

class BaseSTACClient(ABC):
    """Abstract base class with improved error handling."""
    
    def __init__(self, base_url: str, provider_name: str, verbose: bool = False):
        self.base_url = base_url
        self.search_url = f"{base_url}/search"
        self.provider_name = provider_name
        self.verbose = verbose
        self.collections = self._fetch_collections()
        self._collection_details = {}

    def _fetch_collections(self):
        """Fetch all collections from the STAC API."""
        url = f"{self.base_url}/collections"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            collections = data.get('collections', [])
            return {col['id']: f"{self.base_url}/collections/{col['id']}" for col in collections}
        except requests.RequestException as e:
            # 🔥 FIXED: Better error handling for mocking
            verbose = getattr(self, 'verbose', False)  # Safe attribute access
            if verbose:
                print(f"Error fetching collections: {e}")
            return {}


    def list_collections(self):
        """Return a list of all available collection names."""
        return sorted(list(self.collections.keys()))

    def search_collections(self, keyword):
        """Search for collections containing a specific keyword."""
        keyword = keyword.lower()
        return [col for col in self.collections.keys() if keyword in col.lower()]

    def get_collection_info(self, collection_name):
        """Get detailed information about a specific collection."""
        if collection_name not in self.collections:
            return None

        if collection_name not in self._collection_details:
            try:
                response = requests.get(self.collections[collection_name])
                response.raise_for_status()
                self._collection_details[collection_name] = response.json()
            except requests.RequestException as e:
                if self.verbose:
                    print(f"Error fetching collection details: {e}")
                return None

        return self._collection_details[collection_name]

    def _format_datetime_rfc3339(self, datetime_input: Union[str, datetime]) -> str:
        """Convert datetime to RFC3339 format."""
        if not datetime_input:
            return None

        if isinstance(datetime_input, datetime):
            return datetime_input.strftime('%Y-%m-%dT%H:%M:%SZ')

        datetime_str = str(datetime_input)

        if 'T' in datetime_str and datetime_str.endswith('Z'):
            return datetime_str

        if '/' in datetime_str:
            start_date, end_date = datetime_str.split('/')
            
            if 'T' not in start_date:
                start_rfc3339 = f"{start_date}T00:00:00Z"
            else:
                start_rfc3339 = start_date if start_date.endswith('Z') else f"{start_date}Z"

            if 'T' not in end_date:
                end_rfc3339 = f"{end_date}T23:59:59Z"
            else:
                end_rfc3339 = end_date if end_date.endswith('Z') else f"{end_date}Z"

            return f"{start_rfc3339}/{end_rfc3339}"

        if 'T' not in datetime_str:
            return f"{datetime_str}T00:00:00Z"

        if not datetime_str.endswith('Z'):
            return f"{datetime_str}Z"

        return datetime_str

    def _build_search_payload(self, collections, intersects, bbox, datetime, query, limit):
        """Build search payload from parameters."""
        search_payload = {}
        
        if collections:
            search_payload["collections"] = collections
        if intersects:
            search_payload["intersects"] = intersects
        if bbox:
            search_payload["bbox"] = bbox
        if datetime:
            if isinstance(datetime, list):
                search_payload["datetime"] = "/".join(datetime)
            else:
                search_payload["datetime"] = self._format_datetime_rfc3339(datetime)
        if query:
            search_payload["query"] = query
        if limit:
            search_payload["limit"] = limit
        
        return search_payload

    @abstractmethod
    def search(self, collections: Optional[List[str]] = None, **kwargs) -> STACSearch:
        """Abstract search method to be implemented by each provider."""
        pass

    @abstractmethod
    def _create_pystac_catalog_fallback(self):
        """Create pystac-client catalog for fallback strategy."""
        pass

    def _fallback_chunking_search(self, search_params: Dict, search_url: str = None, verbose: bool = False) -> List[Dict]:
        """🔄 FALLBACK TIER 3: Own chunking implementation (silent)."""
        
        if not search_url:
            search_url = self.search_url
        
        # Simple time-based chunking strategy
        if "datetime" in search_params and "/" in search_params["datetime"]:
            return self._chunked_time_search(search_params, search_url, verbose)
        else:
            return self._simple_pagination_fallback(search_params, search_url, verbose)

    def _chunked_time_search(self, search_params: Dict, search_url: str, verbose: bool = False) -> List[Dict]:
        """Silent time-based chunking for fallback."""
        
        start_date_str, end_date_str = search_params["datetime"].split("/")
        start_dt = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        all_items = []
        chunk_days = 30  # Conservative chunk size
        current_dt = start_dt
        
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        
        while current_dt < end_dt:
            chunk_end = min(current_dt + timedelta(days=chunk_days), end_dt)
            chunk_datetime = f"{current_dt.strftime('%Y-%m-%dT%H:%M:%SZ')}/{chunk_end.strftime('%Y-%m-%dT%H:%M:%SZ')}"
            
            chunk_params = search_params.copy()
            chunk_params["datetime"] = chunk_datetime
            chunk_params["limit"] = 100
            
            try:
                response = requests.post(search_url, json=chunk_params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                chunk_items = data.get('features', data.get('items', []))
                all_items.extend(chunk_items)
                
                if verbose:
                    print(f"   📅 Chunk {current_dt.strftime('%Y-%m-%d')}: {len(chunk_items)} items")
                    
            except Exception as e:
                if verbose:
                    print(f"   ⚠️ Chunk failed: {e}")
            
            current_dt = chunk_end
        
        return all_items

    def _simple_pagination_fallback(self, search_params: Dict, search_url: str, verbose: bool = False) -> List[Dict]:
        """Silent pagination for non-time searches."""
        
        all_items = []
        headers = {'Content-Type': 'application/json', 'Accept': 'application/geo+json'}
        page_params = {**search_params, "limit": 100}
        
        for page in range(10):  # Max 10 pages for safety
            try:
                response = requests.post(search_url, json=page_params, headers=headers, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                page_items = data.get('features', data.get('items', []))
                if not page_items:
                    break
                
                all_items.extend(page_items)
                
                # Simple offset-based pagination
                page_params = {**search_params, "limit": 100, "offset": len(all_items)}
                
                if verbose:
                    print(f"   📄 Page {page + 1}: {len(page_items)} items")
                
            except Exception as e:
                if verbose:
                    print(f"   ⚠️ Page {page + 1} failed: {e}")
                break
        
        return all_items

    def create_bbox_from_center(self, lat: float, lon: float, buffer_km: float = 10) -> List[float]:
        """Create a bounding box around a center point."""
        buffer_deg = buffer_km / 111.0
        return [lon - buffer_deg, lat - buffer_deg, lon + buffer_deg, lat + buffer_deg]

    def create_geojson_polygon(self, coordinates: List[List[float]]) -> Dict:
        """Create a GeoJSON polygon for area of interest."""
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        return {"type": "Polygon", "coordinates": [coordinates]}

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self.collections)} collections, provider='{self.provider_name}')"
