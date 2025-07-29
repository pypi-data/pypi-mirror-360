"""
Data processing utilities for open-geodata-api
"""

import json
import os
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from pathlib import Path


def export_urls_to_json(items, output_file: str, asset_keys: Optional[List[str]] = None,
                       signed: bool = True, include_metadata: bool = False,
                       **kwargs) -> Dict[str, Any]:
    """
    Export asset URLs to JSON file for external processing.
    
    Args:
        items: STAC items to export URLs from
        output_file: Output JSON file path
        asset_keys: Specific assets to export
        signed: Whether to use signed URLs
        include_metadata: Include item metadata
        **kwargs: Additional export options
    
    Returns:
        Export metadata
    """
    
    export_data = {
        'export_metadata': {
            'timestamp': datetime.now().isoformat(),
            'signed_urls': signed,
            'include_metadata': include_metadata,
            'total_items': len(items),
            'asset_keys': asset_keys
        },
        'items': {}
    }
    
    total_urls = 0
    
    for item in items:
        try:
            item_data = {
                'item_id': item.id,
                'collection': item.collection,
                'urls': {}
            }
            
            # Get URLs for specified assets
            if asset_keys:
                for asset_key in asset_keys:
                    try:
                        url = item.get_asset_url(asset_key, auto_sign=signed)
                        item_data['urls'][asset_key] = url
                        total_urls += 1
                    except Exception as e:
                        print(f"Warning: Could not get URL for {item.id}/{asset_key}: {e}")
            else:
                # Get all asset URLs
                all_urls = item.get_all_asset_urls(auto_sign=signed)
                item_data['urls'] = all_urls
                total_urls += len(all_urls)
            
            # Include metadata if requested
            if include_metadata:
                item_data['metadata'] = {
                    'datetime': item.properties.get('datetime'),
                    'cloud_cover': item.properties.get('eo:cloud_cover'),
                    'platform': item.properties.get('platform'),
                    'geometry': item.geometry if hasattr(item, 'geometry') else None,
                    'bbox': item.bbox if hasattr(item, 'bbox') else None
                }
            
            export_data['items'][item.id] = item_data
            
        except Exception as e:
            print(f"Warning: Failed to process item {item.id}: {e}")
    
    # Update export metadata
    export_data['export_metadata'].update({
        'total_urls': total_urls,
        'assets_per_item': len(asset_keys) if asset_keys else 'all',
        'successful_items': len(export_data['items'])
    })
    
    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    print(f"📤 Exported {total_urls} URLs from {len(export_data['items'])} items to {output_file}")
    
    return {
        'output_file': str(output_path),
        'total_items': len(export_data['items']),
        'total_urls': total_urls,
        'assets_per_item': len(asset_keys) if asset_keys else 'all'
    }
