"""
Intelligent download utilities for open-geodata-api
Handles various input formats and automatic URL management
"""
import os
import json
import requests
import time
from pathlib import Path
from typing import Union, Dict, List, Optional, Any
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta      
import re
from tqdm import tqdm


def is_url_expired(url: str) -> bool:
    """Check if a signed URL is expired by examining the 'se' parameter with 1 minute safe timer."""
    try:
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        if 'se' in query_params:
            expiry_time = query_params['se'][0]
            # Convert to timestamp and compare with current time
            expiry_dt = datetime.fromisoformat(expiry_time.replace('Z', '+00:00'))
            current_dt = datetime.now(expiry_dt.tzinfo)
            
            # Declare expired if current time is >= expiry time minus 1 minute (safe timer)
            safe_expiry_dt = expiry_dt - timedelta(seconds=30)
            return current_dt >= safe_expiry_dt
        
        return False  # If no expiry parameter, assume not expired
    except Exception:
        return False



def is_signed_url(url: str) -> bool:
    """Check if URL is already signed (has signature parameters)."""
    return 'sig=' in url or 'signature=' in url


def extract_filename_from_url(url: str) -> str:
    """Extract original filename from URL."""
    try:
        # Remove query parameters first
        clean_url = url.split('?')[0]
        # Get the last part of the path
        filename = os.path.basename(clean_url)
        
        # If no extension, try to extract from the path
        if '.' not in filename:
            path_parts = clean_url.split('/')
            for part in reversed(path_parts):
                if '.' in part:
                    filename = part
                    break
        
        return filename or "downloaded_file"
    except Exception:
        return "downloaded_file"


def re_sign_url_if_needed(url: str, provider: str = "planetary_computer") -> str:
    """Re-sign URL if it's expired and needs signing."""
    try:
        if provider == "planetary_computer" and is_signed_url(url):
            if is_url_expired(url):
                print(f"⚠️  URL expired, attempting to re-sign...")
                # Remove existing signature parameters
                clean_url = url.split('?')[0]
                
                try:
                    from ..planetary.signing import sign_url
                    new_url = sign_url(clean_url)
                    print(f"✅ URL successfully re-signed")
                    return new_url
                except Exception as e:
                    print(f"❌ Failed to re-sign URL: {e}")
                    print(f"🔄 Attempting download with original URL...")
                    return url
        
        return url
    except Exception:
        return url


def download_single_file(url: str, destination: Optional[str] = None, 
                        provider: str = "unknown", chunk_size: int = 8192,
                        show_progress: bool = True) -> str:
    """
    Download a single file from URL.
    
    Parameters:
    -----------
    url : str
        URL to download from
    destination : str, optional
        Destination path (file or directory)
    provider : str
        Provider name for URL handling
    chunk_size : int
        Download chunk size in bytes
    show_progress : bool
        Show download progress bar
        
    Returns:
    --------
    str : Path to downloaded file
    """
    
    # Handle URL signing/validation
    url = re_sign_url_if_needed(url, provider)
    
    # Determine destination
    if destination is None:
        # Download to current directory with original name
        filename = extract_filename_from_url(url)
        destination = Path.cwd() / filename
    else:
        dest_path = Path(destination)
        if dest_path.is_dir() or not dest_path.suffix:
            # Destination is a directory
            filename = extract_filename_from_url(url)
            destination = dest_path / filename
        # else: destination already includes filename
    
    # Create parent directory if needed
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    
    # Download the file
    try:
        print(f"📥 Downloading: {extract_filename_from_url(url)}")
        print(f"📍 To: {destination}")
        
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f:
            if show_progress and total_size > 0:
                with tqdm(total=total_size, unit='B', unit_scale=True, 
                         desc=destination.name) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))
            else:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
        
        print(f"✅ Downloaded: {destination}")
        return str(destination)
        
    except Exception as e:
        print(f"❌ Download failed: {e}")
        # Clean up partial file
        if destination.exists():
            destination.unlink()
        raise


def download_url_dict(urls_dict: Dict[str, str], base_destination: Optional[str] = None,
                      provider: str = "unknown", create_subfolders: bool = True) -> Dict[str, str]:
    """
    Download multiple files from URL dictionary.
    
    Parameters:
    -----------
    urls_dict : dict
        Dictionary of {asset_key: url}
    base_destination : str, optional
        Base destination directory
    provider : str
        Provider name for URL handling
    create_subfolders : bool
        Create subfolders for organization
        
    Returns:
    --------
    dict : {asset_key: downloaded_path}
    """
    
    base_path = Path(base_destination) if base_destination else Path.cwd()
    downloaded_files = {}
    
    print(f"📦 Downloading {len(urls_dict)} files...")
    
    for asset_key, url in urls_dict.items():
        try:
            if create_subfolders:
                asset_dir = base_path / "assets" / asset_key
            else:
                asset_dir = base_path
            
            downloaded_path = download_single_file(
                url, asset_dir, provider, show_progress=True
            )
            downloaded_files[asset_key] = downloaded_path
            
        except Exception as e:
            print(f"❌ Failed to download {asset_key}: {e}")
            downloaded_files[asset_key] = None
    
    successful = sum(1 for v in downloaded_files.values() if v is not None)
    print(f"✅ Downloaded {successful}/{len(urls_dict)} files successfully")
    
    return downloaded_files


def download_items(items, base_destination: Optional[str] = None, 
                  asset_keys: Optional[List[str]] = None,
                  create_product_folders: bool = True) -> Dict[str, Dict[str, str]]:
    """
    Download files from STAC items with intelligent folder structure.
    
    Parameters:
    -----------
    items : STACItemCollection or list of STACItem
        Items to download from
    base_destination : str, optional
        Base destination directory
    asset_keys : list, optional
        Specific assets to download (downloads all if None)
    create_product_folders : bool
        Create folders for each product
        
    Returns:
    --------
    dict : {item_id: {asset_key: downloaded_path}}
    """
    
    base_path = Path(base_destination) if base_destination else Path.cwd()
    all_downloads = {}
    
    # Handle different input types
    if hasattr(items, '__iter__') and not isinstance(items, (str, dict)):
        items_list = list(items)
    else:
        items_list = [items]
    
    print(f"📦 Downloading from {len(items_list)} items...")
    
    for item in items_list:
        try:
            # Get item ID and available assets
            item_id = getattr(item, 'id', f"item_{hash(str(item))}")
            
            # Create product folder
            if create_product_folders:
                item_dir = base_path / item_id
            else:
                item_dir = base_path
            
            # Get URLs for specified assets or all assets
            if asset_keys:
                urls = item.get_band_urls(asset_keys)
            else:
                urls = item.get_all_asset_urls()
            
            print(f"📂 Processing item: {item_id} ({len(urls)} assets)")
            
            # Download all assets for this item
            item_downloads = download_url_dict(
                urls, item_dir, getattr(item, 'provider', 'unknown'), 
                create_subfolders=False
            )
            
            all_downloads[item_id] = item_downloads
            
        except Exception as e:
            print(f"❌ Failed to process item {getattr(item, 'id', 'unknown')}: {e}")
            all_downloads[getattr(item, 'id', 'unknown')] = {}
    
    return all_downloads


def download_seasonal_data(seasonal_data: Dict[str, Any], 
                          base_destination: Optional[str] = None,
                          seasons: Optional[List[str]] = None,
                          asset_keys: Optional[List[str]] = None) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Download seasonal data structure.
    
    Parameters:
    -----------
    seasonal_data : dict
        Seasonal data structure like {season: {count, date_range, urls: {item_id: {asset: url}}}}
    base_destination : str, optional
        Base destination directory
    seasons : list, optional
        Specific seasons to download
    asset_keys : list, optional
        Specific assets to download
        
    Returns:
    --------
    dict : {season: {item_id: {asset_key: downloaded_path}}}
    """
    
    base_path = Path(base_destination) if base_destination else Path.cwd()
    all_downloads = {}
    
    # Filter seasons if specified
    seasons_to_process = seasons if seasons else list(seasonal_data.keys())
    
    print(f"📅 Processing {len(seasons_to_process)} seasons...")
    
    for season in seasons_to_process:
        if season not in seasonal_data:
            print(f"⚠️  Season '{season}' not found in data")
            continue
        
        season_data = seasonal_data[season]
        season_urls = season_data.get('urls', {})
        
        print(f"🌱 Processing season: {season} ({len(season_urls)} items)")
        
        # Create season folder
        season_dir = base_path / season
        season_downloads = {}
        
        for item_id, item_urls in season_urls.items():
            try:
                # Filter assets if specified
                if asset_keys:
                    filtered_urls = {k: v for k, v in item_urls.items() if k in asset_keys}
                else:
                    filtered_urls = item_urls
                
                # Create item folder within season
                item_dir = season_dir / item_id
                
                print(f"📂 Processing item: {item_id} ({len(filtered_urls)} assets)")
                
                # Download all assets for this item
                item_downloads = download_url_dict(
                    filtered_urls, item_dir, "planetary_computer", 
                    create_subfolders=False
                )
                
                season_downloads[item_id] = item_downloads
                
            except Exception as e:
                print(f"❌ Failed to process item {item_id}: {e}")
                season_downloads[item_id] = {}
        
        all_downloads[season] = season_downloads
    
    return all_downloads


def download_datasets(data: Union[str, Dict, Any], 
                     destination: Optional[str] = None,
                     **kwargs) -> Union[str, Dict]:
    """
    Universal download function that intelligently handles various input types.
    
    Parameters:
    -----------
    data : str, dict, STACItem, STACItemCollection, or seasonal data
        Data to download
    destination : str, optional
        Destination path
    **kwargs : additional arguments
        - asset_keys: list of specific assets to download
        - seasons: list of specific seasons (for seasonal data)
        - provider: provider name for URL handling
        - create_folders: bool, create organized folder structure
        
    Returns:
    --------
    str or dict : Downloaded file path(s) or download results
    """
    
    # Extract common parameters
    asset_keys = kwargs.get('asset_keys', None)
    seasons = kwargs.get('seasons', None)
    provider = kwargs.get('provider', 'unknown')
    create_folders = kwargs.get('create_folders', True)
    
    print(f"🚀 Starting intelligent download...")
    
    # Handle different input types
    if isinstance(data, str):
        # Single URL
        if data.startswith(('http://', 'https://')):
            print("📄 Detected: Single URL")
            return download_single_file(data, destination, provider)
        
        # JSON file path
        elif data.endswith('.json'):
            print("📋 Detected: JSON file")
            with open(data, 'r') as f:
                json_data = json.load(f)
            return download_datasets(json_data, destination, **kwargs)
        
        else:
            raise ValueError(f"Invalid string input: {data}")
    
    elif isinstance(data, dict):
        # Check if it's seasonal data structure
        if any(isinstance(v, dict) and 'urls' in v for v in data.values()):
            print("🌱 Detected: Seasonal data structure")
            return download_seasonal_data(data, destination, seasons, asset_keys)
        
        # Check if it's a simple URL dictionary
        elif all(isinstance(v, str) and v.startswith(('http://', 'https://')) for v in data.values()):
            print("🔗 Detected: URL dictionary")
            return download_url_dict(data, destination, provider, create_folders)
        
        # Check if it's nested items structure {item_id: {asset: url}}
        elif all(isinstance(v, dict) for v in data.values()):
            print("📦 Detected: Items URL structure")
            all_downloads = {}
            base_path = Path(destination) if destination else Path.cwd()
            
            for item_id, item_urls in data.items():
                item_dir = base_path / item_id if create_folders else base_path
                item_downloads = download_url_dict(item_urls, item_dir, provider, False)
                all_downloads[item_id] = item_downloads
            
            return all_downloads
        
        else:
            raise ValueError("Unknown dictionary structure")
    
    # Handle STAC objects
    elif hasattr(data, 'get_all_asset_urls'):
        # Single STACItem
        print("🛰️  Detected: Single STAC Item")
        item_id = getattr(data, 'id', 'stac_item')
        provider = getattr(data, 'provider', 'unknown')
        
        if asset_keys:
            urls = data.get_band_urls(asset_keys)
        else:
            urls = data.get_all_asset_urls()
        
        item_dir = Path(destination) / item_id if destination and create_folders else destination
        return download_url_dict(urls, item_dir, provider, False)
    
    elif hasattr(data, '__iter__') and hasattr(data, '__getitem__'):
        # STACItemCollection or list of items
        print("📦 Detected: STAC Item Collection")
        return download_items(data, destination, asset_keys, create_folders)
    
    else:
        raise ValueError(f"Unsupported data type: {type(data)}")


# Convenience functions
def download_url(url: str, destination: Optional[str] = None, provider: str = "unknown") -> str:
    """Download single URL - convenience function."""
    return download_single_file(url, destination, provider)


def download_from_json(json_path: str, destination: Optional[str] = None, **kwargs) -> Dict:
    """Download from JSON file - convenience function."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return download_datasets(data, destination, **kwargs)


def download_seasonal(seasonal_data: Dict, destination: Optional[str] = None,
                     seasons: Optional[List[str]] = None, 
                     bands: Optional[List[str]] = None) -> Dict:
    """Download seasonal data - convenience function."""
    return download_seasonal_data(seasonal_data, destination, seasons, bands)


# Export summary function
def create_download_summary(download_results: Dict, output_file: Optional[str] = None) -> Dict:
    """
    Create a summary of download results.
    
    Parameters:
    -----------
    download_results : dict
        Results from download functions
    output_file : str, optional
        Path to save summary JSON
        
    Returns:
    --------
    dict : Download summary
    """
    
    def count_files(data, level=0):
        """Recursively count files in nested structure."""
        if isinstance(data, dict):
            total = 0
            successful = 0
            for v in data.values():
                if isinstance(v, dict):
                    t, s = count_files(v, level + 1)
                    total += t
                    successful += s
                elif isinstance(v, str) and v is not None:
                    total += 1
                    successful += 1
                elif v is None:
                    total += 1
            return total, successful
        return 0, 0
    
    total_files, successful_files = count_files(download_results)
    
    summary = {
        'total_files': total_files,
        'successful_downloads': successful_files,
        'failed_downloads': total_files - successful_files,
        'success_rate': f"{(successful_files/total_files*100):.1f}%" if total_files > 0 else "0%",
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'results': download_results
    }
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"📊 Download summary saved to: {output_file}")
    
    return summary
