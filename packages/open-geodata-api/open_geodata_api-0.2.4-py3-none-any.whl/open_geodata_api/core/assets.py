"""
Core STAC Asset classes - common for both PC and EarthSearch
"""
from typing import Dict, Any, Optional

class STACAsset:
    """Universal wrapper for STAC assets compatible with both PC and EarthSearch."""
    
    def __init__(self, asset_data: Dict):
        self._data = asset_data
        self.href = asset_data.get('href', '')
        self.title = asset_data.get('title', '')
        self.type = asset_data.get('type', '')
        self.description = asset_data.get('description', '')
        self.roles = asset_data.get('roles', [])

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)

    def to_dict(self):
        return self._data.copy()

    def copy(self):
        return STACAsset(self._data.copy())

    def __repr__(self):
        return f"STACAsset(href='{self.href}', type='{self.type}')"

class STACAssets:
    """Universal wrapper for STAC assets collection."""
    
    def __init__(self, assets_data: Dict):
        self._data = assets_data
        self._assets = {key: STACAsset(asset) for key, asset in assets_data.items()}

    def __getitem__(self, key):
        return self._assets[key]

    def __iter__(self):
        return iter(self._assets)

    def __contains__(self, key):
        return key in self._assets

    def items(self):
        return self._assets.items()

    def keys(self):
        return self._assets.keys()

    def values(self):
        return self._assets.values()

    def get(self, key, default=None):
        return self._assets.get(key, default)

    def copy(self):
        return STACAssets(self._data.copy())

    def __len__(self):
        return len(self._assets)

    def __repr__(self):
        return f"STACAssets({len(self._assets)} assets)"
