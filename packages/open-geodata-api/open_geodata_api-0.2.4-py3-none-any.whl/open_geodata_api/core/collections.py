"""
Core STAC Item Collection class with enhanced URL access capabilities
"""
from typing import Dict, List, Optional, Any, Union
from .items import STACItem

class STACItemCollection:
    """Universal STAC Item Collection with batch URL access capabilities."""
    
    def __init__(self, items_data: List[Dict], provider: str = "unknown"):
        self._raw_items = items_data
        self.provider = provider
        self._items = [STACItem(item, provider=provider) for item in items_data]

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return self._items[index]

    def __iter__(self):
        return iter(self._items)

    def copy(self):
        return STACItemCollection([item.copy().to_dict() for item in self._items], provider=self.provider)

    def to_list(self):
        """Return list of original item dictionaries."""
        return [item.to_dict() for item in self._items]

    def to_dict(self):
        """Return GeoJSON FeatureCollection format."""
        return {
            "type": "FeatureCollection",
            "features": self._raw_items
        }

    def to_geojson(self):
        """Return GeoJSON FeatureCollection - alias for to_dict()."""
        return self.to_dict()

    def to_dataframe(self, include_geometry=True):
        """Convert to pandas DataFrame with optional geometry."""
        try:
            if include_geometry:
                try:
                    import geopandas as gpd
                    return gpd.GeoDataFrame.from_features(self.to_dict(), crs="epsg:4326")
                except ImportError:
                    raise ImportError("geopandas is required for geometry support. Install with: pip install open-geodata-api[spatial]")
            else:
                import pandas as pd
                records = []
                for item in self._items:
                    record = item.properties.copy()
                    record['id'] = item.id
                    record['collection'] = item.collection
                    record['bbox'] = item.bbox
                    records.append(record)
                return pd.DataFrame(records)
        except ImportError as e:
            raise ImportError(f"Required library not installed: {e}")

    def filter_by_date_range(self, start_date: str, end_date: str):
        """Filter items by date range."""
        filtered_items = []
        for item in self._raw_items:
            item_date = item.get('properties', {}).get('datetime', '')
            if start_date <= item_date <= end_date:
                filtered_items.append(item)
        return STACItemCollection(filtered_items, provider=self.provider)

    def get_unique_collections(self):
        """Get list of unique collections."""
        return list(set(item.collection for item in self._items))

    def get_date_range(self):
        """Get the date range covered by all items."""
        dates = [item.properties.get('datetime') for item in self._items if item.properties.get('datetime')]
        if dates:
            return {"min": min(dates), "max": max(dates)}
        return {"min": None, "max": None}

    def get_all_assets(self):
        """Get ALL available assets/bands across items."""
        asset_keys = set()
        for item in self._items:
            asset_keys.update(item.assets.keys())
        return sorted(list(asset_keys))

    def get_assets_by_pattern(self, patterns: List[str], case_sensitive: bool = False):
        """Get assets that match specific patterns."""
        all_assets = self.get_all_assets()
        matching_assets = []

        for asset in all_assets:
            asset_to_check = asset if case_sensitive else asset.lower()
            patterns_to_check = patterns if case_sensitive else [p.lower() for p in patterns]

            if any(pattern in asset_to_check for pattern in patterns_to_check):
                matching_assets.append(asset)

        return sorted(matching_assets)

    def get_assets_by_collection(self):
        """Get assets organized by collection type."""
        assets_by_collection = {}
        for item in self._items:
            collection = item.collection
            if collection not in assets_by_collection:
                assets_by_collection[collection] = set()
            assets_by_collection[collection].update(item.assets.keys())

        for collection in assets_by_collection:
            assets_by_collection[collection] = sorted(list(assets_by_collection[collection]))

        return assets_by_collection

    def to_products_dict(self, include_metadata=True, include_all_assets=True):
        """Create a structured dictionary of products with asset information."""
        products_dict = {}

        for item in self._items:
            product_id = item.id
            bands = []
            band_urls = {}

            for asset_key, asset in item.assets.items():
                bands.append(asset_key)
                band_urls[asset_key] = {
                    'url': asset.href,
                    'title': asset.title,
                    'type': asset.type
                }

            product_entry = {
                'bands': sorted(bands),
                'band_urls': band_urls,
                'total_bands': len(bands),
                'provider': self.provider
            }

            if include_metadata:
                product_entry['metadata'] = {
                    'collection': item.collection,
                    'datetime': item.properties.get('datetime'),
                    'cloud_cover': item.properties.get('eo:cloud_cover'),
                    'geometry': item.geometry,
                    'bbox': item.bbox,
                    'properties': item.properties
                }

            products_dict[product_id] = product_entry

        return products_dict

    def to_simple_products_list(self, bands_filter=None, signed_urls=None):
        """Create simple products list with optional filtering."""
        products_dict = {}

        for item in self._items:
            product_id = item.id
            available_assets = list(item.assets.keys())

            if bands_filter is not None:
                assets_to_use = [asset for asset in available_assets if asset in bands_filter]
            else:
                assets_to_use = available_assets

            bands_urls = {}
            for asset_key in assets_to_use:
                if signed_urls is None:
                    auto_sign = (self.provider == "planetary_computer")
                else:
                    auto_sign = signed_urls
                
                bands_urls[asset_key] = item.get_asset_url(asset_key, signed=auto_sign)

            if bands_urls:
                products_dict[product_id] = bands_urls

        return products_dict

    def get_available_bands(self):
        """Get ALL unique bands/assets available."""
        return self.get_all_assets()

    def get_common_bands(self):
        """Get bands available in ALL products."""
        if not self._items:
            return []

        common_bands = set(self._items[0].assets.keys())
        for item in self._items[1:]:
            common_bands &= set(item.assets.keys())

        return sorted(list(common_bands))

    def get_all_urls(self, asset_keys: List[str] = None, signed: Optional[bool] = None) -> Dict[str, Dict[str, str]]:
        """
        Get all URLs from all items - ready for any raster package.
        
        Parameters:
        -----------
        asset_keys : list, optional
            Specific asset keys to get URLs for (default: all assets)
        signed : bool, optional
            Whether to sign URLs (auto-detected by provider if None)
        
        Returns:
        --------
        dict: {item_id: {asset_key: url}}
        """
        all_urls = {}
        for item in self._items:
            if asset_keys:
                all_urls[item.id] = item.get_band_urls(asset_keys, signed=signed)
            else:
                all_urls[item.id] = item.get_all_asset_urls(signed=signed)
        return all_urls
    
    def export_urls_json(self, filename: str, asset_keys: List[str] = None):
        """Export all URLs to JSON file for external processing."""
        import json
        urls = self.get_all_urls(asset_keys)
        with open(filename, 'w') as f:
            json.dump(urls, f, indent=2)
        print(f"📁 Exported {len(urls)} items to {filename}")
        print(f"💡 Load with: import json; urls = json.load(open('{filename}'))")

    def print_collection_summary(self):
        """Print summary of the collection."""
        print(f"📦 STAC Item Collection Summary")
        print(f"=" * 40)
        print(f"🔗 Provider: {self.provider}")
        print(f"📊 Total Items: {len(self._items)}")
        
        if self._items:
            collections = self.get_unique_collections()
            print(f"📁 Collections: {collections}")
            
            date_range = self.get_date_range()
            print(f"📅 Date Range: {date_range['min']} to {date_range['max']}")
            
            all_assets = self.get_all_assets()
            print(f"🎯 Available Assets ({len(all_assets)}): {all_assets[:10]}{'...' if len(all_assets) > 10 else ''}")
            
            common_assets = self.get_common_bands()
            print(f"🔗 Common Assets: {common_assets}")

    def __repr__(self):
        return f"STACItemCollection({len(self._items)} items, provider='{self.provider}')"
