"""
Item management CLI commands with comprehensive help
"""
import click
import json
import open_geodata_api as ogapi


@click.group(name='items')
def items_group():
    """
    📄 Item information and asset management commands.
    
    Work with individual satellite data items (scenes/products).
    View metadata, list available assets/bands, and get direct URLs.
    
    \b
    Common workflows:
    1. Inspect item metadata and assets
    2. Get URLs for specific bands
    3. Check asset availability across items
    
    \b
    Examples:
      ogapi items info item_id              # Show item details
      ogapi items assets item_id            # List available assets
      ogapi items urls item_id -a "B04,B03" # Get band URLs
    
    \b
    Note: Most item operations work with search results.
    Use 'ogapi search items' first to find items of interest.
    """
    pass


@items_group.command('info')
@click.argument('search_results_file', type=click.Path(exists=True))
@click.option('--item-index', '-i',
              type=int,
              default=0,
              help='Index of item to show info for (default: 0, first item)')
@click.option('--item-id', '--id',
              help='Specific item ID to show info for (overrides --item-index)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save item info to JSON file')
@click.option('--show-all/--show-summary',
              default=False,
              help='Show all metadata vs summary only')
@click.pass_context
def item_info(ctx, search_results_file, item_index, item_id, output, show_all):
    """
    📄 Show detailed information about a specific item.
    
    Display comprehensive metadata for a satellite data item including:
    - Basic information (ID, collection, date, platform)
    - Geographic extent and projection
    - Processing details and quality metrics
    - Available assets and their properties
    
    \b
    Examples:
      # Show first item from search results:
      ogapi items info search_results.json
      
      # Show specific item by index:
      ogapi items info search_results.json --item-index 2
      
      # Show item by ID:
      ogapi items info search_results.json --item-id "S2A_MSIL2A_20240630..."
      
      # Show all metadata and save to file:
      ogapi items info search_results.json --show-all -o item_metadata.json
    
    \b
    Arguments:
    SEARCH_RESULTS_FILE  JSON file from 'ogapi search items' command
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load search results
        with open(search_results_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data:
            click.echo("❌ Invalid search results file")
            click.echo("💡 Use: ogapi search items ... -o results.json")
            return
        
        items_data = search_data['items']
        
        if not items_data:
            click.echo("❌ No items found in search results")
            return
        
        # Find target item
        target_item = None
        
        if item_id:
            # Find by ID
            for item in items_data:
                if item.get('id') == item_id:
                    target_item = item
                    break
            
            if not target_item:
                click.echo(f"❌ Item ID '{item_id}' not found in results")
                click.echo(f"💡 Available items:")
                for i, item in enumerate(items_data[:5]):
                    click.echo(f"   {i}: {item.get('id', 'unknown')}")
                return
        else:
            # Use index
            if item_index >= len(items_data):
                click.echo(f"❌ Item index {item_index} out of range")
                click.echo(f"💡 Available range: 0-{len(items_data)-1}")
                return
            
            target_item = items_data[item_index]
        
        # Create STAC item object
        provider = search_data.get('search_params', {}).get('provider', 'unknown')
        from open_geodata_api.core.items import STACItem
        item = STACItem(target_item, provider=provider)
        
        # Display information
        click.echo(f"📄 Item Information")
        click.echo("=" * 50)
        
        # Basic info
        click.echo(f"🆔 ID: {item.id}")
        click.echo(f"📁 Collection: {item.collection}")
        click.echo(f"🔗 Provider: {item.provider}")
        click.echo(f"🛰️ Platform: {item.properties.get('platform', item.properties.get('constellation', 'N/A'))}")
        
        # Date and time
        datetime_str = item.properties.get('datetime', 'N/A')
        if datetime_str != 'N/A':
            click.echo(f"📅 Date/Time: {datetime_str}")
        
        # Cloud cover
        cloud_cover = item.properties.get('eo:cloud_cover')
        if cloud_cover is not None:
            click.echo(f"☁️ Cloud Cover: {cloud_cover:.1f}%")
        
        # Processing info
        processing_level = item.properties.get('processing:level', item.properties.get('product_type'))
        if processing_level:
            click.echo(f"⚙️ Processing Level: {processing_level}")
        
        # Geometry info
        if item.bbox:
            click.echo(f"🗺️ Bounding Box: {item.bbox}")
        
        # Assets summary
        assets = item.list_assets()
        click.echo(f"🎯 Assets: {len(assets)} available")
        
        if not show_all:
            # Show first few assets
            display_assets = assets[:8]
            click.echo(f"   📊 Sample: {', '.join(display_assets)}")
            if len(assets) > 8:
                click.echo(f"   📊 ... and {len(assets)-8} more")
        else:
            # Show all assets with details
            click.echo(f"   📊 All assets:")
            for asset_key, asset in item.assets.items():
                click.echo(f"      {asset_key:12s} | {asset.type:20s} | {asset.title}")
        
        # Additional properties
        if show_all:
            click.echo(f"\n📋 All Properties:")
            for key, value in item.properties.items():
                if key not in ['datetime', 'eo:cloud_cover', 'platform', 'constellation', 'processing:level', 'product_type']:
                    click.echo(f"   {key}: {value}")
        
        # Save to file if requested
        if output:
            output_data = {
                'item_info': {
                    'id': item.id,
                    'collection': item.collection,
                    'provider': item.provider,
                    'assets_count': len(assets),
                    'assets_list': assets
                },
                'full_item': target_item
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\n💾 Item info saved to: {output}")
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        click.echo(f"   ogapi items assets {search_results_file} -i {item_index}")
        click.echo(f"   ogapi items urls {search_results_file} -i {item_index} -a \"B04,B03,B02\"")
        click.echo(f"   ogapi download search-results {search_results_file}")
    
    except Exception as e:
        click.echo(f"❌ Error showing item info: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@items_group.command('assets')
@click.argument('search_results_file', type=click.Path(exists=True))
@click.option('--item-index', '-i',
              type=int,
              default=0,
              help='Index of item to list assets for (default: 0)')
@click.option('--item-id', '--id',
              help='Specific item ID to list assets for')
@click.option('--pattern', '-p',
              help='Filter assets by pattern (case-insensitive substring match)')
@click.option('--type', '-t', 'asset_type',
              help='Filter assets by MIME type (e.g., "image/tiff")')
@click.option('--show-urls/--no-urls',
              default=False,
              help='Show asset URLs')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save asset list to JSON file')
@click.pass_context
def list_assets(ctx, search_results_file, item_index, item_id, pattern, asset_type, show_urls, output):
    """
    📊 List and filter assets/bands for a specific item.
    
    Display available assets (bands, thumbnails, metadata files) for a satellite data item.
    Useful for understanding what data is available before downloading.
    
    \b
    Examples:
      # List all assets for first item:
      ogapi items assets search_results.json
      
      # List assets for specific item:
      ogapi items assets search_results.json --item-id "S2A_MSIL2A..."
      
      # Filter by pattern:
      ogapi items assets search_results.json --pattern "B0"  # B01, B02, etc.
      
      # Filter by type:
      ogapi items assets search_results.json --type "image/tiff"
      
      # Show URLs for downloading:
      ogapi items assets search_results.json --show-urls
      
      # Save asset info:
      ogapi items assets search_results.json -o assets_info.json
    
    \b
    Asset Types:
    • image/tiff  - Raster data bands
    • image/jpeg  - Preview images  
    • text/xml    - Metadata files
    • application/json - STAC metadata
    
    \b
    Common Patterns:
    • "B0"     - Optical bands (B01, B02, ...)
    • "red"    - Red band (EarthSearch naming)
    • "thumb"  - Thumbnail images
    • "qa"     - Quality assessment bands
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load and validate search results
        with open(search_results_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data or not search_data['items']:
            click.echo("❌ No items found in search results file")
            return
        
        items_data = search_data['items']
        
        # Find target item
        target_item = None
        
        if item_id:
            for item in items_data:
                if item.get('id') == item_id:
                    target_item = item
                    break
            if not target_item:
                click.echo(f"❌ Item ID '{item_id}' not found")
                return
        else:
            if item_index >= len(items_data):
                click.echo(f"❌ Item index {item_index} out of range (0-{len(items_data)-1})")
                return
            target_item = items_data[item_index]
        
        # Create STAC item
        provider = search_data.get('search_params', {}).get('provider', 'unknown')
        from open_geodata_api.core.items import STACItem
        item = STACItem(target_item, provider=provider)
        
        click.echo(f"📊 Assets for item: {item.id}")
        click.echo(f"🔗 Provider: {item.provider}")
        
        # Get and filter assets
        all_assets = list(item.assets.items())
        filtered_assets = []
        
        for asset_key, asset in all_assets:
            # Apply filters
            if pattern and pattern.lower() not in asset_key.lower():
                continue
            
            if asset_type and asset.type != asset_type:
                continue
            
            filtered_assets.append((asset_key, asset))
        
        if not filtered_assets:
            click.echo("❌ No assets match the specified filters")
            click.echo(f"💡 Available assets: {', '.join([k for k, v in all_assets])}")
            return
        
        # Display results
        click.echo(f"\n📋 Found {len(filtered_assets)} assets:")
        
        # Table header
        if show_urls:
            click.echo(f"{'Asset':15s} | {'Type':25s} | {'Title':30s} | URL")
            click.echo("-" * 100)
        else:
            click.echo(f"{'Asset':15s} | {'Type':25s} | {'Title':50s}")
            click.echo("-" * 95)
        
        # Asset details
        asset_data = {}
        for asset_key, asset in filtered_assets:
            title = asset.title[:47] + "..." if len(asset.title) > 50 else asset.title
            
            if show_urls:
                try:
                    url = item.get_asset_url(asset_key)
                    display_url = url[:30] + "..." if len(url) > 30 else url
                    click.echo(f"{asset_key:15s} | {asset.type:25s} | {title:30s} | {display_url}")
                    asset_data[asset_key] = {
                        'type': asset.type,
                        'title': asset.title,
                        'url': url
                    }
                except Exception as e:
                    click.echo(f"{asset_key:15s} | {asset.type:25s} | {title:30s} | Error: {e}")
            else:
                click.echo(f"{asset_key:15s} | {asset.type:25s} | {title:50s}")
                asset_data[asset_key] = {
                    'type': asset.type,
                    'title': asset.title,
                    'href': asset.href
                }
        
        # Summary
        click.echo(f"\n📈 Asset Summary:")
        
        # Group by type
        type_counts = {}
        for _, asset in filtered_assets:
            asset_type = asset.type
            type_counts[asset_type] = type_counts.get(asset_type, 0) + 1
        
        for asset_type, count in type_counts.items():
            click.echo(f"   {asset_type}: {count} assets")
        
        # Save to file
        if output:
            output_data = {
                'item_id': item.id,
                'provider': item.provider,
                'filters_applied': {
                    'pattern': pattern,
                    'type': asset_type
                },
                'assets_found': len(filtered_assets),
                'assets': asset_data
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\n💾 Asset info saved to: {output}")
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        asset_names = [k for k, v in filtered_assets[:3]]
        click.echo(f"   ogapi items urls {search_results_file} -i {item_index} -a \"{','.join(asset_names)}\"")
        click.echo(f"   ogapi download search-results {search_results_file} -a \"{','.join(asset_names)}\"")
    
    except Exception as e:
        click.echo(f"❌ Error listing assets: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@items_group.command('urls')
@click.argument('search_results_file', type=click.Path(exists=True))
@click.option('--item-index', '-i',
              type=int,
              default=0,
              help='Index of item to get URLs for (default: 0)')
@click.option('--item-id', '--id',
              help='Specific item ID to get URLs for')
@click.option('--assets', '-a',
              help='Comma-separated list of specific assets (e.g., "B04,B03,B02")')
@click.option('--pattern', '-p',
              help='Get URLs for assets matching pattern')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save URLs to JSON file')
@click.option('--signed/--unsigned',
              default=True,
              help='Get signed URLs for Planetary Computer (default: signed)')
@click.option('--check-expiry/--no-check-expiry',
              default=True,
              help='Check if URLs are expired')
@click.pass_context
def get_urls(ctx, search_results_file, item_index, item_id, assets, pattern, output, signed, check_expiry):
    """
    🔗 Get download URLs for specific assets of an item.
    
    Retrieve ready-to-use URLs for satellite data assets. URLs are automatically
    signed for Planetary Computer and validated for EarthSearch.
    
    \b
    Examples:
      # Get URLs for RGB bands:
      ogapi items urls search_results.json -a "B04,B03,B02"
      
      # Get all URLs for an item:
      ogapi items urls search_results.json
      
      # Get URLs by pattern:
      ogapi items urls search_results.json --pattern "B0"
      
      # Save URLs for later download:
      ogapi items urls search_results.json -a "B08,B04" -o ndvi_urls.json
      
      # Get unsigned URLs:
      ogapi items urls search_results.json --unsigned
      
      # Check URL expiration:
      ogapi items urls search_results.json --check-expiry
    
    \b
    URL Types:
    • Planetary Computer: Automatically signed for immediate use
    • EarthSearch: Direct COG URLs (no signing needed)
    
    \b
    Common Asset Combinations:
    • RGB: "B04,B03,B02" (Red, Green, Blue)
    • NDVI: "B08,B04" (NIR, Red)  
    • All optical: "B02,B03,B04,B05,B06,B07,B08,B8A,B11,B12"
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load search results
        with open(search_results_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data or not search_data['items']:
            click.echo("❌ No items found in search results file")
            return
        
        items_data = search_data['items']
        
        # Find target item
        target_item = None
        display_index = item_index
        
        if item_id:
            for i, item in enumerate(items_data):
                if item.get('id') == item_id:
                    target_item = item
                    display_index = i
                    break
            if not target_item:
                click.echo(f"❌ Item ID '{item_id}' not found")
                return
        else:
            if item_index >= len(items_data):
                click.echo(f"❌ Item index {item_index} out of range (0-{len(items_data)-1})")
                return
            target_item = items_data[item_index]
        
        # Create STAC item
        provider = search_data.get('search_params', {}).get('provider', 'unknown')
        from open_geodata_api.core.items import STACItem
        item = STACItem(target_item, provider=provider)
        
        click.echo(f"🔗 Getting URLs for item: {item.id}")
        click.echo(f"📍 Provider: {item.provider}")
        
        # Determine which assets to get URLs for
        if assets:
            # Specific assets
            asset_list = [a.strip() for a in assets.split(',')]
            urls = item.get_band_urls(asset_list, signed=signed)
            click.echo(f"🎯 Requested assets: {', '.join(asset_list)}")
        elif pattern:
            # Pattern matching
            all_assets = item.list_assets()
            matching_assets = [a for a in all_assets if pattern.lower() in a.lower()]
            if not matching_assets:
                click.echo(f"❌ No assets match pattern '{pattern}'")
                click.echo(f"💡 Available: {', '.join(all_assets)}")
                return
            urls = item.get_band_urls(matching_assets, signed=signed)
            click.echo(f"🎯 Pattern '{pattern}' matched: {', '.join(matching_assets)}")
        else:
            # All assets
            urls = item.get_all_asset_urls(signed=signed)
            click.echo(f"🎯 Getting all {len(urls)} asset URLs")
        
        if not urls:
            click.echo("❌ No URLs retrieved")
            return
        
        # Check URL status if requested
        url_status = {}
        if check_expiry and provider == 'planetary_computer':
            from open_geodata_api.utils import is_url_expired, is_signed_url
            
            expired_count = 0
            for asset_key, url in urls.items():
                is_expired = is_url_expired(url) if is_signed_url(url) else False
                url_status[asset_key] = {
                    'signed': is_signed_url(url),
                    'expired': is_expired
                }
                if is_expired:
                    expired_count += 1
            
            if expired_count > 0:
                click.echo(f"⚠️ Warning: {expired_count} URLs are expired")
                click.echo("💡 Use download commands to auto-refresh expired URLs")
        
        # Display URLs
        click.echo(f"\n📋 Retrieved {len(urls)} URLs:")
        
        for asset_key, url in urls.items():
            status_info = ""
            if check_expiry and asset_key in url_status:
                status = url_status[asset_key]
                if status['expired']:
                    status_info = " [EXPIRED]"
                elif status['signed']:
                    status_info = " [SIGNED]"
            
            # Truncate long URLs for display
            display_url = url[:80] + "..." if len(url) > 80 else url
            click.echo(f"   {asset_key:12s}: {display_url}{status_info}")
        
        # Save to file
        if output:
            output_data = {
                'item_info': {
                    'id': item.id,
                    'provider': item.provider,
                    'index': display_index
                },
                'url_options': {
                    'signed': signed,
                    'assets_requested': assets,
                    'pattern_used': pattern
                },
                'urls': urls
            }
            
            if url_status:
                output_data['url_status'] = url_status
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            click.echo(f"\n💾 URLs saved to: {output}")
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        first_asset = list(urls.keys())[0]
        first_url = urls[first_asset]
        click.echo(f"   # Download single asset:")
        click.echo(f"   ogapi download url \"{first_url}\"")
        click.echo(f"   ")
        if output:
            click.echo(f"   # Download from saved URLs:")
            click.echo(f"   ogapi download urls-json {output}")
        else:
            click.echo(f"   # Download specific assets:")
            asset_names = list(urls.keys())[:3]
            click.echo(f"   ogapi download search-results {search_results_file} -a \"{','.join(asset_names)}\"")
    
    except Exception as e:
        click.echo(f"❌ Error getting URLs: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@items_group.command('compare')
@click.argument('search_results_file', type=click.Path(exists=True))
@click.option('--max-items', '-m',
              type=int,
              default=5,
              help='Maximum number of items to compare (default: 5)')
@click.option('--metric', '-mt',
              type=click.Choice(['cloud_cover', 'date', 'assets'], case_sensitive=False),
              default='cloud_cover',
              help='Comparison metric (default: cloud_cover)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save comparison to JSON file')
@click.pass_context
def compare_items(ctx, search_results_file, max_items, metric, output):
    """
    📊 Compare multiple items by quality metrics.
    
    Analyze and rank items from search results based on various criteria.
    Useful for selecting the best available data for your analysis.
    
    \b
    Examples:
      # Compare by cloud cover (find clearest):
      ogapi items compare search_results.json
      
      # Compare by date (find most recent):
      ogapi items compare search_results.json --metric date
      
      # Compare asset availability:
      ogapi items compare search_results.json --metric assets --max-items 10
      
      # Save comparison results:
      ogapi items compare search_results.json -o comparison.json
    
    \b
    Comparison Metrics:
    • cloud_cover: Rank by lowest cloud coverage
    • date: Rank by most recent acquisition
    • assets: Rank by number of available assets
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load search results
        with open(search_results_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data or not search_data['items']:
            click.echo("❌ No items found in search results file")
            return
        
        items_data = search_data['items'][:max_items]
        provider = search_data.get('search_params', {}).get('provider', 'unknown')
        
        click.echo(f"📊 Comparing {len(items_data)} items by {metric}")
        
        # Create STAC items and collect comparison data
        items_comparison = []
        
        for i, item_data in enumerate(items_data):
            from open_geodata_api.core.items import STACItem
            item = STACItem(item_data, provider=provider)
            
            comparison_entry = {
                'index': i,
                'id': item.id,
                'datetime': item.properties.get('datetime', ''),
                'cloud_cover': item.properties.get('eo:cloud_cover'),
                'assets_count': len(item.list_assets()),
                'platform': item.properties.get('platform', item.properties.get('constellation', 'Unknown'))
            }
            
            items_comparison.append(comparison_entry)
        
        # Sort by metric
        if metric == 'cloud_cover':
            # Sort by cloud cover (ascending - lower is better)
            items_comparison.sort(key=lambda x: x['cloud_cover'] if x['cloud_cover'] is not None else 999)
            click.echo("🏆 Ranked by cloud cover (lowest first):")
        elif metric == 'date':
            # Sort by date (descending - newer is better)
            items_comparison.sort(key=lambda x: x['datetime'], reverse=True)
            click.echo("🏆 Ranked by date (newest first):")
        elif metric == 'assets':
            # Sort by asset count (descending - more is better)
            items_comparison.sort(key=lambda x: x['assets_count'], reverse=True)
            click.echo("🏆 Ranked by asset count (most first):")
        
        # Display comparison table
        click.echo("\n" + "="*90)
        click.echo(f"{'Rank':4s} | {'ID':20s} | {'Date':12s} | {'Clouds':6s} | {'Assets':6s} | {'Platform':10s}")
        click.echo("="*90)
        
        for rank, item in enumerate(items_comparison, 1):
            item_id = item['id'][:18] + "..." if len(item['id']) > 20 else item['id']
            date_str = item['datetime'][:10] if item['datetime'] else 'N/A'
            cloud_str = f"{item['cloud_cover']:.1f}%" if item['cloud_cover'] is not None else 'N/A'
            
            click.echo(f"{rank:4d} | {item_id:20s} | {date_str:12s} | {cloud_str:6s} | {item['assets_count']:6d} | {item['platform']:10s}")
        
        # Highlight best item
        best_item = items_comparison[0]
        click.echo(f"\n🏆 Best item: {best_item['id']}")
        
        if metric == 'cloud_cover':
            click.echo(f"   ☁️ Cloud cover: {best_item['cloud_cover']:.1f}%")
        elif metric == 'date':
            click.echo(f"   📅 Date: {best_item['datetime']}")
        elif metric == 'assets':
            click.echo(f"   🎯 Assets: {best_item['assets_count']}")
        
        # Save comparison
        if output:
            comparison_data = {
                'comparison_metadata': {
                    'metric': metric,
                    'items_compared': len(items_comparison),
                    'source_file': search_results_file
                },
                'ranking': items_comparison,
                'best_item': best_item
            }
            
            with open(output, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            click.echo(f"\n💾 Comparison saved to: {output}")
        
        # Usage suggestions
        best_index = best_item['index']
        click.echo(f"\n💡 Work with best item:")
        click.echo(f"   ogapi items info {search_results_file} -i {best_index}")
        click.echo(f"   ogapi items urls {search_results_file} -i {best_index} -a \"B04,B03,B02\"")
        click.echo(f"   ogapi download search-results {search_results_file} --max-items 1")
    
    except Exception as e:
        click.echo(f"❌ Error comparing items: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()
