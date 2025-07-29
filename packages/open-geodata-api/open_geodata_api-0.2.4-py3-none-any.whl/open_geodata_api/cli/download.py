"""
Download CLI commands with comprehensive help
"""
import click
import json
from pathlib import Path
import open_geodata_api as ogapi
from open_geodata_api.utils import download_datasets, download_url, download_from_json


@click.group(name='download')
def download_group():
    """
    📥 Download satellite data and assets from various sources.
    
    Intelligent download system with automatic URL management, progress tracking,
    and support for multiple input formats. Handles expired URL re-signing automatically.
    
    \b
    Download Sources:
    • Single URLs (direct file download)
    • Search results (from search commands)
    • URL dictionaries (exported URLs)
    • Seasonal data (temporal analysis datasets)
    
    \b
    Common workflows:
    1. Search for data, then download results
    2. Export URLs, then download from URLs file
    3. Download specific assets/bands only
    4. Batch download with filtering
    
    \b
    Examples:
      ogapi download url "https://example.com/file.tif"     # Single file
      ogapi download search-results results.json           # From search
      ogapi download urls-json urls.json                   # From URLs file
    """
    pass


@download_group.command('url')
@click.argument('url')
@click.option('--destination', '-d',
              type=click.Path(),
              help='Destination file path or directory (auto-names if directory)')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es', 'auto'], case_sensitive=False),
              default='auto',
              help='Provider for URL handling (pc=Planetary Computer, es=EarthSearch, auto=detect)')
@click.option('--check-expiry/--no-check-expiry',
              default=True,
              help='Check and re-sign expired URLs automatically')
@click.pass_context
def download_single_url(ctx, url, destination, provider, check_expiry):
    """
    📁 Download a single file from URL.
    
    Downloads a single satellite data file with automatic URL management.
    Supports Planetary Computer signed URLs and EarthSearch direct URLs.
    
    \b
    Examples:
      # Download to current directory with original name:
      ogapi download url "https://example.com/B04.tif"
      
      # Download to specific directory:
      ogapi download url "https://example.com/B04.tif" -d "./data/"
      
      # Download with custom filename:
      ogapi download url "https://example.com/B04.tif" -d "./data/red_band.tif"
      
      # Download with provider specification:
      ogapi download url "https://pc.example.com/B04.tif" -p pc
      
      # Skip expiry check for speed:
      ogapi download url "https://example.com/B04.tif" --no-check-expiry
    
    \b
    URL Requirements:
    • Must be a valid HTTP/HTTPS URL
    • Should point to a downloadable file
    • Planetary Computer URLs will be automatically signed if expired
    
    \b
    Destination Options:
    • No destination: Downloads to current directory with original name
    • Directory path: Downloads to directory with original name
    • File path: Downloads with specified filename
    
    URL: Direct URL to the file to download
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        if verbose:
            click.echo(f"📥 Preparing to download: {url}")
            click.echo(f"🔗 Provider: {provider}")
            if destination:
                click.echo(f"📍 Destination: {destination}")
            else:
                click.echo(f"📍 Destination: Current directory (auto-named)")
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            click.echo("❌ Invalid URL: Must start with http:// or https://")
            return
        
        # Check expiry if requested
        if check_expiry and provider in ['pc', 'auto']:
            from open_geodata_api.utils import is_url_expired, is_signed_url, re_sign_url_if_needed
            
            if is_signed_url(url) and is_url_expired(url):
                click.echo("⚠️ URL appears to be expired, attempting to re-sign...")
                url = re_sign_url_if_needed(url, provider='planetary_computer')
        
        click.echo(f"📥 Starting download...")
        downloaded_path = download_url(url, destination, provider)
        click.echo(f"✅ Download completed: {downloaded_path}")
        
        # Show file info
        try:
            file_path = Path(downloaded_path)
            file_size = file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            click.echo(f"📊 File size: {size_mb:.2f} MB")
        except:
            pass
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        click.echo(f"   # View with rioxarray:")
        click.echo(f"   import rioxarray; data = rioxarray.open_rasterio('{downloaded_path}')")
        click.echo(f"   # Or with rasterio:")
        click.echo(f"   import rasterio; data = rasterio.open('{downloaded_path}')")
    
    except Exception as e:
        click.echo(f"❌ Download failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        click.echo(f"\n💡 Troubleshooting:")
        click.echo(f"   • Check URL accessibility")
        click.echo(f"   • Verify internet connection")
        click.echo(f"   • Try different provider: --provider pc/es")
        click.echo(f"   • Check destination permissions")
        raise click.Abort()


@download_group.command('search-results')
@click.argument('search_json_file', type=click.Path(exists=True))
@click.option('--destination', '-d',
              type=click.Path(),
              default='./downloads/',
              help='Destination directory for downloads')
@click.option('--assets', '-a',
              help='Comma-separated list of assets to download (e.g., "B04,B03,B02")')
@click.option('--max-items', '-m',
              type=int,
              help='Maximum number of items to download (for testing/limiting)')
@click.option('--cloud-cover', '-cc',
              type=float,
              help='Maximum cloud cover percentage for additional filtering')
@click.option('--create-folders/--flat-structure',
              default=True,
              help='Create organized folder structure vs flat download')
@click.option('--resume/--no-resume',
              default=True,
              help='Resume interrupted downloads (skip existing files)')
@click.pass_context
def download_search_results(ctx, search_json_file, destination, assets, max_items, cloud_cover, create_folders, resume):
    """
    📦 Download assets from search results JSON file.
    
    Downloads satellite data from saved search results with intelligent organization
    and filtering options. Supports partial downloads and resuming interrupted transfers.
    
    \b
    Examples:
      # Download all assets from search results:
      ogapi download search-results search_results.json
      
      # Download specific bands only:
      ogapi download search-results results.json -a "B04,B03,B02"
      
      # Download with cloud filtering:
      ogapi download search-results results.json --cloud-cover 20
      
      # Limit download for testing:
      ogapi download search-results results.json --max-items 3
      
      # Custom destination with flat structure:
      ogapi download search-results results.json -d "./rgb_data/" --flat-structure
      
      # Resume interrupted download:
      ogapi download search-results results.json --resume
    
    \b
    Organization Options:
    --create-folders    Create folders: destination/item_id/asset_files
    --flat-structure   All files in one folder: destination/all_files
    
    \b
    Filtering Options:
    --assets           Download only specific bands/assets
    --max-items        Limit number of items (useful for testing)
    --cloud-cover      Additional cloud filtering beyond search results
    
    \b
    Performance Tips:
    • Use specific assets (-a) to download only what you need
    • Set max-items for testing before full download
    • Use resume flag for large downloads
    
    SEARCH_JSON_FILE: JSON file from 'ogapi search items' command
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load and validate search results
        with open(search_json_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data:
            click.echo("❌ Invalid search results file")
            click.echo("💡 Expected format from: ogapi search items ... -o results.json")
            return
        
        items_data = search_data['items']
        
        if not items_data:
            click.echo("❌ No items found in search results")
            return
        
        if verbose:
            click.echo(f"📦 Processing {len(items_data)} items from search results")
            click.echo(f"📁 Source: {search_json_file}")
        
        # Create STACItemCollection from JSON data
        provider = search_data.get('search_params', {}).get('provider', 'pc')
        from open_geodata_api.core.collections import STACItemCollection
        items = STACItemCollection(items_data, provider=provider)
        
        original_count = len(items)
        
        # Apply cloud cover filter if specified
        if cloud_cover is not None:
            from open_geodata_api.utils import filter_by_cloud_cover
            items = filter_by_cloud_cover(items, max_cloud_cover=cloud_cover)
            if verbose:
                click.echo(f"☁️ Filtered to {len(items)} items with <{cloud_cover}% clouds")
            
            if len(items) == 0:
                click.echo(f"❌ No items remain after cloud filtering (<{cloud_cover}%)")
                click.echo(f"💡 Try higher cloud cover threshold")
                return
        
        # Limit items if specified
        if max_items:
            items = items[:max_items]
            if verbose:
                click.echo(f"🔢 Limited to first {len(items)} items")
        
        # Parse assets list
        asset_list = None
        if assets:
            asset_list = [a.strip() for a in assets.split(',')]
            if verbose:
                click.echo(f"🎯 Downloading assets: {', '.join(asset_list)}")
        
        # Show download plan
        total_items = len(items)
        click.echo(f"\n📋 Download Plan:")
        click.echo(f"   Items to download: {total_items}")
        if cloud_cover:
            click.echo(f"   Original items: {original_count} (filtered by clouds)")
        click.echo(f"   Provider: {provider.upper()}")
        click.echo(f"   Destination: {destination}")
        click.echo(f"   Folder structure: {'Organized' if create_folders else 'Flat'}")
        
        if asset_list:
            click.echo(f"   Assets: {', '.join(asset_list)}")
        else:
            # Estimate total assets
            sample_item = items[0]
            estimated_assets = len(sample_item.list_assets())
            estimated_total = total_items * estimated_assets
            click.echo(f"   Estimated files: ~{estimated_total} (all assets)")
        
        # Confirm for large downloads
        if total_items > 10:
            if not click.confirm(f"\n⚠️ Download {total_items} items? This may take significant time."):
                click.echo("Download cancelled")
                return
        
        # Download
        click.echo(f"\n📥 Starting download to: {destination}")
        results = download_datasets(
            items,
            destination=destination,
            asset_keys=asset_list,
            create_folders=create_folders
        )
        
        # Summary
        successful = sum(1 for item_results in results.values() 
                        for path in item_results.values() if path is not None)
        total = sum(len(item_results) for item_results in results.values())
        
        click.echo(f"\n✅ Download completed!")
        click.echo(f"   📊 Success: {successful}/{total} files")
        click.echo(f"   📁 Location: {destination}")
        
        if successful < total:
            failed = total - successful
            click.echo(f"   ⚠️ Failed: {failed} files")
            click.echo(f"   💡 Check verbose mode for details: --verbose")
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        click.echo(f"   # Explore downloads:")
        click.echo(f"   ls -la {destination}")
        click.echo(f"   # Create download summary:")
        click.echo(f"   ogapi utils download-summary results.json")
    
    except Exception as e:
        click.echo(f"❌ Download failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@download_group.command('urls-json')
@click.argument('urls_json_file', type=click.Path(exists=True))
@click.option('--destination', '-d',
              type=click.Path(),
              default='./downloads/',
              help='Destination directory for downloads')
@click.option('--create-folders/--flat-structure',
              default=True,
              help='Create organized folder structure')
@click.pass_context
def download_urls_json(ctx, urls_json_file, destination, create_folders):
    """
    🔗 Download files from URLs JSON file.
    
    Downloads files from a JSON file containing URLs, typically exported
    from search results or created manually. Supports various JSON formats.
    
    \b
    Examples:
      # Download from exported URLs:
      ogapi download urls-json exported_urls.json
      
      # Custom destination:
      ogapi download urls-json urls.json -d "./satellite_data/"
      
      # Flat file structure:
      ogapi download urls-json urls.json --flat-structure
    
    \b
    Supported JSON Formats:
    1. From export command: {"metadata": {...}, "urls": {...}}
    2. Simple URLs: {"item1": {"B04": "url1", "B03": "url2"}}
    3. Nested structure: {"urls": {"item1": {"asset": "url"}}}
    
    \b
    Organization:
    --create-folders   destination/item_id/asset_files
    --flat-structure   destination/all_files_together
    
    URLS_JSON_FILE: JSON file containing URLs to download
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        if verbose:
            click.echo(f"📋 Loading URLs from: {urls_json_file}")
        
        # Validate file and show preview
        with open(urls_json_file, 'r') as f:
            data = json.load(f)
        
        # Extract URLs based on format
        if 'urls' in data and isinstance(data['urls'], dict):
            urls = data['urls']
            metadata = data.get('metadata', {})
            if verbose and metadata:
                click.echo(f"📊 Source: {metadata.get('source_file', 'unknown')}")
                click.echo(f"🔗 Provider: {metadata.get('provider', 'unknown')}")
        else:
            urls = data
        
        # Count URLs
        total_urls = 0
        for item_urls in urls.values():
            if isinstance(item_urls, dict):
                total_urls += len(item_urls)
            else:
                total_urls += 1
        
        click.echo(f"📋 Found {len(urls)} items with {total_urls} total URLs")
        
        # Confirm for large downloads
        if total_urls > 20:
            if not click.confirm(f"⚠️ Download {total_urls} files? This may take time."):
                click.echo("Download cancelled")
                return
        
        click.echo(f"📥 Starting download to: {destination}")
        results = download_from_json(urls_json_file, destination)
        
        # Count results
        if isinstance(results, dict):
            successful = sum(1 for item_results in results.values()
                           if isinstance(item_results, dict)
                           for path in item_results.values() if path is not None)
            click.echo(f"✅ Download completed: {successful} files processed")
        else:
            click.echo("✅ Download completed")
        
        click.echo(f"📁 Files saved to: {destination}")
    
    except Exception as e:
        click.echo(f"❌ Download failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@download_group.command('seasonal')
@click.argument('seasonal_json_file', type=click.Path(exists=True))
@click.option('--destination', '-d',
              type=click.Path(),
              default='./seasonal_downloads/',
              help='Destination directory for seasonal data')
@click.option('--seasons', '-s',
              help='Comma-separated list of seasons to download (e.g., "spring,summer")')
@click.option('--assets', '-a',
              help='Comma-separated list of assets to download (e.g., "B08,B04")')
@click.option('--create-folders/--flat-structure',
              default=True,
              help='Create seasonal folder organization')
@click.pass_context
def download_seasonal(ctx, seasonal_json_file, destination, seasons, assets, create_folders):
    """
    🌱 Download seasonal data from JSON file.
    
    Downloads temporal datasets organized by seasons for time-series analysis.
    Creates organized folder structure by season and item.
    
    \b
    Examples:
      # Download all seasons:
      ogapi download seasonal seasonal_data.json
      
      # Download specific seasons:
      ogapi download seasonal data.json -s "spring,summer"
      
      # Download NDVI bands only:
      ogapi download seasonal data.json -a "B08,B04"
      
      # Custom destination:
      ogapi download seasonal data.json -d "./time_series_analysis/"
    
    \b
    Expected JSON Format:
    {
      "spring_2024": {
        "count": 50,
        "date_range": "2024-03-01/2024-05-31",
        "urls": {
          "item1": {"B08": "url1", "B04": "url2"},
          "item2": {"B08": "url3", "B04": "url4"}
        }
      }
    }
    
    \b
    Organization Structure:
    destination/
    ├── spring_2024/
    │   ├── item1/
    │   │   ├── B08.tif
    │   │   └── B04.tif
    │   └── item2/
    └── summer_2024/
    
    \b
    Use Cases:
    • Vegetation phenology studies
    • Change detection analysis
    • Climate monitoring
    • Agricultural assessment
    
    SEASONAL_JSON_FILE: JSON file containing seasonal data structure
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load and validate seasonal data
        with open(seasonal_json_file, 'r') as f:
            seasonal_data = json.load(f)
        
        # Validate format
        if not isinstance(seasonal_data, dict):
            click.echo("❌ Invalid seasonal data format")
            click.echo("💡 Expected: {season: {urls: {item: {asset: url}}}}")
            return
        
        available_seasons = list(seasonal_data.keys())
        
        if not available_seasons:
            click.echo("❌ No seasons found in data file")
            return
        
        # Parse seasons list
        seasons_list = None
        if seasons:
            seasons_list = [s.strip() for s in seasons.split(',')]
            # Validate requested seasons
            invalid_seasons = [s for s in seasons_list if s not in available_seasons]
            if invalid_seasons:
                click.echo(f"❌ Invalid seasons: {invalid_seasons}")
                click.echo(f"💡 Available: {available_seasons}")
                return
            if verbose:
                click.echo(f"🌱 Downloading seasons: {', '.join(seasons_list)}")
        else:
            seasons_list = available_seasons
            if verbose:
                click.echo(f"🌱 Downloading all seasons: {', '.join(seasons_list)}")
        
        # Parse assets list
        asset_list = None
        if assets:
            asset_list = [a.strip() for a in assets.split(',')]
            if verbose:
                click.echo(f"🎯 Downloading assets: {', '.join(asset_list)}")
        
        # Count total files
        total_files = 0
        for season in seasons_list:
            season_data = seasonal_data.get(season, {})
            season_urls = season_data.get('urls', {})
            
            for item_urls in season_urls.values():
                if asset_list:
                    total_files += len([a for a in asset_list if a in item_urls])
                else:
                    total_files += len(item_urls)
        
        click.echo(f"\n📋 Seasonal Download Plan:")
        click.echo(f"   Seasons: {len(seasons_list)} ({', '.join(seasons_list)})")
        click.echo(f"   Estimated files: {total_files}")
        click.echo(f"   Destination: {destination}")
        
        # Confirm large downloads
        if total_files > 50:
            if not click.confirm(f"⚠️ Download {total_files} files? This may take significant time."):
                click.echo("Download cancelled")
                return
        
        click.echo(f"\n🌱 Starting seasonal download...")
        from open_geodata_api.utils import download_seasonal_data
        results = download_seasonal_data(
            seasonal_data,
            base_destination=destination,
            seasons=seasons_list,
            asset_keys=asset_list
        )
        
        # Summary
        total_downloaded = 0
        for season_results in results.values():
            for item_results in season_results.values():
                total_downloaded += sum(1 for path in item_results.values() if path)
        
        click.echo(f"\n✅ Seasonal download completed!")
        click.echo(f"   📊 Files downloaded: {total_downloaded}")
        click.echo(f"   📁 Location: {destination}")
        click.echo(f"   🌱 Seasons: {len(results)} folders created")
        
        # Show structure
        click.echo(f"\n📂 Folder structure:")
        for season in sorted(results.keys()):
            click.echo(f"   {destination}/{season}/ ({len(results[season])} items)")
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        click.echo(f"   # Explore structure:")
        click.echo(f"   find {destination} -name '*.tif' | head -10")
        click.echo(f"   # Time series analysis:")
        click.echo(f"   # Use seasonal folders for temporal analysis")
        
    except Exception as e:
        click.echo(f"❌ Seasonal download failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@download_group.command('batch')
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--dry-run/--execute',
              default=False,
              help='Show what would be downloaded without actually downloading')
@click.pass_context
def download_batch(ctx, config_file, dry_run):
    """
    📋 Download from batch configuration file.
    
    Downloads multiple datasets based on a configuration file that can specify
    different sources, destinations, and filters for each download task.
    
    \b
    Example Config File (batch_config.json):
    {
      "downloads": [
        {
          "source": "search_results.json",
          "type": "search-results",
          "destination": "./rgb_data/",
          "assets": ["B04", "B03", "B02"],
          "max_items": 5
        },
        {
          "source": "urls.json", 
          "type": "urls-json",
          "destination": "./analysis_data/"
        }
      ]
    }
    
    \b
    Examples:
      # Test batch configuration:
      ogapi download batch config.json --dry-run
      
      # Execute batch download:
      ogapi download batch config.json
    
    CONFIG_FILE: JSON configuration file with download tasks
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        downloads = config.get('downloads', [])
        
        if not downloads:
            click.echo("❌ No downloads configured")
            return
        
        click.echo(f"📋 Batch Download Configuration:")
        click.echo(f"   Tasks: {len(downloads)}")
        click.echo(f"   Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
        
        for i, download in enumerate(downloads, 1):
            click.echo(f"\n📦 Task {i}:")
            click.echo(f"   Source: {download.get('source')}")
            click.echo(f"   Type: {download.get('type')}")
            click.echo(f"   Destination: {download.get('destination')}")
            
            if 'assets' in download:
                click.echo(f"   Assets: {download['assets']}")
            if 'max_items' in download:
                click.echo(f"   Max items: {download['max_items']}")
        
        if dry_run:
            click.echo(f"\n✅ Dry run completed - no files downloaded")
            click.echo(f"💡 Remove --dry-run to execute downloads")
            return
        
        # Execute downloads
        if not click.confirm("\n🚀 Execute batch download?"):
            click.echo("Batch download cancelled")
            return
        
        for i, download in enumerate(downloads, 1):
            click.echo(f"\n📦 Executing task {i}/{len(downloads)}...")
            
            # This would implement actual batch downloading
            # For now, show what would happen
            click.echo(f"   ⚠️ Batch execution not yet implemented")
            click.echo(f"   💡 Use individual download commands for now")
        
    except Exception as e:
        click.echo(f"❌ Batch download failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()
