<p align="center">
  <img src="https://github.com/Mirjan-Ali-Sha/open-geodata-api/blob/main/icon.png" alt="Open Geodata API Icon" width="150" height="150" />
</p>

# Open Geodata API - Complete User Guide

## Table of Contents

1. [Introduction](README.md#introduction)
2. [Open Geodata API - Complete Tool Summary](README.md#open-geodata-api---complete-tool-summary)
3. [Installation](README.md#installation)
4. [Quick Start](README.md#quick-start)
5. [Core Concepts](README.md#core-concepts)
6. [API Reference](README.md#api-reference)
7. [Usage Examples](README.md#usage-examples)
8. [Best Practices](README.md#best-practices)
9. [Troubleshooting](README.md#troubleshooting)
10. [Advanced Usage](README.md#advanced-usage)
11. [Utility Functions](README.md#utils-functions)
12. [CLI Usage](README.md#cli-usage)
13. [FAQ](README.md#faq)

## Introduction

### What is Open Geodata API?

**Open Geodata API** is a unified Python client library that provides seamless access to multiple open geospatial data APIs. It focuses on **API access, search, and URL management** while maintaining maximum flexibility for data reading and processing.

## Open Geodata API - Complete Tool Summary

**🛰️ Unified Python Client for Satellite Data Access**

#### **What It Does**

✅ **One Interface** - Access Microsoft Planetary Computer \& AWS EarthSearch APIs<br>
✅ **Smart URLs** - Automatic signing, validation, and expiration handling<br>
✅ **Your Choice** - Use any raster package (rioxarray, rasterio, GDAL)<br>
✅ **Complete Workflow** - Search → Filter → Download → Analyze

#### **Key Capabilities**

✅ **Python API** - Programmatic access with full flexibility<br>
✅ **Command Line** - `ogapi` CLI for all operations with help<br>
✅ **Smart Downloads** - Progress tracking, resume, batch processing<br>
✅ **Data Filtering** - Cloud cover, temporal, quality-based filtering<br>
✅ **URL Management** - Export, validate, and refresh URLs automatically


### Supported APIs

| API | Provider | Authentication | URL Handling |
| :-- | :-- | :-- | :-- |
| **Planetary Computer** | Microsoft | API Key + Signing | Automatic signing |
| **EarthSearch** | Element84/AWS | None required | URL validation |

### Philosophy

🎯 **Core Focus**: We provide URLs - you choose how to read them!<br>
📦 **Use Any Package**: rioxarray, rasterio, GDAL, or any package you prefer<br>
🚀 **Maximum Flexibility**: Zero restrictions on your workflow

## Installation

### Basic Installation

```bash
# Install core package
pip install open-geodata-api
```


### Optional Dependencies

```bash
# For spatial analysis (shapely, geopandas)
pip install open-geodata-api[spatial]

# For raster reading suggestions (rioxarray,rasterio, xarray)
pip install open-geodata-api[io]  # rioxarray + xarray

# For complete examples (shapely, geopandas, rioxarray, rasterio, xarray)
pip install open-geodata-api[complete]

# Development dependencies
pip install open-geodata-api[dev]
```


### Verify Installation

```python
import open_geodata_api as ogapi
ogapi.info()
```


## Quick Start

### 30-Second Example

```python
import open_geodata_api as ogapi

# Get clients for both APIs
clients = ogapi.get_clients(pc_auto_sign=True)
pc = clients['planetary_computer']
es = clients['earth_search']

# Search for Sentinel-2 data
results = pc.search(
    collections=["sentinel-2-l2a"],
    bbox=[-122.5, 47.5, -122.0, 48.0],
    datetime="2024-01-01/2024-03-31"
)

# Get items and URLs
items = results.get_all_items()
item = items[0]

# Get ready-to-use URLs
blue_url = item.get_asset_url('B02')  # Automatically signed!
all_urls = item.get_all_asset_urls()  # All assets

# Use with ANY raster package
import rioxarray
data = rioxarray.open_rasterio(blue_url)

# Or use with rasterio
import rasterio
with rasterio.open(blue_url) as src:
    data = src.read(1)
```


### 5-Minute Tutorial

```python
# 1. Import and setup
import open_geodata_api as ogapi

# 2. Create clients
pc = ogapi.planetary_computer(auto_sign=True)
es = ogapi.earth_search()

# 3. Search for data
search_params = {
    'collections': ['sentinel-2-l2a'],
    'bbox': [-122.5, 47.5, -122.0, 48.0],
    'datetime': '2024-01-01/2024-03-31',
    'query': {'eo:cloud_cover': {'lt': 30}}
}

pc_results = pc.search(**search_params, limit=10)
es_results = es.search(**search_params, limit=10)

# 4. Work with results
pc_items = pc_results.get_all_items()
es_items = es_results.get_all_items()

print(f"Found: PC={len(pc_items)}, ES={len(es_items)} items")

# 5. Get URLs and use with your preferred package
item = pc_items[0]
item.print_assets_info()

# Get specific bands
rgb_urls = item.get_band_urls(['B04', 'B03', 'B02'])  # Red, Green, Blue
print(f"RGB URLs: {rgb_urls}")

# Use URLs with any package you want!
```


## Core Concepts

### STAC (SpatioTemporal Asset Catalog)

Open Geodata API works with STAC-compliant APIs. Key STAC concepts:

- **Collections**: Groups of related datasets (e.g., "sentinel-2-l2a")
- **Items**: Individual products/scenes with metadata
- **Assets**: Individual files (bands, thumbnails, metadata)


### Package Architecture

```
open-geodata-api/
├── Core Classes (Universal)
│   ├── STACItem           # Individual products
│   ├── STACItemCollection # Groups of products  
│   ├── STACAsset          # Individual files
│   └── STACSearch         # Search results
├── API Clients
│   ├── PlanetaryComputerCollections
│   └── EarthSearchCollections
└── Utilities
    ├── URL signing (PC)
    ├── URL validation (ES)
    └── Filtering functions
```


### Provider-Specific Handling

| Feature | Planetary Computer | EarthSearch |
| :-- | :-- | :-- |
| **Authentication** | Automatic via planetary-computer package | None required |
| **URL Signing** | Automatic (auto_sign=True) | Not applicable |
| **Asset Naming** | B01, B02, B03... | coastal, blue, green... |
| **Cloud Cover** | eo:cloud_cover | eo:cloud_cover |

## API Reference

### Factory Functions

#### `planetary_computer(auto_sign=False)`

Creates a Planetary Computer client.

**Parameters:**

- `auto_sign` (bool): Automatically sign URLs for immediate use

**Returns:** `PlanetaryComputerCollections` instance

#### `earth_search(auto_validate=False)`

Creates an EarthSearch client.

**Parameters:**

- `auto_validate` (bool): Validate URLs (currently placeholder)

**Returns:** `EarthSearchCollections` instance

#### `get_clients(pc_auto_sign=False, es_auto_validate=False)`

Creates both clients simultaneously.

**Returns:** Dictionary with 'planetary_computer' and 'earth_search' keys

### Client Methods

#### `search(collections, bbox=None, datetime=None, query=None, limit=100)`

Search for STAC items.

**Parameters:**

- `collections` (list): Collection IDs to search
- `bbox` (list): Bounding box [west, south, east, north]
- `datetime` (str): Date range "YYYY-MM-DD/YYYY-MM-DD"
- `query` (dict): Additional filters like `{"eo:cloud_cover": {"lt": 30}}`
- `limit` (int): Maximum results to return

**Returns:** `STACSearch` instance

#### `list_collections()`

Get list of available collection names.

**Returns:** List of collection ID strings

#### `get_collection_info(collection_name)`

Get detailed information about a specific collection.

**Returns:** Collection metadata dictionary

### STACItem Methods

#### `get_asset_url(asset_key, signed=None)`

Get ready-to-use URL for a specific asset.

**Parameters:**

- `asset_key` (str): Asset name (e.g., 'B02', 'blue', 'red')
- `signed` (bool): Override automatic signing behavior

**Returns:** URL string ready for any raster package

#### `get_all_asset_urls(signed=None)`

Get URLs for all available assets.

**Returns:** Dictionary `{asset_key: url}`

#### `get_band_urls(bands, signed=None)`

Get URLs for specific bands/assets.

**Parameters:**

- `bands` (list): List of asset names

**Returns:** Dictionary `{asset_key: url}`

#### `list_assets()`

Get list of available asset names.

**Returns:** List of asset key strings

#### `print_assets_info()`

Print detailed information about all assets.

### STACItemCollection Methods

#### `get_all_urls(asset_keys=None, signed=None)`

Get URLs from all items in the collection.

**Parameters:**

- `asset_keys` (list, optional): Specific assets to get URLs for
- `signed` (bool, optional): Override signing behavior

**Returns:** Dictionary `{item_id: {asset_key: url}}`

#### `to_dataframe(include_geometry=True)`

Convert collection to pandas/geopandas DataFrame.

**Parameters:**

- `include_geometry` (bool): Include spatial geometry (requires geopandas)

**Returns:** DataFrame with item metadata

#### `export_urls_json(filename, asset_keys=None)`

Export all URLs to JSON file for external processing.

## Usage Examples

### Example 1: Simple Data Discovery

```python
import open_geodata_api as ogapi

# Setup
pc = ogapi.planetary_computer(auto_sign=True)

# Find available collections
collections = pc.list_collections()
sentinel_collections = [c for c in collections if 'sentinel' in c.lower()]
print(f"Sentinel collections: {sentinel_collections}")

# Get collection details
s2_info = pc.get_collection_info('sentinel-2-l2a')
print(f"Sentinel-2 L2A: {s2_info['title']}")
print(f"Description: {s2_info['description'][:100]}...")
```


### Example 2: Geographic Search

```python
# Search around San Francisco Bay Area
bbox = [-122.5, 37.5, -122.0, 38.0]

results = pc.search(
    collections=['sentinel-2-l2a'],
    bbox=bbox,
    datetime='2024-06-01/2024-08-31',
    query={'eo:cloud_cover': {'lt': 20}},  # Less than 20% clouds
    limit=20
)

items = results.get_all_items()
print(f"Found {len(items)} items with <20% cloud cover")

# Convert to DataFrame for analysis
df = items.to_dataframe()
print(f"Date range: {df['datetime'].min()} to {df['datetime'].max()}")
print(f"Cloud cover range: {df['eo:cloud_cover'].min():.1f}% to {df['eo:cloud_cover'].max():.1f}%")
```


### Example 3: Multi-Provider Comparison

```python
# Compare results from both providers
bbox = [-122.2, 47.6, -122.1, 47.7]  # Seattle area

pc_results = pc.search(
    collections=['sentinel-2-l2a'],
    bbox=bbox,
    datetime='2024-01-01/2024-03-31'
)

es_results = es.search(
    collections=['sentinel-2-l2a'], 
    bbox=bbox,
    datetime='2024-01-01T00:00:00Z/2024-03-31T23:59:59Z'
)

pc_items = pc_results.get_all_items()
es_items = es_results.get_all_items()

print(f"Planetary Computer: {len(pc_items)} items")
print(f"EarthSearch: {len(es_items)} items")

# Compare asset availability
if pc_items and es_items:
    pc_assets = pc_items[0].list_assets()
    es_assets = es_items[0].list_assets()
    
    print(f"PC assets: {pc_assets[:5]}")
    print(f"ES assets: {es_assets[:5]}")
```


### Example 4: URL Export for External Processing

```python
# Get URLs for specific bands across multiple items
items = pc_results.get_all_items()

# Export RGB band URLs
rgb_urls = items.get_all_urls(['B04', 'B03', 'B02'])  # Red, Green, Blue

# Save to JSON for external processing
items.export_urls_json('sentinel2_rgb_urls.json', ['B04', 'B03', 'B02'])

# Use the URLs with any package
first_item_urls = rgb_urls[list(rgb_urls.keys())[0]]
print(f"Red band URL: {first_item_urls['B04']}")

# Example with different raster packages
import rioxarray
import rasterio
from osgeo import gdal

red_url = first_item_urls['B04']

# Option 1: rioxarray
red_data_xr = rioxarray.open_rasterio(red_url)

# Option 2: rasterio
with rasterio.open(red_url) as src:
    red_data_rio = src.read(1)

# Option 3: GDAL
red_ds = gdal.Open(red_url)
red_data_gdal = red_ds.ReadAsArray()

print(f"Data shapes - XR: {red_data_xr.shape}, RIO: {red_data_rio.shape}, GDAL: {red_data_gdal.shape}")
```


### Example 5: Batch Processing Setup

```python
# Setup for batch processing
import json

# Search for monthly data
results = pc.search(
    collections=['sentinel-2-l2a'],
    bbox=[-120.0, 35.0, -119.0, 36.0],
    datetime='2024-01-01/2024-12-31',
    query={'eo:cloud_cover': {'lt': 15}},
    limit=100
)

items = results.get_all_items()
print(f"Found {len(items)} low-cloud scenes")

# Group by month
df = items.to_dataframe()
df['month'] = df['datetime'].str[:7]  # YYYY-MM
monthly_counts = df.groupby('month').size()
print("Monthly data availability:")
print(monthly_counts)

# Export all URLs for batch processing
all_urls = items.get_all_urls(['B04', 'B03', 'B02', 'B08'])  # RGB + NIR

# Save configuration for external processing
config = {
    'search_params': {
        'bbox': [-120.0, 35.0, -119.0, 36.0],
        'datetime': '2024-01-01/2024-12-31',
        'collections': ['sentinel-2-l2a']
    },
    'items_found': len(items),
    'urls': all_urls
}

with open('batch_processing_config.json', 'w') as f:
    json.dump(config, f, indent=2)

print("Batch processing configuration saved!")
```


### Example 6: EarthSearch Specific Features

```python
# EarthSearch uses different asset names
es = ogapi.earth_search()

es_results = es.search(
    collections=['sentinel-2-l2a'],
    bbox=[-122.5, 47.5, -122.0, 48.0],
    datetime='2024-06-01T00:00:00Z/2024-08-31T23:59:59Z',
    limit=5
)

es_items = es_results.get_all_items()
item = es_items[0]

# EarthSearch asset names
item.print_assets_info()

# Get URLs using EarthSearch naming
rgb_urls = item.get_band_urls(['red', 'green', 'blue'])
nir_url = item.get_asset_url('nir')

print(f"RGB URLs: {list(rgb_urls.keys())}")
print(f"NIR URL ready: {nir_url[:50]}...")

# All URLs (no signing needed for EarthSearch)
all_urls = item.get_all_asset_urls()
print(f"Total assets available: {len(all_urls)}")
```


## Best Practices

### 1. Client Configuration

```python
# Recommended setup
import open_geodata_api as ogapi

# Auto-sign PC URLs for immediate use
pc = ogapi.planetary_computer(auto_sign=True)
es = ogapi.earth_search()

# Or get both at once
clients = ogapi.get_clients(pc_auto_sign=True)
```


### 2. Search Strategy

```python
# Start with broad search, then refine
results = pc.search(
    collections=['sentinel-2-l2a'],
    bbox=your_bbox,
    datetime='2024-01-01/2024-12-31',
    query={'eo:cloud_cover': {'lt': 50}},  # Start broad
    limit=100
)

# Filter further based on your needs
df = results.get_all_items().to_dataframe()
filtered_df = df[df['eo:cloud_cover'] < 20]  # Refine cloud cover
```


### 3. URL Management

```python
# Let the package handle URL signing automatically
item = items[0]

# This automatically handles signing based on provider
blue_url = item.get_asset_url('B02')  # PC: signed, ES: validated

# Override if needed
unsigned_url = item.get_asset_url('B02', signed=False)
```


### 4. Asset Name Handling

```python
# Handle different naming conventions gracefully
def get_rgb_urls(item):
    """Get RGB URLs regardless of provider naming."""
    assets = item.list_assets()
    
    # Try Planetary Computer naming
    if all(band in assets for band in ['B04', 'B03', 'B02']):
        return item.get_band_urls(['B04', 'B03', 'B02'])
    
    # Try EarthSearch naming  
    elif all(band in assets for band in ['red', 'green', 'blue']):
        return item.get_band_urls(['red', 'green', 'blue'])
    
    else:
        print(f"Available assets: {assets}")
        return {}

# Use the function
rgb_urls = get_rgb_urls(item)
```


### 5. Error Handling

```python
# Robust search with error handling
def safe_search(client, **kwargs):
    """Search with comprehensive error handling."""
    try:
        results = client.search(**kwargs)
        items = results.get_all_items()
        
        if len(items) == 0:
            print("No items found. Try adjusting search parameters.")
            return None
            
        print(f"Found {len(items)} items")
        return items
        
    except Exception as e:
        print(f"Search failed: {e}")
        return None

# Use robust search
items = safe_search(
    pc,
    collections=['sentinel-2-l2a'],
    bbox=your_bbox,
    datetime='2024-01-01/2024-03-31'
)
```


### 6. Memory Management

```python
# For large datasets, process in batches
def process_in_batches(items, batch_size=10):
    """Process items in batches to manage memory."""
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        
        # Get URLs for this batch
        batch_urls = {}
        for item in batch:
            try:
                batch_urls[item.id] = item.get_band_urls(['B04', 'B03', 'B02'])
            except Exception as e:
                print(f"Failed to get URLs for {item.id}: {e}")
        
        # Process batch_urls as needed
        yield batch_urls

# Use batch processing
for batch_urls in process_in_batches(items):
    print(f"Processing batch with {len(batch_urls)} items")
    # Your processing logic here
```


## Troubleshooting

### Common Issues and Solutions

#### Issue: "planetary-computer package not found"

**Problem:** PC URL signing fails

```python
# Error: planetary-computer package not found, returning unsigned URL
```

**Solution:**

```bash
pip install planetary-computer
```


#### Issue: No items found

**Problem:** Search returns empty results

**Solutions:**

```python
# 1. Check collection names
available_collections = pc.list_collections()
print("Available collections:", available_collections)

# 2. Expand search area
bbox = [-123.0, 47.0, -121.0, 48.0]  # Larger area

# 3. Expand date range
datetime = '2023-01-01/2024-12-31'  # Larger time window

# 4. Relax cloud cover
query = {'eo:cloud_cover': {'lt': 80}}  # More permissive
```


#### Issue: Asset not found

**Problem:** `KeyError: Asset 'B02' not found`

**Solutions:**

```python
# 1. Check available assets
item.print_assets_info()

# 2. Use correct naming for provider
# PC: B01, B02, B03...
# ES: coastal, blue, green...

# 3. Handle gracefully
try:
    url = item.get_asset_url('B02')
except KeyError:
    # Try alternative naming
    url = item.get_asset_url('blue')
```


#### Issue: EarthSearch datetime format

**Problem:** EarthSearch requires RFC3339 format

**Solution:**

```python
# Use proper format for EarthSearch
datetime_es = '2024-01-01T00:00:00Z/2024-03-31T23:59:59Z'

# Package handles this automatically in most cases
```


#### Issue: Large data downloads

**Problem:** Memory issues with large datasets

**Solutions:**

```python
# 1. Use overview levels (if your raster package supports it)
import rioxarray
data = rioxarray.open_rasterio(url, overview_level=2)

# 2. Use chunking
data = rioxarray.open_rasterio(url, chunks={'x': 512, 'y': 512})

# 3. Read windows
import rasterio
with rasterio.open(url) as src:
    window = rasterio.windows.Window(0, 0, 1024, 1024)
    data = src.read(1, window=window)
```


### Debug Mode

```python
# Enable debug information
import logging
logging.basicConfig(level=logging.DEBUG)

# Check what URLs are being generated
item = items[0]
print(f"Item ID: {item.id}")
print(f"Provider: {item.provider}")

all_urls = item.get_all_asset_urls()
for asset, url in all_urls.items():
    print(f"{asset}: {url[:50]}...")
```


### Validation Steps

```python
# Validate your setup
def validate_setup():
    """Validate package installation and API access."""
    try:
        import open_geodata_api as ogapi
        print("✅ Package imported successfully")
        
        # Test client creation
        pc = ogapi.planetary_computer()
        es = ogapi.earth_search()
        print("✅ Clients created successfully")
        
        # Test collection listing
        pc_collections = pc.list_collections()
        print(f"✅ PC collections: {len(pc_collections)} available")
        
        # Test simple search
        test_results = pc.search(
            collections=['sentinel-2-l2a'],
            bbox=[-122.0, 47.0, -121.0, 48.0],
            limit=1
        )
        test_items = test_results.get_all_items()
        print(f"✅ Test search: {len(test_items)} items found")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

# Run validation
validate_setup()
```


## Advanced Usage

### Custom Processing Workflows

```python
# Example: Multi-temporal analysis setup
def setup_temporal_analysis(bbox, date_ranges, max_cloud_cover=20):
    """Setup data for temporal analysis."""
    
    all_data = {}
    
    for period_name, date_range in date_ranges.items():
        print(f"Searching for {period_name}...")
        
        results = pc.search(
            collections=['sentinel-2-l2a'],
            bbox=bbox,
            datetime=date_range,
            query={'eo:cloud_cover': {'lt': max_cloud_cover}},
            limit=50
        )
        
        items = results.get_all_items()
        urls = items.get_all_urls(['B04', 'B03', 'B02', 'B08'])  # RGB + NIR
        
        all_data[period_name] = {
            'count': len(items),
            'date_range': date_range,
            'urls': urls
        }
        
        print(f"  Found {len(items)} items")
    
    return all_data

# Use for seasonal analysis
seasonal_data = setup_temporal_analysis(
    bbox=[-120.0, 35.0, -119.0, 36.0],
    date_ranges={
        'spring_2024': '2024-03-01/2024-05-31',
        'summer_2024': '2024-06-01/2024-08-31',
        'fall_2024': '2024-09-01/2024-11-30'
    }
)
```


### Integration with Other Libraries
##### Install Required Packages
```python
pip install stackstac pystac
```
##### The Custom Functions
```python
# Example: Integration with STAC-tools
def integrate_with_stac_tools(items):
    """Convert to format compatible with other STAC tools."""
    
    # Export as standard STAC format
    stac_collection = items.to_dict()  # GeoJSON FeatureCollection
    
    # Use with pystac
    try:
        import pystac
        
        # Convert items for pystac
        pystac_items = []
        for item_data in items.to_list():
            pystac_item = pystac.Item.from_dict(item_data)
            pystac_items.append(pystac_item)
        
        print(f"Converted {len(pystac_items)} items to pystac format")
        return pystac_items
        
    except ImportError:
        print("pystac not available")
        return stac_collection

# Example: Integration with stackstac
def prepare_for_stackstac(items, bands=['B04', 'B03', 'B02']):
    """Prepare data for stackstac processing."""
    
    try:
        import stackstac
        
        # Get STAC items in proper format
        stac_items = [item.to_dict() for item in items]
        
        # Note: URLs need to be properly signed
        # The package handles this automatically
        
        print(f"Prepared {len(stac_items)} items for stackstac")
        print(f"Bands: {bands}")
        
        return stac_items
        
    except ImportError:
        print("stackstac not available")
        return None

if __name__ == "__main__":
    # Use the functions
    stac_items = integrate_with_stac_tools(items)
    stackstac_items = prepare_for_stackstac(items)
    print(f"STAC items: {stac_items} \nStackSTAC items: {stackstac_items}")
    print(f"STAC items: {len(stac_items)} \nStackSTAC items: {len(stackstac_items)}")
    print("Integration and preparation complete!")
```


### Custom URL Processing

```python
# Example: Custom URL validation and processing
def process_urls_custom(items, custom_processor=None):
    """Process URLs with custom logic."""
    
    def default_processor(url):
        """Default URL processor."""
        # Add custom headers, caching, etc.
        return url
    
    processor = custom_processor or default_processor
    
    processed_urls = {}
    
    for item in items:
        item_urls = item.get_all_asset_urls()
        processed_item_urls = {}
        
        for asset, url in item_urls.items():
            processed_url = processor(url)
            processed_item_urls[asset] = processed_url
        
        processed_urls[item.id] = processed_item_urls
    
    return processed_urls

# Example custom processor
def add_caching_headers(url):
    """Add caching parameters to URL."""
    if '?' in url:
        return f"{url}&cache=3600"
    else:
        return f"{url}?cache=3600"

# Use custom processing
cached_urls = process_urls_custom(items, add_caching_headers)
print(f"Cached URLs: {cached_urls}")
```
## Utils Functions

### Utils Functions - Usage Examples

```python
import open_geodata_api as ogapi
from open_geodata_api.utils import (
    filter_by_cloud_cover,
    download_datasets,
    download_url,
    download_from_json,
    download_seasonal,
    download_single_file,
    download_url_dict,
    download_items,
    download_seasonal_data,
    create_download_summary,
    is_url_expired,
    is_signed_url,
    re_sign_url_if_needed
)

# Setup clients
pc = ogapi.planetary_computer(auto_sign=True)
es = ogapi.earth_search()
```

#### Example 1: Complete Workflow - Search and Filter by Cloud Cover
```python
print("🔍 Searching for Sentinel-2 data...")
results = pc.search(
    collections=["sentinel-2-l2a"],
    bbox=[-122.5, 47.5, -122.0, 48.0],  # Seattle area
    datetime="2024-06-01/2024-08-31",
    limit=20
)

items = results.get_all_items()
print(f"Found {len(items)} items")

# Filter by cloud cover using utils
clear_items = filter_by_cloud_cover(items, max_cloud_cover=15)
print(f"After filtering: {len(clear_items)} clear items (<15% clouds)")
```

#### Example 2: Download Single Asset from Search Results
```python
print("\n📥 Downloading single asset...")
first_item = clear_items[^0]
first_item.print_assets_info()

# Get a single band URL and download
red_url = first_item.get_asset_url('B04')  # Red band, auto-signed
downloaded_file = download_single_file(
    red_url, 
    destination="./data/red_band.tif",
    provider="planetary_computer"
)
print(f"Downloaded: {downloaded_file}")
```

#### Example 3: Download RGB Bands from Multiple Items
```python
print("\n🎨 Downloading RGB bands from multiple items...")
rgb_downloads = download_items(
    clear_items[:3],  # First 3 clear items
    base_destination="./rgb_data/",
    asset_keys=['B04', 'B03', 'B02'],  # Red, Green, Blue
    create_product_folders=True
)

print(f"Downloaded RGB data for {len(rgb_downloads)} items")
```

#### Example 4: Multi-Provider Data Collection and Download
```python
print("\n🌍 Comparing data from multiple providers...")

# Search both providers
search_params = {
    'collections': ['sentinel-2-l2a'],
    'bbox': [-120.0, 35.0, -119.0, 36.0],  # California
    'datetime': '2024-07-01/2024-07-31',
    'limit': 5
}

pc_results = pc.search(**search_params)
es_results = es.search(**search_params)

pc_items = pc_results.get_all_items()
es_items = es_results.get_all_items()

print(f"PC found: {len(pc_items)} items")
print(f"ES found: {len(es_items)} items")

# Filter both collections
pc_clear = filter_by_cloud_cover(pc_items, max_cloud_cover=20)
es_clear = filter_by_cloud_cover(es_items, max_cloud_cover=20)

# Download from both providers
print("📦 Downloading from Planetary Computer...")
pc_downloads = download_items(
    pc_clear[:2], 
    base_destination="./pc_data/",
    asset_keys=['B08', 'B04'],  # NIR, Red for NDVI
)

print("📦 Downloading from EarthSearch...")
es_downloads = download_items(
    es_clear[:2], 
    base_destination="./es_data/",
    asset_keys=['nir', 'red'],  # ES naming convention
)
```

#### Example 5: Seasonal Analysis Workflow
```python
print("\n🌱 Setting up seasonal analysis...")

def collect_seasonal_data(bbox, year):
    """Collect data for seasonal analysis."""
    seasons = {
        'spring': f'{year}-03-01/{year}-05-31',
        'summer': f'{year}-06-01/{year}-08-31', 
        'fall': f'{year}-09-01/{year}-11-30',
        'winter': f'{year}-12-01/{year+1}-02-28'
    }
    
    seasonal_data = {}
    
    for season, date_range in seasons.items():
        print(f"🔍 Searching {season} {year} data...")
        
        results = pc.search(
            collections=['sentinel-2-l2a'],
            bbox=bbox,
            datetime=date_range,
            query={'eo:cloud_cover': {'lt': 25}},
            limit=10
        )
        
        items = results.get_all_items()
        filtered_items = filter_by_cloud_cover(items, max_cloud_cover=20)
        
        # Get URLs for NDVI calculation
        urls = filtered_items.get_all_urls(['B08', 'B04'])  # NIR, Red
        
        seasonal_data[season] = {
            'count': len(filtered_items),
            'date_range': date_range,
            'urls': urls
        }
        
        print(f"  Found {len(filtered_items)} clear scenes")
    
    return seasonal_data

# Collect seasonal data
bbox = [-121.0, 38.0, -120.5, 38.5]  # Northern California
seasonal_data = collect_seasonal_data(bbox, 2024)

# Download seasonal data using utils
seasonal_downloads = download_seasonal_data(
    seasonal_data,
    base_destination="./seasonal_analysis/",
    seasons=['spring', 'summer'],  # Only spring and summer
    asset_keys=['B08', 'B04']  # NIR and Red bands
)
```

#### Example 6: URL Management and Re-signing
```python
print("\n🔐 URL management example...")

# Get some URLs from items
item = pc_items[^0] if pc_items else clear_items[^0]
all_urls = item.get_all_asset_urls()

# Check URL status
for asset, url in list(all_urls.items())[:3]:
    print(f"\n🔗 Asset: {asset}")
    print(f"   Signed: {is_signed_url(url)}")
    print(f"   Expired: {is_url_expired(url)}")
    
    # Re-sign if needed
    fresh_url = re_sign_url_if_needed(url, provider="planetary_computer")
    if fresh_url != url:
        print(f"   ✅ URL was re-signed")
```

#### Example 7: Batch Processing with URL Dictionary
```python
print("\n📊 Batch processing workflow...")

# Create a custom URL dictionary from search results
custom_urls = {}
for i, item in enumerate(clear_items[:3]):
    item_id = f"sentinel2_{item.id[-8:]}"  # Shortened ID
    # Get specific bands for analysis
    item_urls = item.get_band_urls(['B02', 'B03', 'B04', 'B08'])
    custom_urls[item_id] = item_urls

print(f"Created custom URL dictionary with {len(custom_urls)} items")

# Download using URL dictionary
batch_downloads = download_url_dict(
    {k: v for k, v in list(custom_urls.items())[^0].items()},  # First item only
    base_destination="./batch_data/",
    provider="planetary_computer",
    create_subfolders=True
)
```
#### Example 8: Export and Import Workflow
```python
print("\n💾 Export/Import workflow...")

# Export URLs to JSON for later processing
import json
with open('./data_urls.json', 'w') as f:
    json.dump(custom_urls, f, indent=2)

print("📤 URLs exported to data_urls.json")

# Download from JSON file using utils
json_downloads = download_from_json(
    './data_urls.json',
    destination="./from_json/",
    asset_keys=['B04', 'B08'],  # Only specific bands
    create_folders=True
)
```

#### Example 9: Download Summary and Reporting
```python
print("\n📋 Creating download summary...")

# Combine all download results
all_downloads = {
    'rgb_downloads': rgb_downloads,
    'pc_downloads': pc_downloads,
    'es_downloads': es_downloads,
    'seasonal_downloads': seasonal_downloads,
    'batch_downloads': batch_downloads,
    'json_downloads': json_downloads
}

# Create comprehensive summary
summary = create_download_summary(
    all_downloads, 
    output_file="./download_report.json"
)

print(f"📊 Download Summary:")
print(f"   Total files: {summary['total_files']}")
print(f"   Successful: {summary['successful_downloads']}")
print(f"   Failed: {summary['failed_downloads']}")
print(f"   Success rate: {summary['success_rate']}")
```

#### Example 10: Advanced Filtering and Processing
```python
print("\n🔬 Advanced processing workflow...")

# Multi-step filtering
def advanced_processing_workflow(bbox, max_cloud=10):
    """Advanced workflow with multiple filtering steps."""
    
    # Step 1: Search with broader criteria
    results = pc.search(
        collections=['sentinel-2-l2a'],
        bbox=bbox,
        datetime='2024-06-01/2024-09-30',
        limit=50
    )
    
    items = results.get_all_items()
    print(f"Step 1: Found {len(items)} total items")
    
    # Step 2: Filter by cloud cover
    clear_items = filter_by_cloud_cover(items, max_cloud_cover=max_cloud)
    print(f"Step 2: {len(clear_items)} items with <{max_cloud}% clouds")
    
    # Step 3: Convert to DataFrame for advanced filtering
    df = clear_items.to_dataframe(include_geometry=False)
    
    # Step 4: Filter by date (summer months only)
    summer_mask = df['datetime'].str.contains('2024-0[^678]')  # June, July, August
    summer_items_ids = df[summer_mask]['id'].tolist()
    
    # Step 5: Get items for summer period
    summer_items = [item for item in clear_items if item.id in summer_items_ids]
    print(f"Step 3: {len(summer_items)} summer items")
    
    # Step 6: Download analysis-ready data
    analysis_downloads = download_items(
        summer_items[:5],  # Top 5 summer items
        base_destination="./analysis_ready/",
        asset_keys=['B02', 'B03', 'B04', 'B08', 'B11', 'B12'],  # Multi-spectral
        create_product_folders=True
    )
    
    return analysis_downloads, summer_items

# Run advanced workflow
analysis_results, summer_items = advanced_processing_workflow(
    bbox=[-122.0, 37.0, -121.5, 37.5],  # San Francisco Bay
    max_cloud=5
)

print(f"✅ Analysis-ready data downloaded for {len(analysis_results)} items")
```

#### Example 11: Error Handling and Resilient Downloads
```python
print("\n🛡️ Resilient download example...")

def resilient_download(items, max_retries=3):
    """Download with retry logic and error handling."""
    
    successful_downloads = {}
    failed_downloads = {}
    
    for item in items[:2]:  # Process first 2 items
        item_id = item.id
        retries = 0
        
        while retries < max_retries:
            try:
                # Try to download key bands
                downloads = download_items(
                    [item],
                    base_destination=f"./resilient_data/attempt_{retries+1}/",
                    asset_keys=['B04', 'B08'],
                    create_product_folders=True
                )
                
                successful_downloads[item_id] = downloads
                print(f"✅ Successfully downloaded {item_id}")
                break
                
            except Exception as e:
                retries += 1
                print(f"❌ Attempt {retries} failed for {item_id}: {e}")
                
                if retries >= max_retries:
                    failed_downloads[item_id] = str(e)
                    print(f"💀 Gave up on {item_id} after {max_retries} attempts")
    
    return successful_downloads, failed_downloads

# Run resilient download
successful, failed = resilient_download(clear_items)
print(f"Resilient download completed: {len(successful)} successful, {len(failed)} failed")

print("\n🎉 All utils function examples completed!")
print(f"Check your './data/' directory for downloaded files")
```

## CLI Usage

### Command Line Interface (CLI) Usage
Open Geodata API provides a comprehensive CLI for satellite data discovery, filtering, and downloading. After installation, use the `ogapi` command to access all functionality.

#### Show package information
```bash
ogapi info
```

#### Get help for any command
```bash
ogapi --help
```
```bash
ogapi collections --help
```
```bash
ogapi search items --help
```
### Collections Management
#### List all collections from both providers
```bash
ogapi collections list
```
#### List from specific provider
```bash
ogapi collections list --provider pc
```
```bash
ogapi collections list --provider es
```

#### Filter collections by keyword
```bash
ogapi collections list --filter sentinel
```

#### Save results to file
```bash
ogapi collections list --output collections.json
```

### Search Collections
#### Find collections by keyword
```bash
ogapi collections search sentinel
```
```bash
ogapi collections search landsat --provider pc
```
```bash
ogapi collections search modis --provider both
```

### Get Collection Information
#### Get detailed collection info
```bash
ogapi collections info sentinel-2-l2a
```
```bash
ogapi collections info sentinel-2-l2a --provider es
```
```bash
ogapi collections info landsat-c2-l2 --output collection_info.json
```

### Data Search
#### Search for Sentinel-2 data in Seattle area
```bash
ogapi search items --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --datetime "2024-06-01/2024-08-31" --limit 10
```

#### Search with cloud cover filter
```bash
ogapi search items --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --cloud-cover 20 --output search_results.json
```

#### Search multiple collections
```bash
ogapi search items --collections "sentinel-2-l2a,landsat-c2-l2" --bbox "-120.0,35.0,-119.0,36.0" --datetime "2024-01-01/2024-12-31"
```
#### Advanced Search with JSON Query
```bash
ogapi search items --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --query '{"eo:cloud_cover":{"lt":15},"platform":{"eq":"sentinel-2a"}}' --output advanced_search.json
```

#### Find recent clear data (last 30 days)
```bash
ogapi search quick sentinel-2-l2a "-122.5,47.5,-122.0,48.0"
```

#### Customize time range and cloud threshold
```bash
ogapi search quick sentinel-2-l2a "-122.5,47.5,-122.0,48.0" --days 7 --cloud-cover 10 --limit 5
```

#### Save results for later processing
```bash
ogapi search quick landsat-c2-l2 "-120.0,35.0,-119.0,36.0" --output recent_landsat.json
```

### Compare Data Availability Between Providers
#### Compare Sentinel-2 availability
```bash
ogapi search compare --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --datetime "2024-06-01/2024-08-31"
```
#### Compare with cloud filtering
```bash
ogapi search compare --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --cloud-cover 25 --output comparison_results.json
```

### Working with Items
#### Show info for first item in search results
```bash
ogapi items info search_results.json
```
#### Show info for specific item by index
```bash
ogapi items info search_results.json --item-index 2
```
#### Show detailed metadata
```bash
ogapi items info search_results.json --show-all --output item_details.json
```
#### List all assets for an item
```bash
ogapi items assets search_results.json
```
#### Filter assets by pattern
```bash
ogapi items assets search_results.json --type "image/tiff"
```
#### Show URLs for assets
```bash
ogapi items assets search_results.json --show-urls
```
#### Get URLs for RGB bands
```bash
ogapi items urls search_results.json --assets "B04,B03,B02"
```
#### Get all asset URLs
```bash
ogapi items urls search_results.json --output all_urls.json
```
#### Get URLs by pattern
```bash
ogapi items urls search_results.json --pattern "B0" --output optical_bands.json
```
#### Get unsigned URLs
```bash
ogapi items urls search_results.json --unsigned
```
### Compare Items by Quality
#### Compare items by cloud cover (find clearest)
```bash
ogapi items compare search_results.json
```
#### Compare by date (find most recent)
```bash
ogapi items compare search_results.json --metric date
```
#### Compare asset availability
```bash
ogapi items compare search_results.json --metric assets --max-items 10
```
### Data Download
#### Download all assets from search results
```bash
ogapi download search-results search_results.json
```
#### Download specific bands only
```bash
ogapi download search-results search_results.json --assets "B04,B03,B02" --destination "./rgb_data/"
```
#### Download with additional filtering
```bash
ogapi download search-results search_results.json --cloud-cover 15 --max-items 5 --assets "B08,B04"
```
#### Create flat file structure
```bash
ogapi download search-results search_results.json --flat-structure --destination "./satellite_data/
```
#### Download single file
```bash
ogapi download url "https://example.com/sentinel2_B04.tif"
```
#### Download to specific location
```bash
ogapi download url "https://example.com/B04.tif" --destination "./data/red_band.tif"
```
#### Download with provider specification (it will handdle url validation)
```bash
ogapi download url "https://pc.example.com/B04.tif" --provider pc
```
#### Download from exported URLs
```bash
ogapi download urls-json exported_urls.json
```
#### Custom destination
```bash
ogapi download urls-json urls.json --destination "./downloads/" --flat-structure
```
#### Download all seasons from seasonal JSON
```bash
ogapi download seasonal seasonal_data.json
```
#### Download specific seasons and assets
```bash
ogapi download seasonal seasonal_data.json --seasons "spring,summer" --assets "B08,B04" --destination "./time_series/"
```
### Filter by Cloud Cover
#### Filter search results by cloud cover
```bash
ogapi utils filter-clouds search_results.json --max-cloud-cover 20
```
#### Filter and save results
```bash
ogapi utils filter-clouds search_results.json --max-cloud-cover 15 --output clear_results.json --show-stats
```
### Export URLs
#### Export all URLs from search results
```bash
ogapi utils export-urls search_results.json --output all_urls.json
```
#### Export specific assets
```bash
ogapi utils export-urls search_results.json --output rgb_urls.json --assets "B04,B03,B02"
```
#### Export in simple format
```bash
ogapi utils export-urls search_results.json --output simple_urls.json --format simple
```
#### Export unsigned URLs
```bash
ogapi utils export-urls search_results.json --output unsigned_urls.json --unsigned
```
### Validate URLs
#### Basic URL validation
```bash
ogapi utils validate-urls urls.json
```
#### Check accessibility (HTTP requests)
```bash
ogapi utils validate-urls urls.json --check-access
```
#### Fix expired URLs
```bash
ogapi utils validate-urls urls.json --fix-expired --output fixed_urls.json
```
#### Skip expiry check for speed
```bash
ogapi utils validate-urls urls.json --no-check-expiry
```
### Analyze Search Results
#### Analyze cloud cover distribution
```bash
ogapi utils analyze search_results.json
```
#### Temporal analysis
```bash
ogapi utils analyze search_results.json --metric temporal
```
#### Asset availability analysis
```bash
ogapi utils analyze search_results.json --metric assets --output analysis_report.json
```
### Create Download Summaries
#### Create detailed download summary
```bash
ogapi utils download-summary download_results.json
```
#### Brief summary
```bash
ogapi utils download-summary results.json --format brief
```
#### Save summary report
```bash
ogapi utils download-summary results.json --output report.json
```
### Complete Workflow Examples
#### 1.1: Search for data (Basic RGB Download Workflow)
```bash
ogapi search items --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --datetime "2024-06-01/2024-08-31" --cloud-cover 20 --output search_results.json
```
#### 1.2: Filter for very clear imagery
```bash
ogapi utils filter-clouds search_results.json --max-cloud-cover 10 --output clear_results.json
```
#### 1.3: Download RGB bands
```bash
ogapi download search-results clear_results.json --assets "B04,B03,B02" --destination "./rgb_analysis/"
```
#### 1.4: Create summary
```bash
ogapi utils download-summary download_results.json
```
#### 2.1: Search for data (NDVI Analysis Workflow)
```bash
ogapi search items --collections sentinel-2-l2a --bbox "-120.0,35.0,-119.0,36.0" --datetime "2024-01-01/2024-12-31" --cloud-cover 25 --output yearly_search.json
```
#### 2.2: Filter by seasons and export URLs
```bash
ogapi utils filter-clouds yearly_search.json --max-cloud-cover 15 --output clear_yearly.json
```
```bash
ogapi utils export-urls clear_yearly.json --assets "B08,B04" --output ndvi_urls.json
```
#### 2.3: Download NDVI bands
```bash
ogapi download urls-json ndvi_urls.json --destination "./ndvi_analysis/"
```
#### 3.1 Compare data availability (Multi-Provider Comparison)
```bash
ogapi search compare --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --datetime "2024-06-01/2024-08-31" --output comparison.json
```
#### 3.2 Search both providers separately
```bash
ogapi search items --provider pc --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --cloud-cover 20 --output pc_results.json
```
```bash
ogapi search items --provider es --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --cloud-cover 20 --output es_results.json
```
#### 3.3 Download from best provider
```bash
ogapi download search-results pc_results.json --max-items 3 --destination "./pc_data/"
```
#### 4.1 Search and analyze (Quality Assessment Workflow) 
```bash
ogapi search items --collections sentinel-2-l2a --bbox "-122.5,47.5,-122.0,48.0" --limit 50 --output large_search.json
```
#### 4.2 Analyze data quality 
```bash
ogapi utils analyze large_search.json --metric cloud_cover
```
```bash
ogapi utils analyze large_search.json --metric temporal
```
```bash
ogapi utils analyze large_search.json --metric assets
```
#### 4.3 Compare individual items
```bash
ogapi items compare large_search.json --metric cloud_cover
```
#### 4.4 Download best items only
```bash
ogapi utils filter-clouds large_search.json --max-cloud-cover 10 --output best_quality.json
```
```bash
ogapi download search-results best_quality.json --max-items 5
```
### Global Options
**All commands support these global options:**
#### Enable verbose output for debugging
```bash
ogapi --verbose [command]
```
#### Show version
```bash
ogapi --version
```
#### Get help for any command
```bash
ogapi [command] --help
```
```bash
ogapi [command] [subcommand] --help
```

### Tips and Best Practices

1. **Start Small**: Use `--limit` and `--max-items` to test workflows before large downloads
2. **Save Results**: Always use `--output` to save search results for reprocessing
3. **Filter Early**: Use cloud cover filters to reduce data volume
4. **Check Status**: Use validation commands before large downloads
5. **Resume Downloads**: Most download commands support resuming interrupted transfers
6. **Use Verbose Mode**: Add `--verbose` for detailed debugging information

### Environment Variables
#### Optional: Set default provider
```bash
export OGAPI_DEFAULT_PROVIDER=pc
```
#### Optional: Set default destination
```bash
export OGAPI_DEFAULT_DEST=./satellite_data/
```

## FAQ

### General Questions

**Q: What makes this package different from using APIs directly?**

A: Key advantages:

- Unified interface across multiple APIs
- Automatic URL signing/validation
- Consistent error handling
- No lock-in to specific data reading packages
- Built-in best practices

**Q: Can I use this with my existing geospatial workflow?**

A: Absolutely! The package provides URLs that work with any raster reading library:

```python
url = item.get_asset_url('red')

# Use with your existing tools
import rioxarray; data = rioxarray.open_rasterio(url)
import rasterio; data = rasterio.open(url)
from osgeo import gdal; data = gdal.Open(url)
```

**Q: Do I need API keys?**

A: Only for Planetary Computer. EarthSearch is completely open.

### Technical Questions

**Q: How does automatic URL signing work?**

A: When `auto_sign=True`, the package:

1. Detects the provider (PC vs ES)
2. For PC: Uses the planetary-computer package to sign URLs
3. For ES: Returns URLs as-is (no signing needed)
4. You can override with `signed=False/True`

**Q: What about rate limiting?**

A: Both APIs have rate limits:

- **Planetary Computer**: Generous limits for signed URLs
- **EarthSearch**: Standard HTTP rate limits

The package doesn't implement rate limiting - use your own if needed.

**Q: Can I cache results?**

A: Yes, several approaches:

```python
# 1. Export URLs to JSON
items.export_urls_json('cache.json')

# 2. Save DataFrames
df = items.to_dataframe()
df.to_parquet('metadata_cache.parquet')

# 3. Use your own caching layer
```

**Q: How do I handle different projections?**

A: The package provides URLs - projection handling is up to your raster library:

```python
import rioxarray
data = rioxarray.open_rasterio(url)
data_reprojected = data.rio.reproject('EPSG:4326')
```


### Troubleshooting Questions

**Q: Why am I getting "Asset not found" errors?**

A: Different providers use different asset names:

- **PC**: B01, B02, B03, B04...
- **EarthSearch**: coastal, blue, green, red...

Use `item.print_assets_info()` to see available assets.

**Q: Search returns no results but data should exist**

A: Common issues:

1. **Bbox order**: Use [west, south, east, north]
2. **Date format**: PC accepts "YYYY-MM-DD", ES prefers RFC3339
3. **Collection names**: Use `client.list_collections()` to verify
4. **Cloud cover**: Try relaxing the threshold

**Q: URLs work but data loading is slow**

A: Optimization strategies:

1. Use overview levels: `rioxarray.open_rasterio(url, overview_level=2)`
2. Enable chunking: `rioxarray.open_rasterio(url, chunks=True)`
3. Read smaller windows with rasterio
4. Consider geographic proximity to data

### Integration Questions

**Q: Can I use this with Jupyter notebooks?**

A: Yes! The package works great in Jupyter:

```python
# Display asset info
item.print_assets_info()

# Show DataFrames
df = items.to_dataframe()
display(df)

# Plot with matplotlib/cartopy
import matplotlib.pyplot as plt
data = rioxarray.open_rasterio(url)
data.plot()
```

**Q: How do I integrate with QGIS/ArcGIS?**

A: Export URLs and use them directly:

```python
# Get URLs
urls = item.get_all_asset_urls()

# In QGIS: Add Raster Layer -> use the URL directly
# In ArcGIS: Add Data -> Raster Dataset -> paste URL
```

**Q: Can I use this in production systems?**

A: Yes! The package is designed for production use:

- Robust error handling
- No forced dependencies
- Clean separation of concerns
- Comprehensive logging support

**Q: How do I contribute or report issues?**

A: Visit the GitHub repository:

- Report issues: GitHub Issues
- Contribute: Pull Requests welcome
- Documentation: Help improve this guide

---

This completes the comprehensive user guide for Open Geodata API. The package provides a clean, flexible foundation for accessing open geospatial data while letting you maintain full control over data processing and analysis workflows.

--- End ---

[^1]: https://developers.arcgis.com/python/latest/guide/tutorials/import-data/

[^2]: https://github.com/geopython/pygeoapi/blob/master/pygeoapi/openapi.py

[^3]: https://opencagedata.com/api

[^4]: https://opencagedata.com/tutorials/geocode-in-python

[^5]: https://guides.library.columbia.edu/geotools/Python

[^6]: https://pygeoapi.io

[^7]: https://live.osgeo.org/en/quickstart/pygeoapi_quickstart.html

[^8]: https://packaging.python.org

[^9]: [http://r-project.ro/conference2018/presentations/Tutorial_Spatial_Analysis_in_R_with_Open_Geodata_-_uRos2018.pdf](https://github.com/Mirjan-Ali-Sha/open-geodata-api/blob/main/Open%20Geodata%20API%20-%20Complete%20User%20Guide.pdf)

[^10]: https://geodata.readthedocs.io

