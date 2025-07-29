"""
Core STAC Item class - focused on URL access and metadata
"""
from typing import Dict, Any, Optional, List
from .assets import STACAssets

class STACItem:
    """Universal STAC Item wrapper - focused on URL access and flexibility."""
    
    def __init__(self, item_data: Dict, provider: str = "unknown"):
        self._data = item_data.copy()
        self.provider = provider
        
        self.assets = STACAssets(self._data.get('assets', {}))
        self.properties = self._data.get('properties', {})
        self.geometry = self._data.get('geometry', {})
        self.bbox = self._data.get('bbox', [])
        self.id = self._data.get('id', '')
        self.collection = self._data.get('collection', '')
        self.type = self._data.get('type', 'Feature')
        self.stac_version = self._data.get('stac_version', '')
        self.links = self._data.get('links', [])

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def to_dict(self):
        return self._data.copy()

    def copy(self):
        return STACItem(self._data.copy(), provider=self.provider)

    def get_asset_url(self, asset_key: str, signed: Optional[bool] = None) -> str:
        """Get ready-to-use asset URL with automatic provider handling."""
        if asset_key not in self.assets:
            available_assets = list(self.assets.keys())
            raise KeyError(f"Asset '{asset_key}' not found. Available assets: {available_assets}")
        
        url = self.assets[asset_key].href
        
        # Auto-handle based on provider
        if signed is None:
            signed = (self.provider == "planetary_computer")
        
        if signed and self.provider == "planetary_computer":
            try:
                from ..planetary.signing import sign_url
                return sign_url(url)
            except ImportError:
                print("⚠️ planetary-computer package not found, returning unsigned URL")
                return url
        elif self.provider == "earthsearch":
            try:
                from ..earthsearch.validation import validate_url
                return validate_url(url)
            except ImportError:
                return url
        
        return url
    
    def get_all_asset_urls(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """Get all asset URLs as a dictionary - ready for any raster package."""
        return {
            asset_key: self.get_asset_url(asset_key, signed=signed)
            for asset_key in self.assets.keys()
        }
    
    def get_assets_by_type(self, asset_type: str = "image/tiff") -> Dict[str, str]:
        """Get URLs for assets of specific type (e.g., 'image/tiff' for COGs)."""
        return {
            asset_key: self.get_asset_url(asset_key)
            for asset_key, asset in self.assets.items()
            if asset.type == asset_type
        }
    
    def get_band_urls(self, bands: List[str], signed: Optional[bool] = None) -> Dict[str, str]:
        """Get URLs for specific bands/assets."""
        urls = {}
        missing_bands = []
        
        for band in bands:
            if band in self.assets:
                urls[band] = self.get_asset_url(band, signed=signed)
            else:
                missing_bands.append(band)
        
        if missing_bands:
            available_assets = list(self.assets.keys())
            print(f"⚠️ Bands not available: {missing_bands}")
            print(f"📊 Available assets: {available_assets}")
        
        return urls
    
    def list_assets(self) -> List[str]:
        """Return list of available asset keys."""
        return list(self.assets.keys())

    def has_asset(self, asset_key: str) -> bool:
        """Check if asset exists."""
        return asset_key in self.assets

    def get_rgb_urls(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """Get RGB band URLs (convenience method)."""
        rgb_bands = ['red', 'green', 'blue']
        return self.get_band_urls(rgb_bands, signed=signed)

    def get_sentinel2_urls(self, signed: Optional[bool] = None) -> Dict[str, str]:
        """Get common Sentinel-2 band URLs (convenience method)."""
        s2_bands = ['B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08', 'B8A', 'B09', 'B11', 'B12']
        es_bands = ['coastal', 'blue', 'green', 'red', 'rededge1', 'rededge2', 'rededge3', 'nir', 'nir08', 'nir09', 'swir16', 'swir22']
        
        available_assets = list(self.assets.keys())
        
        if any(band in available_assets for band in s2_bands):
            return self.get_band_urls(s2_bands, signed=signed)
        elif any(band in available_assets for band in es_bands):
            return self.get_band_urls(es_bands, signed=signed)
        else:
            return self.get_all_asset_urls(signed=signed)
    
    def print_assets_info(self):
        """Print detailed information about all available assets."""
        print(f"📦 Item: {self.id}")
        print(f"🔗 Provider: {self.provider}")
        print(f"📅 Date: {self.properties.get('datetime', 'Unknown')}")
        print(f"☁️ Cloud Cover: {self.properties.get('eo:cloud_cover', 'N/A')}%")
        print(f"📊 Available Assets ({len(self.assets)}):")
        
        for asset_key, asset in self.assets.items():
            print(f"   {asset_key:12s} | {asset.type:30s} | {asset.title}")
        
        print(f"\n💡 Usage Examples:")
        print(f"   # Get single asset URL:")
        if self.assets:
            first_asset = list(self.assets.keys())[0]
            print(f"   url = item.get_asset_url('{first_asset}')")
        print(f"   # Get all URLs:")
        print(f"   all_urls = item.get_all_asset_urls()")
        print(f"   # Get specific bands:")
        print(f"   band_urls = item.get_band_urls(['red', 'green', 'blue'])")

    def __repr__(self):
        return f"STACItem(id='{self.id}', collection='{self.collection}', provider='{self.provider}', assets={len(self.assets)})"
