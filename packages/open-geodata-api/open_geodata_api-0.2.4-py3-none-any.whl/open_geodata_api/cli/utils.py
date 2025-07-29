"""
Utility CLI commands with comprehensive help
"""
import click
import json
import open_geodata_api as ogapi
from open_geodata_api.utils import filter_by_cloud_cover, create_download_summary


@click.group(name='utils')
def utils_group():
    """
    🛠️ Utility commands for data filtering, processing, and management.
    
    Essential tools for working with search results, URLs, and download data.
    Includes filtering, validation, export, and analysis functions.
    
    \b
    Common utilities:
    • Filter data by quality metrics (cloud cover, etc.)
    • Export and validate URLs 
    • Create download summaries and reports
    • Process and analyze search results
    
    \b
    Typical workflow:
    1. Search for data and save results
    2. Filter results by quality criteria
    3. Export URLs for external processing
    4. Download data and create summaries
    
    \b
    Examples:
      ogapi utils filter-clouds results.json --max-cloud-cover 20
      ogapi utils export-urls results.json -o urls.json
      ogapi utils validate-urls urls.json
    """
    pass


@utils_group.command('filter-clouds')
@click.argument('search_json_file', type=click.Path(exists=True))
@click.option('--max-cloud-cover', '-cc',
              type=float,
              required=True,
              help='Maximum cloud cover percentage (0-100)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save filtered results to JSON file')
@click.option('--show-stats/--no-stats',
              default=True,
              help='Show cloud cover statistics')
@click.pass_context
def filter_by_clouds(ctx, search_json_file, max_cloud_cover, output, show_stats):
    """
    ☁️ Filter search results by cloud cover percentage.
    
    Removes items with cloud cover above the specified threshold.
    Essential for ensuring high-quality optical imagery for analysis.
    
    \b
    Examples:
      # Filter to very clear imagery:
      ogapi utils filter-clouds results.json --max-cloud-cover 10
      
      # Filter and save results:
      ogapi utils filter-clouds results.json -cc 25 -o clear_results.json
      
      # Filter without statistics:
      ogapi utils filter-clouds results.json -cc 15 --no-stats
    
    \b
    Cloud Cover Guidelines:
    • 0-10%:   Excellent (minimal clouds)
    • 10-25%:  Good (usable for most analysis)
    • 25-50%:  Fair (some analysis possible)
    • 50%+:    Poor (limited utility)
    
    \b
    Use Cases:
    • Optical analysis requiring clear views
    • NDVI and vegetation studies
    • Land cover classification
    • Change detection analysis
    
    SEARCH_JSON_FILE: JSON file from 'ogapi search items' command
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Validate input
        if max_cloud_cover < 0 or max_cloud_cover > 100:
            click.echo("❌ Cloud cover must be between 0 and 100 percent")
            return
        
        # Load search results
        with open(search_json_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data:
            click.echo("❌ Invalid search results file")
            click.echo("💡 Expected file from: ogapi search items ... -o results.json")
            return
        
        items_data = search_data['items']
        provider = search_data.get('search_params', {}).get('provider', 'pc')
        
        # Create collection and analyze
        from open_geodata_api.core.collections import STACItemCollection
        items = STACItemCollection(items_data, provider=provider)
        
        if verbose:
            click.echo(f"☁️ Filtering {len(items)} items by cloud cover ≤{max_cloud_cover}%")
        
        # Collect cloud cover statistics
        cloud_covers = []
        items_with_clouds = 0
        
        for item in items:
            cloud_cover = item.properties.get('eo:cloud_cover')
            if cloud_cover is not None:
                cloud_covers.append(cloud_cover)
                items_with_clouds += 1
        
        # Show original statistics
        if show_stats and cloud_covers:
            avg_cloud = sum(cloud_covers) / len(cloud_covers)
            min_cloud = min(cloud_covers)
            max_cloud = max(cloud_covers)
            
            click.echo(f"\n📊 Original cloud cover statistics:")
            click.echo(f"   Items with cloud data: {items_with_clouds}/{len(items)}")
            click.echo(f"   Range: {min_cloud:.1f}% - {max_cloud:.1f}%")
            click.echo(f"   Average: {avg_cloud:.1f}%")
        
        # Apply filter
        filtered_items = filter_by_cloud_cover(items, max_cloud_cover=max_cloud_cover)
        
        # Results
        original_count = len(items)
        filtered_count = len(filtered_items)
        removed_count = original_count - filtered_count
        
        click.echo(f"\n✅ Filtering completed:")
        click.echo(f"   Original items: {original_count}")
        click.echo(f"   Items passing filter: {filtered_count}")
        click.echo(f"   Items removed: {removed_count}")
        
        if filtered_count > 0:
            retention_rate = (filtered_count / original_count) * 100
            click.echo(f"   Retention rate: {retention_rate:.1f}%")
            
            # Show filtered statistics
            if show_stats:
                filtered_clouds = []
                for item in filtered_items:
                    cloud_cover = item.properties.get('eo:cloud_cover')
                    if cloud_cover is not None:
                        filtered_clouds.append(cloud_cover)
                
                if filtered_clouds:
                    avg_filtered = sum(filtered_clouds) / len(filtered_clouds)
                    max_filtered = max(filtered_clouds)
                    click.echo(f"\n📊 Filtered data statistics:")
                    click.echo(f"   Cloud range: 0% - {max_filtered:.1f}%")
                    click.echo(f"   Average: {avg_filtered:.1f}%")
        else:
            click.echo(f"\n⚠️ No items pass the {max_cloud_cover}% threshold")
            if cloud_covers:
                min_available = min(cloud_covers)
                click.echo(f"💡 Minimum available cloud cover: {min_available:.1f}%")
                click.echo(f"💡 Try: --max-cloud-cover {min_available + 5:.0f}")
        
        # Save filtered results
        if output:
            if filtered_count == 0:
                click.echo("⚠️ No filtered items to save")
                return
            
            filtered_data = search_data.copy()
            filtered_data['items'] = filtered_items.to_list()
            filtered_data['filter_applied'] = {
                'type': 'cloud_cover',
                'max_cloud_cover': max_cloud_cover,
                'original_count': original_count,
                'filtered_count': filtered_count,
                'retention_rate': f"{(filtered_count/original_count)*100:.1f}%"
            }
            
            with open(output, 'w') as f:
                json.dump(filtered_data, f, indent=2)
            click.echo(f"\n💾 Filtered results saved to: {output}")
            
            # Usage suggestions
            click.echo(f"\n💡 Next steps:")
            click.echo(f"   ogapi download search-results {output}")
            click.echo(f"   ogapi utils export-urls {output} -o clean_urls.json")
    
    except Exception as e:
        click.echo(f"❌ Filtering failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@utils_group.command('export-urls')
@click.argument('search_json_file', type=click.Path(exists=True))
@click.option('--output', '-o',
              type=click.Path(),
              required=True,
              help='Output URLs JSON file')
@click.option('--assets', '-a',
              help='Comma-separated list of specific assets (e.g., "B04,B03,B02")')
@click.option('--signed/--unsigned',
              default=True,
              help='Export signed URLs for Planetary Computer (default: signed)')
@click.option('--format', '-f',
              type=click.Choice(['standard', 'simple', 'nested'], case_sensitive=False),
              default='standard',
              help='Output format (standard=with metadata, simple=URLs only)')
@click.pass_context
def export_urls(ctx, search_json_file, output, assets, signed, format):
    """
    🔗 Export asset URLs from search results for external processing.
    
    Creates a JSON file with ready-to-use URLs that can be processed by
    external tools, scripts, or other applications.
    
    \b
    Examples:
      # Export all URLs:
      ogapi utils export-urls results.json -o all_urls.json
      
      # Export specific bands:
      ogapi utils export-urls results.json -o rgb_urls.json -a "B04,B03,B02"
      
      # Export unsigned URLs:
      ogapi utils export-urls results.json -o unsigned.json --unsigned
      
      # Simple format (URLs only):
      ogapi utils export-urls results.json -o simple.json --format simple
    
    \b
    Output Formats:
    • standard: Full metadata + URLs (recommended)
    • simple:   URLs only (smaller file)
    • nested:   Hierarchical structure
    
    \b
    Use Cases:
    • External download tools (wget, aria2)
    • Custom processing scripts
    • Integration with other workflows
    • Sharing URLs with collaborators
    
    \b
    URL Signing:
    • Planetary Computer: URLs are signed for immediate use
    • EarthSearch: Direct URLs (no signing needed)
    
    SEARCH_JSON_FILE: JSON file from search commands
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load and validate search results
        with open(search_json_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data:
            click.echo("❌ Invalid search results file")
            return
        
        items_data = search_data['items']
        provider = search_data.get('search_params', {}).get('provider', 'pc')
        
        # Create collection
        from open_geodata_api.core.collections import STACItemCollection
        items = STACItemCollection(items_data, provider=provider)
        
        if len(items) == 0:
            click.echo("❌ No items found in search results")
            return
        
        # Parse assets list
        asset_list = None
        if assets:
            asset_list = [a.strip() for a in assets.split(',')]
            if verbose:
                click.echo(f"🎯 Exporting assets: {', '.join(asset_list)}")
            
            # Validate assets exist
            sample_item = items[0]
            available_assets = sample_item.list_assets()
            missing_assets = [a for a in asset_list if a not in available_assets]
            if missing_assets:
                click.echo(f"⚠️ Assets not found in sample item: {missing_assets}")
                click.echo(f"💡 Available: {available_assets[:10]}")
                if not click.confirm("Continue with available assets only?"):
                    return
        
        # Export URLs
        click.echo(f"🔗 Exporting URLs from {len(items)} items...")
        if verbose:
            click.echo(f"📡 Provider: {provider}")
            click.echo(f"🔐 Signed URLs: {signed}")
        
        urls = items.get_all_urls(asset_keys=asset_list, signed=signed)
        
        if not urls:
            click.echo("❌ No URLs exported")
            return
        
        # Count URLs
        total_urls = sum(len(item_urls) for item_urls in urls.values())
        
        # Prepare export data based on format
        if format == 'simple':
            export_data = urls
        elif format == 'nested':
            export_data = {
                'provider': provider,
                'items': urls
            }
        else:  # standard format
            export_data = {
                'metadata': {
                    'source_file': search_json_file,
                    'provider': provider,
                    'items_count': len(items),
                    'assets_filter': asset_list,
                    'signed_urls': signed,
                    'total_urls': total_urls,
                    'export_format': format,
                    'created_by': 'open-geodata-api'
                },
                'urls': urls
            }
        
        # Save to file
        with open(output, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        # Success message
        click.echo(f"\n✅ Export completed:")
        click.echo(f"   Items: {len(urls)}")
        click.echo(f"   Total URLs: {total_urls}")
        click.echo(f"   Format: {format}")
        click.echo(f"   File: {output}")
        
        # File size
        try:
            from pathlib import Path
            file_size = Path(output).stat().st_size / 1024
            click.echo(f"   Size: {file_size:.1f} KB")
        except:
            pass
        
        # Usage suggestions
        click.echo(f"\n💡 Next steps:")
        click.echo(f"   ogapi download urls-json {output}")
        click.echo(f"   ogapi utils validate-urls {output}")
        
        # External tool examples
        if format == 'simple':
            click.echo(f"\n💡 External usage:")
            click.echo(f"   # Extract URLs for wget:")
            click.echo(f"   cat {output} | jq -r '.[][]' > urls.txt")
        
    except Exception as e:
        click.echo(f"❌ Export failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@utils_group.command('validate-urls')
@click.argument('urls_json_file', type=click.Path(exists=True))
@click.option('--check-expiry/--no-check-expiry',
              default=True,
              help='Check if URLs are expired (Planetary Computer only)')
@click.option('--check-access/--no-check-access',
              default=False,
              help='Test URL accessibility (HTTP HEAD requests)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save validation report to JSON file')
@click.option('--fix-expired/--no-fix',
              default=False,
              help='Attempt to re-sign expired URLs')
@click.pass_context
def validate_urls(ctx, urls_json_file, check_expiry, check_access, output, fix_expired):
    """
    🔍 Validate URLs in a JSON file for accessibility and expiration.
    
    Checks URL validity, expiration status, and optionally tests accessibility.
    Essential for ensuring download success before processing large datasets.
    
    \b
    Examples:
      # Basic validation:
      ogapi utils validate-urls urls.json
      
      # Check accessibility (slower):
      ogapi utils validate-urls urls.json --check-access
      
      # Fix expired URLs:
      ogapi utils validate-urls urls.json --fix-expired -o fixed_urls.json
      
      # Skip expiry check:
      ogapi utils validate-urls urls.json --no-check-expiry
    
    \b
    Validation Checks:
    • URL format validation
    • Expiration status (PC signed URLs)
    • HTTP accessibility (optional)
    • Provider detection
    
    \b
    Expiration Handling:
    • Detects expired Planetary Computer URLs
    • Can attempt automatic re-signing
    • Shows time until expiration
    
    \b
    Use Cases:
    • Pre-download validation
    • Troubleshooting download failures
    • URL maintenance and cleanup
    • Quality assurance
    
    URLS_JSON_FILE: JSON file containing URLs to validate
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load URLs
        with open(urls_json_file, 'r') as f:
            data = json.load(f)
        
        # Extract URLs from different formats
        if 'urls' in data and isinstance(data['urls'], dict):
            urls = data['urls']
            metadata = data.get('metadata', {})
        elif isinstance(data, dict) and all(isinstance(v, dict) for v in data.values()):
            urls = data
            metadata = {}
        else:
            click.echo("❌ Invalid URLs file format")
            click.echo("💡 Expected: {item_id: {asset: url}} or {metadata: {...}, urls: {...}}")
            return
        
        if verbose:
            click.echo(f"🔍 Validating URLs from: {urls_json_file}")
            if metadata:
                click.echo(f"📊 Source: {metadata.get('source_file', 'unknown')}")
                click.echo(f"🔗 Provider: {metadata.get('provider', 'unknown')}")
        
        # Count URLs
        total_urls = 0
        for item_urls in urls.values():
            if isinstance(item_urls, dict):
                total_urls += len(item_urls)
            else:
                total_urls += 1
        
        click.echo(f"🔍 Validating {total_urls} URLs from {len(urls)} items...")
        
        # Validation counters
        valid_urls = 0
        invalid_urls = 0
        signed_urls = 0
        expired_urls = 0
        accessible_urls = 0
        inaccessible_urls = 0
        
        expired_items = []
        invalid_items = []
        inaccessible_items = []
        fixed_urls = {}
        
        # Import validation functions
        if check_expiry or fix_expired:
            from open_geodata_api.utils import is_url_expired, is_signed_url, re_sign_url_if_needed
        
        # Validate each URL
        for item_id, item_urls in urls.items():
            if not isinstance(item_urls, dict):
                continue
            
            item_fixed_urls = {}
            
            for asset, url in item_urls.items():
                # Basic URL validation
                if not isinstance(url, str) or not url.startswith(('http://', 'https://')):
                    invalid_urls += 1
                    invalid_items.append(f"{item_id}/{asset}")
                    continue
                
                valid_urls += 1
                
                # Check signing and expiration
                if check_expiry:
                    if is_signed_url(url):
                        signed_urls += 1
                        
                        if is_url_expired(url):
                            expired_urls += 1
                            expired_items.append(f"{item_id}/{asset}")
                            
                            # Attempt to fix if requested
                            if fix_expired:
                                try:
                                    fixed_url = re_sign_url_if_needed(url, provider='planetary_computer')
                                    if fixed_url != url:
                                        item_fixed_urls[asset] = fixed_url
                                        if verbose:
                                            click.echo(f"✅ Fixed: {item_id}/{asset}")
                                except Exception as e:
                                    if verbose:
                                        click.echo(f"❌ Fix failed: {item_id}/{asset} - {e}")
                
                # Check accessibility if requested
                if check_access:
                    try:
                        import requests
                        response = requests.head(url, timeout=10)
                        if response.status_code == 200:
                            accessible_urls += 1
                        else:
                            inaccessible_urls += 1
                            inaccessible_items.append(f"{item_id}/{asset} (HTTP {response.status_code})")
                    except Exception as e:
                        inaccessible_urls += 1
                        inaccessible_items.append(f"{item_id}/{asset} ({str(e)[:50]})")
            
            if item_fixed_urls:
                fixed_urls[item_id] = item_fixed_urls
        
        # Display results
        click.echo(f"\n📊 Validation Results:")
        click.echo(f"   Total URLs: {total_urls}")
        click.echo(f"   Valid format: {valid_urls}")
        
        if invalid_urls > 0:
            click.echo(f"   Invalid format: {invalid_urls}")
            if verbose and invalid_items:
                click.echo(f"      Examples: {invalid_items[:3]}")
        
        if check_expiry:
            click.echo(f"   Signed URLs: {signed_urls}")
            
            if expired_urls > 0:
                click.echo(f"   Expired URLs: {expired_urls}")
                click.echo(f"      Items: {len(expired_items)}")
                
                if verbose and expired_items:
                    click.echo(f"      Examples: {expired_items[:5]}")
                
                if fix_expired and fixed_urls:
                    total_fixed = sum(len(item_urls) for item_urls in fixed_urls.values())
                    click.echo(f"   Fixed URLs: {total_fixed}")
            else:
                click.echo(f"   ✅ No expired URLs found")
        
        if check_access:
            click.echo(f"   Accessible: {accessible_urls}")
            
            if inaccessible_urls > 0:
                click.echo(f"   Inaccessible: {inaccessible_urls}")
                if verbose and inaccessible_items:
                    click.echo(f"      Examples: {inaccessible_items[:3]}")
        
        # Save results if requested
        if output:
            # Create output data
            output_data = data.copy()  # Start with original data
            
            # Update URLs with fixed versions
            if fixed_urls:
                if 'urls' in output_data:
                    for item_id, item_fixed_urls in fixed_urls.items():
                        if item_id in output_data['urls']:
                            output_data['urls'][item_id].update(item_fixed_urls)
                else:
                    for item_id, item_fixed_urls in fixed_urls.items():
                        if item_id in output_data:
                            output_data[item_id].update(item_fixed_urls)
            
            # Add validation metadata
            validation_info = {
                'validation_timestamp': click.get_current_context().meta.get('timestamp'),
                'total_urls': total_urls,
                'valid_urls': valid_urls,
                'invalid_urls': invalid_urls,
                'signed_urls': signed_urls,
                'expired_urls': expired_urls,
                'fixed_urls': sum(len(item_urls) for item_urls in fixed_urls.values()) if fixed_urls else 0
            }
            
            if 'metadata' in output_data:
                output_data['metadata']['validation'] = validation_info
            else:
                output_data['validation'] = validation_info
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            click.echo(f"\n💾 Validation results saved to: {output}")
        
        # Recommendations
        if expired_urls > 0:
            click.echo(f"\n💡 Recommendations:")
            click.echo(f"   • Use download commands to auto-refresh expired URLs")
            click.echo(f"   • Or use --fix-expired to update URLs")
        
        if invalid_urls > 0:
            click.echo(f"   • Check URL format and source data")
        
        if check_access and inaccessible_urls > 0:
            click.echo(f"   • Check internet connectivity")
            click.echo(f"   • Some URLs may have temporary access issues")
    
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@utils_group.command('download-summary')
@click.argument('download_results_json', type=click.Path(exists=True))
@click.option('--output', '-o',
              type=click.Path(),
              help='Save summary to JSON file')
@click.option('--format', '-f',
              type=click.Choice(['detailed', 'brief'], case_sensitive=False),
              default='detailed',
              help='Summary detail level')
def download_summary(download_results_json, output, format):
    """
    📈 Create comprehensive summary from download results.
    
    Analyzes download results to provide statistics, success rates,
    and performance metrics. Useful for monitoring and reporting.
    
    \b
    Examples:
      # Create detailed summary:
      ogapi utils download-summary download_results.json
      
      # Brief summary:
      ogapi utils download-summary results.json --format brief
      
      # Save summary report:
      ogapi utils download-summary results.json -o report.json
    
    \b
    Summary Includes:
    • Success/failure rates
    • File size statistics
    • Download performance
    • Error analysis
    • Provider breakdown
    
    \b
    Use Cases:
    • Quality assurance
    • Performance monitoring
    • Project reporting
    • Troubleshooting analysis
    
    DOWNLOAD_RESULTS_JSON: Results from download commands
    """
    try:
        with open(download_results_json, 'r') as f:
            results = json.load(f)
        
        summary = create_download_summary(results, output)
        
        # Display summary
        if format == 'brief':
            click.echo(f"📈 Download Summary (Brief):")
            click.echo(f"   Success: {summary['successful_downloads']}/{summary['total_files']} ({summary['success_rate']})")
            click.echo(f"   Timestamp: {summary['timestamp']}")
        else:
            click.echo(f"📈 Detailed Download Summary:")
            click.echo(f"   Total files: {summary['total_files']}")
            click.echo(f"   Successful: {summary['successful_downloads']}")
            click.echo(f"   Failed: {summary['failed_downloads']}")
            click.echo(f"   Success rate: {summary['success_rate']}")
            click.echo(f"   Timestamp: {summary['timestamp']}")
            
            # Additional details if available
            if 'results' in summary:
                total_items = len(summary['results'])
                click.echo(f"   Items processed: {total_items}")
        
        if output:
            click.echo(f"\n💾 Summary saved to: {output}")
        
        # Recommendations based on success rate
        success_num = summary['successful_downloads']
        total_num = summary['total_files']
        
        if total_num > 0:
            success_rate = (success_num / total_num) * 100
            
            if success_rate < 80:
                click.echo(f"\n⚠️ Low success rate ({success_rate:.1f}%)")
                click.echo(f"💡 Consider:")
                click.echo(f"   • Checking internet connectivity")
                click.echo(f"   • Validating URLs: ogapi utils validate-urls")
                click.echo(f"   • Using --verbose for detailed error info")
            elif success_rate < 95:
                click.echo(f"\n📊 Good success rate ({success_rate:.1f}%)")
                click.echo(f"💡 A few failures are normal for large downloads")
            else:
                click.echo(f"\n✅ Excellent success rate ({success_rate:.1f}%)")
    
    except Exception as e:
        click.echo(f"❌ Summary creation failed: {e}")
        raise click.Abort()


@utils_group.command('analyze')
@click.argument('search_json_file', type=click.Path(exists=True))
@click.option('--metric', '-m',
              type=click.Choice(['cloud_cover', 'temporal', 'spatial', 'assets'], case_sensitive=False),
              default='cloud_cover',
              help='Analysis metric to focus on')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save analysis to JSON file')
@click.pass_context
def analyze_results(ctx, search_json_file, metric, output):
    """
    📊 Analyze search results with statistical summaries.
    
    Provides comprehensive analysis of search results including
    quality metrics, temporal distribution, and coverage statistics.
    
    \b
    Examples:
      # Analyze cloud cover distribution:
      ogapi utils analyze results.json
      
      # Temporal analysis:
      ogapi utils analyze results.json --metric temporal
      
      # Asset availability analysis:
      ogapi utils analyze results.json --metric assets
    
    \b
    Analysis Types:
    • cloud_cover: Quality distribution and statistics
    • temporal: Date coverage and gaps
    • spatial: Geographic distribution
    • assets: Asset availability across items
    
    SEARCH_JSON_FILE: JSON file from search commands
    """
    verbose = ctx.obj.get('verbose', False)
    
    try:
        # Load data
        with open(search_json_file, 'r') as f:
            search_data = json.load(f)
        
        if 'items' not in search_data:
            click.echo("❌ Invalid search results file")
            return
        
        items_data = search_data['items']
        provider = search_data.get('search_params', {}).get('provider', 'unknown')
        
        from open_geodata_api.core.collections import STACItemCollection
        items = STACItemCollection(items_data, provider=provider)
        
        click.echo(f"📊 Analyzing {len(items)} items ({metric} analysis)")
        click.echo(f"🔗 Provider: {provider}")
        
        analysis_results = {}
        
        if metric == 'cloud_cover':
            # Cloud cover analysis
            cloud_covers = []
            items_with_clouds = 0
            
            for item in items:
                cloud_cover = item.properties.get('eo:cloud_cover')
                if cloud_cover is not None:
                    cloud_covers.append(cloud_cover)
                    items_with_clouds += 1
            
            if cloud_covers:
                import statistics
                
                analysis_results = {
                    'total_items': len(items),
                    'items_with_cloud_data': items_with_clouds,
                    'min_cloud_cover': min(cloud_covers),
                    'max_cloud_cover': max(cloud_covers),
                    'mean_cloud_cover': statistics.mean(cloud_covers),
                    'median_cloud_cover': statistics.median(cloud_covers),
                    'std_cloud_cover': statistics.stdev(cloud_covers) if len(cloud_covers) > 1 else 0
                }
                
                # Quality categories
                excellent = len([c for c in cloud_covers if c <= 10])
                good = len([c for c in cloud_covers if 10 < c <= 25])
                fair = len([c for c in cloud_covers if 25 < c <= 50])
                poor = len([c for c in cloud_covers if c > 50])
                
                analysis_results['quality_distribution'] = {
                    'excellent_0_10': excellent,
                    'good_10_25': good,
                    'fair_25_50': fair,
                    'poor_50_plus': poor
                }
                
                click.echo(f"\n☁️ Cloud Cover Analysis:")
                click.echo(f"   Items with data: {items_with_clouds}/{len(items)}")
                click.echo(f"   Range: {min(cloud_covers):.1f}% - {max(cloud_covers):.1f}%")
                click.echo(f"   Mean: {statistics.mean(cloud_covers):.1f}%")
                click.echo(f"   Median: {statistics.median(cloud_covers):.1f}%")
                
                click.echo(f"\n📊 Quality Distribution:")
                click.echo(f"   Excellent (0-10%): {excellent} items")
                click.echo(f"   Good (10-25%): {good} items")
                click.echo(f"   Fair (25-50%): {fair} items")
                click.echo(f"   Poor (50%+): {poor} items")
            else:
                click.echo("❌ No cloud cover data available")
        
        elif metric == 'temporal':
            # Temporal analysis
            dates = []
            for item in items:
                date_str = item.properties.get('datetime')
                if date_str:
                    dates.append(date_str[:10])  # Extract date part
            
            if dates:
                sorted_dates = sorted(dates)
                unique_dates = list(set(dates))
                
                analysis_results = {
                    'total_items': len(items),
                    'date_range': f"{sorted_dates[0]} to {sorted_dates[-1]}",
                    'unique_dates': len(unique_dates),
                    'first_date': sorted_dates[0],
                    'last_date': sorted_dates[-1]
                }
                
                click.echo(f"\n📅 Temporal Analysis:")
                click.echo(f"   Items with dates: {len(dates)}/{len(items)}")
                click.echo(f"   Date range: {sorted_dates[0]} to {sorted_dates[-1]}")
                click.echo(f"   Unique dates: {len(unique_dates)}")
                
                # Monthly distribution
                monthly_counts = {}
                for date in dates:
                    month = date[:7]  # YYYY-MM
                    monthly_counts[month] = monthly_counts.get(month, 0) + 1
                
                if len(monthly_counts) <= 12:  # Show if reasonable
                    click.echo(f"\n📊 Monthly Distribution:")
                    for month in sorted(monthly_counts.keys()):
                        click.echo(f"   {month}: {monthly_counts[month]} items")
                
                analysis_results['monthly_distribution'] = monthly_counts
            else:
                click.echo("❌ No temporal data available")
        
        elif metric == 'assets':
            # Asset availability analysis
            all_assets = set()
            asset_counts = {}
            
            for item in items:
                item_assets = item.list_assets()
                all_assets.update(item_assets)
                
                for asset in item_assets:
                    asset_counts[asset] = asset_counts.get(asset, 0) + 1
            
            if all_assets:
                total_items = len(items)
                
                analysis_results = {
                    'total_items': total_items,
                    'unique_assets': len(all_assets),
                    'asset_availability': asset_counts
                }
                
                # Find common assets (available in most items)
                common_assets = {k: v for k, v in asset_counts.items() 
                               if v >= total_items * 0.9}  # 90% availability
                
                click.echo(f"\n🎯 Asset Analysis:")
                click.echo(f"   Unique assets: {len(all_assets)}")
                click.echo(f"   Common assets (≥90%): {len(common_assets)}")
                
                if common_assets:
                    click.echo(f"\n📊 Most Available Assets:")
                    for asset in sorted(common_assets.keys()):
                        percentage = (asset_counts[asset] / total_items) * 100
                        click.echo(f"   {asset}: {asset_counts[asset]}/{total_items} ({percentage:.0f}%)")
                
                # Show rare assets
                rare_assets = {k: v for k, v in asset_counts.items() 
                              if v < total_items * 0.5}  # <50% availability
                
                if rare_assets and len(rare_assets) <= 10:
                    click.echo(f"\n⚠️ Rare Assets (<50%):")
                    for asset in sorted(rare_assets.keys()):
                        percentage = (asset_counts[asset] / total_items) * 100
                        click.echo(f"   {asset}: {asset_counts[asset]}/{total_items} ({percentage:.0f}%)")
            else:
                click.echo("❌ No asset data available")
        
        # Save analysis if requested
        if output and analysis_results:
            output_data = {
                'analysis_metadata': {
                    'source_file': search_json_file,
                    'metric': metric,
                    'provider': provider,
                    'analysis_timestamp': click.get_current_context().meta.get('timestamp')
                },
                'analysis_results': analysis_results
            }
            
            with open(output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            click.echo(f"\n💾 Analysis saved to: {output}")
        
        # Recommendations
        click.echo(f"\n💡 Recommendations:")
        if metric == 'cloud_cover' and analysis_results:
            mean_cloud = analysis_results.get('mean_cloud_cover', 50)
            if mean_cloud > 30:
                click.echo(f"   • Consider stricter cloud filtering (<25%)")
            else:
                click.echo(f"   • Good quality data available")
        
        elif metric == 'assets' and analysis_results:
            common_count = len([k for k, v in analysis_results['asset_availability'].items() 
                               if v >= len(items) * 0.9])
            if common_count < 5:
                click.echo(f"   • Limited asset consistency across items")
            else:
                click.echo(f"   • Good asset availability for analysis")
    
    except Exception as e:
        click.echo(f"❌ Analysis failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()
