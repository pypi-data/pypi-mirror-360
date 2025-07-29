"""
Enhanced Search CLI commands with silent 3-tier fallback
"""
import click
import json
import warnings
import open_geodata_api as ogapi

# 🔇 SUPPRESS ALL WARNINGS BY DEFAULT IN CLI
warnings.filterwarnings("ignore", category=FutureWarning, module="pystac_client")
warnings.filterwarnings("ignore", message=".*get_all_items.*deprecated.*")

try:
    import pystac_client
    import planetary_computer
    PYSTAC_AVAILABLE = True
except ImportError:
    PYSTAC_AVAILABLE = False

def parse_bbox(bbox_str):
    """Parse bbox string to list of floats with better error handling."""
    if not bbox_str:
        raise click.BadParameter('bbox cannot be empty')
    
    try:
        bbox_str = bbox_str.strip()
        if not bbox_str:
            raise ValueError("bbox is empty after stripping whitespace")
        
        bbox = [float(x.strip()) for x in bbox_str.split(',')]
        
        if len(bbox) != 4:
            raise ValueError(f"bbox must have exactly 4 values, got {len(bbox)}")
        
        west, south, east, north = bbox
        
        # Basic validation
        if west >= east:
            raise ValueError("west coordinate must be less than east coordinate")
        if south >= north:
            raise ValueError("south coordinate must be less than north coordinate")
        
        # Coordinate range validation
        if not (-180 <= west <= 180) or not (-180 <= east <= 180):
            raise ValueError("longitude values must be between -180 and 180")
        if not (-90 <= south <= 90) or not (-90 <= north <= 90):
            raise ValueError("latitude values must be between -90 and 90")
        
        return bbox
    
    except ValueError as e:
        raise click.BadParameter(f'Invalid bbox format: {e}. Use: west,south,east,north (e.g., "-122.5,47.5,-122.0,48.0")')


def parse_query(query_str):
    """Parse query string to dictionary."""
    try:
        return json.loads(query_str)
    except json.JSONDecodeError:
        raise click.BadParameter('query must be valid JSON string')


def create_client_with_fallback(provider, verbose=False):
    """Create client with 3-tier fallback support."""
    try:
        if provider == 'pc':
            return ogapi.planetary_computer(auto_sign=True, verbose=verbose)
        else:
            return ogapi.earth_search(verbose=verbose)
    except Exception as e:
        raise click.ClickException(f"Failed to create {provider} client: {e}")


@click.group(name='search')
def search_group():
    """
    🔄 Enhanced search with 3-tier fallback strategy.
    
    Find satellite imagery using intelligent fallback system:
    1. Fast simple search (default)
    2. pystac-client fallback (if 100+ items detected)
    3. Chunking fallback (if pystac-client fails)
    
    \b
    🔇 SILENT BY DEFAULT:
    • Clean output with no verbose messages
    • All warnings suppressed automatically
    • Use --verbose/-v for detailed progress
    
    \b
    Examples:
      ogapi search quick sentinel-2-l2a -b "bbox"     # Silent operation
      ogapi search items -c sentinel-2-l2a --bbox -v  # Verbose fallback details
      ogapi search compare -c sentinel-2-l2a -b bbox  # Silent comparison
    """
    pass

@search_group.command('items')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Data provider with 3-tier fallback strategy')
@click.option('--collections', '-c',
              required=True,
              help='Comma-separated collection names')
@click.option('--bbox', '-b',
              callback=lambda ctx, param, value: parse_bbox(value) if value else None,
              help='Bounding box as "west,south,east,north"')
@click.option('--datetime', '-d',
              help='Date range as "YYYY-MM-DD/YYYY-MM-DD" OR number of days back (e.g., 500)')  # 🔥 UPDATED HELP
@click.option('--query', '-q',
              callback=lambda ctx, param, value: parse_query(value) if value else None,
              help='Filter query as JSON')
@click.option('--limit', '-l',
              type=int,
              default=None,
              help='Maximum number of items (default: unlimited with fallback)')
@click.option('--all', '-a',
              is_flag=True,
              help='Get all available items using fallback strategy (default)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save search results to JSON file')
@click.option('--show-assets/--no-assets',
              default=False,
              help='Display available assets/bands for each item')
@click.option('--cloud-cover', '-cc',
              type=float,
              help='Maximum cloud cover percentage')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed fallback strategy progress')
@click.pass_context
def search_items(ctx, provider, collections, bbox, datetime, query, limit, all, output, show_assets, cloud_cover, verbose):
    """
    🔄 Enhanced search with silent 3-tier fallback strategy.
    
    Automatically tries multiple strategies to get ALL available items:
    1. Fast simple search (100 items max)
    2. pystac-client fallback (unlimited items)
    3. Chunking fallback (unlimited items)
    
    Silent by default - use --verbose/-v to see fallback details.
    
    \b
    🔥 FIXED: Now properly handles days parameter like quick command
    
    \b
    Examples:
      # Silent unlimited search (uses fallback automatically):
      ogapi search items -c sentinel-2-l2a -b "-122.5,47.5,-122.0,48.0"
      
      # Search last 500 days (FIXED):
      ogapi search items -c sentinel-2-l2a -b "bbox" -d 500
      
      # Date range format:
      ogapi search items -c sentinel-2-l2a -b "bbox" -d "2023-01-01/2023-12-31"
      
      # Verbose to see fallback strategy in action:
      ogapi search items -c sentinel-2-l2a -b "bbox" -d 500 -v
    """
    from datetime import datetime as dt, timedelta
    
    # Handle --all flag or --limit 0 to mean unlimited
    if all or limit == 0:
        actual_limit = None  # Unlimited with fallback
        display_limit = "unlimited (with fallback)"
    else:
        actual_limit = limit
        display_limit = str(limit) if limit else "unlimited (with fallback)"
    
    # 🔥 FIX: Process datetime parameter like quick command does
    processed_datetime = datetime
    if datetime and '/' not in datetime and '-' not in datetime:
        try:
            # If it's just a number, treat it as days back
            days = int(datetime)
            end_date = dt.now()
            start_date = end_date - timedelta(days=days)
            processed_datetime = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
            
            if verbose:
                click.echo(f"🔥 Converted {days} days to date range: {processed_datetime}")
        except ValueError:
            # If conversion fails, use as-is
            pass
    
    if verbose:
        click.echo(f"🔄 Searching {provider.upper()} with 3-tier fallback strategy...")
        click.echo(f"📊 Parameters: collections={collections}, bbox={bbox}, datetime={processed_datetime}")
        click.echo(f"📏 Limit: {display_limit}")
    
    try:
        # Create client with fallback support
        client = create_client_with_fallback(provider, verbose)
        
        if verbose:
            if provider == 'pc':
                click.echo("🌍 Using Planetary Computer with 3-tier fallback")
            else:
                click.echo("🔗 Using EarthSearch with 3-tier fallback")
        
        # Parse collections
        collections_list = [c.strip() for c in collections.split(',')]
        if verbose:
            click.echo(f"📁 Searching collections: {collections_list}")
        
        # Add cloud cover to query if specified
        if cloud_cover is not None:
            if query is None:
                query = {}
            query['eo:cloud_cover'] = {'lt': cloud_cover}
            if verbose:
                click.echo(f"☁️ Added cloud cover filter: <{cloud_cover}%")
        
        # 🔄 SILENT FALLBACK SEARCH
        if not verbose:
            click.echo(f"🔍 Searching {provider.upper()}...")
        
        # Create search - fallback happens automatically when calling get_all_items()
        # 🔥 FIX: Use processed_datetime instead of datetime
        results = client.search(
            collections=collections_list,
            bbox=bbox,
            datetime=processed_datetime,  # 🔥 FIXED: Use processed datetime
            query=query,
            limit=actual_limit
        )
        
        # Get all items - triggers silent fallback if needed
        items = results.get_all_items()
        
        if len(items) == 0:
            click.echo("❌ No items found matching search criteria")
            click.echo("\n💡 Try adjusting your search parameters:")
            click.echo("   • Expand the bounding box area")
            click.echo("   • Extend the date range")
            click.echo("   • Increase cloud cover threshold")
            click.echo("   • Check collection names with 'ogapi collections list'")
            
            # 🔥 DEBUG INFO: Show what parameters were actually used
            if verbose:
                click.echo(f"\n🔧 Debug info:")
                click.echo(f"   Original datetime input: {datetime}")
                click.echo(f"   Processed datetime: {processed_datetime}")
                click.echo(f"   Collections: {collections_list}")
                click.echo(f"   Bbox: {bbox}")
                click.echo(f"   Query: {query}")
            
            return
        
        # Show clean results summary
        if actual_limit is None:
            click.echo(f"\n✅ Found {len(items)} items")
        else:
            click.echo(f"\n✅ Found {len(items)} items")
        
        # Only show detailed results if NO output file is specified
        if not output:
            # Display results summary
            if len(items) > 0:
                # Calculate statistics
                cloud_covers = [item.properties.get('eo:cloud_cover') for item in items 
                               if item.properties.get('eo:cloud_cover') is not None]
                
                if cloud_covers:
                    avg_cloud = sum(cloud_covers) / len(cloud_covers)
                    min_cloud = min(cloud_covers)
                    max_cloud = max(cloud_covers)
                    click.echo(f"☁️ Cloud cover: {min_cloud:.1f}% - {max_cloud:.1f}% (avg: {avg_cloud:.1f}%)")
                
                # Show date range
                dates = [item.properties.get('datetime') for item in items 
                        if item.properties.get('datetime')]
                if dates:
                    click.echo(f"📅 Date range: {min(dates)} to {max(dates)}")
            
            # Display individual items (limit to first 10 for console display)
            display_items = items[:10] if len(items) > 10 else items
            for i, item in enumerate(display_items):
                click.echo(f"\n📄 Item {i+1}: {item.id}")
                click.echo(f"   📁 Collection: {item.collection}")
                click.echo(f"   📅 Date: {item.properties.get('datetime', 'N/A')}")
                
                cloud_cover_val = item.properties.get('eo:cloud_cover')
                if cloud_cover_val is not None:
                    click.echo(f"   ☁️ Cloud Cover: {cloud_cover_val:.1f}%")
                
                platform = item.properties.get('platform', item.properties.get('constellation'))
                if platform:
                    click.echo(f"   🛰️ Platform: {platform}")
                
                if show_assets:
                    assets = item.list_assets()
                    if len(assets) <= 8:
                        click.echo(f"   🎯 Assets: {', '.join(assets)}")
                    else:
                        click.echo(f"   🎯 Assets: {', '.join(assets[:8])} ... (+{len(assets)-8} more)")
            
            # Show if there are more items
            if len(items) > 10:
                click.echo(f"\n   ... and {len(items) - 10} more items")
        
        # Save to file if requested
        if output:
            results_data = {
                'search_metadata': {
                    'provider': provider,
                    'collections': collections_list,
                    'bbox': bbox,
                    'original_datetime_input': datetime,          # 🔥 ADDED: Track original input
                    'processed_datetime': processed_datetime,     # 🔥 ADDED: Track processed datetime
                    'query': query,
                    'limit': actual_limit,
                    'unlimited': actual_limit is None,
                    'items_found': len(items),
                    'search_timestamp': dt.now().isoformat(),
                    'fallback_strategy': True,
                    'silent_operation': not verbose
                },
                'search_params': {
                    'provider': provider,
                    'collections': collections_list,
                    'bbox': bbox,
                    'datetime': processed_datetime,  # 🔥 FIXED: Save processed datetime
                    'query': query,
                    'limit': actual_limit
                },
                'returned_count': len(items),
                'items': [item.to_dict() for item in items]
            }
            
            with open(output, 'w') as f:
                json.dump(results_data, f, indent=2)
            click.echo(f"\n💾 Results saved to: {output} ({len(items)} items)")
        
        # Clean next steps suggestions
        click.echo(f"\n💡 Next steps:")
        
        # Build the original command dynamically
        cmd_parts = ["ogapi", "search", "items", "-c", f'"{collections}"']
        
        if provider != 'pc':
            cmd_parts.extend(["-p", provider])
        if bbox:
            bbox_str = ",".join(map(str, bbox))
            cmd_parts.extend(["-b", f'"{bbox_str}"'])
        if datetime:
            cmd_parts.extend(["-d", f'"{datetime}"'])  # Use original input
        if cloud_cover:
            cmd_parts.extend(["--cloud-cover", str(cloud_cover)])
        if actual_limit:
            cmd_parts.extend(["--limit", str(actual_limit)])
        if show_assets and not output:
            cmd_parts.append("--show-assets")
        
        original_command = " ".join(cmd_parts)
        
        if not output:
            click.echo(f"   {original_command} -o results.json")
        else:
            click.echo(f"   ogapi download search-results {output}")
        
        # Alternative suggestions
        if bbox:
            bbox_str = ",".join(map(str, bbox))
            main_collection = collections_list[0]
            if datetime and datetime.isdigit():
                click.echo(f"   # Alternative quick search:")
                click.echo(f"   ogapi search quick {main_collection} -b \"{bbox_str}\" -d {datetime} -o quick_results.json")
            else:
                click.echo(f"   # Alternative quick search:")
                click.echo(f"   ogapi search quick {main_collection} -b \"{bbox_str}\" -o quick_results.json")
    
    except Exception as e:
        click.echo(f"❌ Search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        click.echo("\n💡 Troubleshooting tips:")
        click.echo("   • Check collection names: ogapi collections list")
        click.echo("   • Verify bbox format: west,south,east,north")
        click.echo("   • Check date format: YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD")
        click.echo("   • Use --verbose/-v to see detailed fallback information")
        
        raise click.Abort()

# @search_group.command('items')
# @click.option('--provider', '-p',
#               type=click.Choice(['pc', 'es'], case_sensitive=False),
#               default='pc',
#               help='Data provider with 3-tier fallback strategy')
# @click.option('--collections', '-c',
#               required=True,
#               help='Comma-separated collection names')
# @click.option('--bbox', '-b',
#               callback=lambda ctx, param, value: parse_bbox(value) if value else None,
#               help='Bounding box as "west,south,east,north"')
# @click.option('--datetime', '-d',
#               help='Date range as "YYYY-MM-DD/YYYY-MM-DD" or single date')
# @click.option('--query', '-q',
#               callback=lambda ctx, param, value: parse_query(value) if value else None,
#               help='Filter query as JSON')
# @click.option('--limit', '-l',
#               type=int,
#               default=None,
#               help='Maximum number of items (default: unlimited with fallback)')
# @click.option('--all', '-a',
#               is_flag=True,
#               help='Get all available items using fallback strategy (default)')
# @click.option('--output', '-o',
#               type=click.Path(),
#               help='Save search results to JSON file')
# @click.option('--show-assets/--no-assets',
#               default=False,
#               help='Display available assets/bands for each item')
# @click.option('--cloud-cover', '-cc',
#               type=float,
#               help='Maximum cloud cover percentage')
# @click.option('--verbose', '-v',
#               is_flag=True,
#               help='Show detailed fallback strategy progress')
# @click.pass_context
# def search_items(ctx, provider, collections, bbox, datetime, query, limit, all, output, show_assets, cloud_cover, verbose):
#     """
#     🔄 Enhanced search with silent 3-tier fallback strategy.
    
#     Automatically tries multiple strategies to get ALL available items:
#     1. Fast simple search (100 items max)
#     2. pystac-client fallback (unlimited items)
#     3. Chunking fallback (unlimited items)
    
#     Silent by default - use --verbose/-v to see fallback details.
    
#     \b
#     Examples:
#       # Silent unlimited search (uses fallback automatically):
#       ogapi search items -c sentinel-2-l2a -b "-122.5,47.5,-122.0,48.0"
      
#       # Verbose to see fallback strategy in action:
#       ogapi search items -c sentinel-2-l2a -b "bbox" -v
      
#       # With filters:
#       ogapi search items -c sentinel-2-l2a -d "2024-06-01/2024-08-31" --cloud-cover 20
#     """
#     from datetime import datetime as dt
    
#     # Handle --all flag or --limit 0 to mean unlimited
#     if all or limit == 0:
#         actual_limit = None  # Unlimited with fallback
#         display_limit = "unlimited (with fallback)"
#     else:
#         actual_limit = limit
#         display_limit = str(limit) if limit else "unlimited (with fallback)"
    
#     if verbose:
#         click.echo(f"🔄 Searching {provider.upper()} with 3-tier fallback strategy...")
#         click.echo(f"📊 Parameters: collections={collections}, bbox={bbox}, datetime={datetime}")
#         click.echo(f"📏 Limit: {display_limit}")
    
#     try:
#         # Create client with fallback support
#         client = create_client_with_fallback(provider, verbose)
        
#         if verbose:
#             if provider == 'pc':
#                 click.echo("🌍 Using Planetary Computer with 3-tier fallback")
#             else:
#                 click.echo("🔗 Using EarthSearch with 3-tier fallback")
        
#         # Parse collections
#         collections_list = [c.strip() for c in collections.split(',')]
#         if verbose:
#             click.echo(f"📁 Searching collections: {collections_list}")
        
#         # Add cloud cover to query if specified
#         if cloud_cover is not None:
#             if query is None:
#                 query = {}
#             query['eo:cloud_cover'] = {'lt': cloud_cover}
#             if verbose:
#                 click.echo(f"☁️ Added cloud cover filter: <{cloud_cover}%")
        
#         # 🔄 SILENT FALLBACK SEARCH
#         if not verbose:
#             click.echo(f"🔍 Searching {provider.upper()}...")
        
#         # Create search - fallback happens automatically when calling get_all_items()
#         results = client.search(
#             collections=collections_list,
#             bbox=bbox,
#             datetime=datetime,
#             query=query,
#             limit=actual_limit
#         )
        
#         # Get all items - triggers silent fallback if needed
#         items = results.get_all_items()
        
#         if len(items) == 0:
#             click.echo("❌ No items found matching search criteria")
#             click.echo("\n💡 Try adjusting your search parameters:")
#             click.echo("   • Expand the bounding box area")
#             click.echo("   • Extend the date range")
#             click.echo("   • Increase cloud cover threshold")
#             click.echo("   • Check collection names with 'ogapi collections list'")
#             return
        
#         # Show clean results summary
#         if actual_limit is None:
#             click.echo(f"\n✅ Found {len(items)} items")
#         else:
#             click.echo(f"\n✅ Found {len(items)} items")
        
#         # Only show detailed results if NO output file is specified
#         if not output:
#             # Display results summary
#             if len(items) > 0:
#                 # Calculate statistics
#                 cloud_covers = [item.properties.get('eo:cloud_cover') for item in items 
#                                if item.properties.get('eo:cloud_cover') is not None]
                
#                 if cloud_covers:
#                     avg_cloud = sum(cloud_covers) / len(cloud_covers)
#                     min_cloud = min(cloud_covers)
#                     max_cloud = max(cloud_covers)
#                     click.echo(f"☁️ Cloud cover: {min_cloud:.1f}% - {max_cloud:.1f}% (avg: {avg_cloud:.1f}%)")
                
#                 # Show date range
#                 dates = [item.properties.get('datetime') for item in items 
#                         if item.properties.get('datetime')]
#                 if dates:
#                     click.echo(f"📅 Date range: {min(dates)} to {max(dates)}")
            
#             # Display individual items (limit to first 10 for console display)
#             display_items = items[:10] if len(items) > 10 else items
#             for i, item in enumerate(display_items):
#                 click.echo(f"\n📄 Item {i+1}: {item.id}")
#                 click.echo(f"   📁 Collection: {item.collection}")
#                 click.echo(f"   📅 Date: {item.properties.get('datetime', 'N/A')}")
                
#                 cloud_cover_val = item.properties.get('eo:cloud_cover')
#                 if cloud_cover_val is not None:
#                     click.echo(f"   ☁️ Cloud Cover: {cloud_cover_val:.1f}%")
                
#                 platform = item.properties.get('platform', item.properties.get('constellation'))
#                 if platform:
#                     click.echo(f"   🛰️ Platform: {platform}")
                
#                 if show_assets:
#                     assets = item.list_assets()
#                     if len(assets) <= 8:
#                         click.echo(f"   🎯 Assets: {', '.join(assets)}")
#                     else:
#                         click.echo(f"   🎯 Assets: {', '.join(assets[:8])} ... (+{len(assets)-8} more)")
            
#             # Show if there are more items
#             if len(items) > 10:
#                 click.echo(f"\n   ... and {len(items) - 10} more items")
        
#         # Save to file if requested
#         if output:
#             results_data = {
#                 'search_metadata': {
#                     'provider': provider,
#                     'collections': collections_list,
#                     'bbox': bbox,
#                     'datetime': datetime,
#                     'query': query,
#                     'limit': actual_limit,
#                     'unlimited': actual_limit is None,
#                     'items_found': len(items),
#                     'search_timestamp': dt.now().isoformat(),
#                     'fallback_strategy': True,
#                     'silent_operation': not verbose
#                 },
#                 'search_params': {
#                     'provider': provider,
#                     'collections': collections_list,
#                     'bbox': bbox,
#                     'datetime': datetime,
#                     'query': query,
#                     'limit': actual_limit
#                 },
#                 'returned_count': len(items),
#                 'items': [item.to_dict() for item in items]
#             }
            
#             with open(output, 'w') as f:
#                 json.dump(results_data, f, indent=2)
#             click.echo(f"\n💾 Results saved to: {output} ({len(items)} items)")
        
#         # Clean next steps suggestions
#         click.echo(f"\n💡 Next steps:")
        
#         # Build the original command dynamically
#         cmd_parts = ["ogapi", "search", "items", "-c", f'"{collections}"']
        
#         if provider != 'pc':
#             cmd_parts.extend(["-p", provider])
#         if bbox:
#             bbox_str = ",".join(map(str, bbox))
#             cmd_parts.extend(["-b", f'"{bbox_str}"'])
#         if datetime:
#             cmd_parts.extend(["-d", f'"{datetime}"'])
#         if cloud_cover:
#             cmd_parts.extend(["--cloud-cover", str(cloud_cover)])
#         if actual_limit:
#             cmd_parts.extend(["--limit", str(actual_limit)])
#         if show_assets and not output:
#             cmd_parts.append("--show-assets")
        
#         original_command = " ".join(cmd_parts)
        
#         if not output:
#             click.echo(f"   {original_command} -o results.json")
#         else:
#             click.echo(f"   ogapi download search-results {output}")
        
#         # Alternative suggestions
#         if bbox:
#             bbox_str = ",".join(map(str, bbox))
#             main_collection = collections_list[0]
#             click.echo(f"   # Alternative quick search:")
#             click.echo(f"   ogapi search quick {main_collection} -b \"{bbox_str}\" -o quick_results.json")
    
#     except Exception as e:
#         click.echo(f"❌ Search failed: {e}")
#         if verbose:
#             import traceback
#             traceback.print_exc()
        
#         click.echo("\n💡 Troubleshooting tips:")
#         click.echo("   • Check collection names: ogapi collections list")
#         click.echo("   • Verify bbox format: west,south,east,north")
#         click.echo("   • Check date format: YYYY-MM-DD or YYYY-MM-DD/YYYY-MM-DD")
#         click.echo("   • Use --verbose/-v to see detailed fallback information")
        
#         raise click.Abort()


@search_group.command('quick')
@click.argument('collection')
@click.argument('location', required=False)
@click.option('--bbox', '-b',
              help='Bounding box as "west,south,east,north"')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Data provider with 3-tier fallback (default: pc)')
@click.option('--days', '-d',
              type=int,
              default=30,
              help='Number of days back to search (default: 30)')
@click.option('--cloud-cover', '-cc',
              type=float,
              default=30,
              help='Maximum cloud cover percentage (default: 30)')
@click.option('--limit', '-l',
              type=int,
              default=None,
              help='Maximum results (default: unlimited with fallback)')
@click.option('--all', '-a',
              is_flag=True,
              help='Get all available items using fallback strategy (default)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save results to JSON file')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed fallback strategy progress')
@click.pass_context
def quick_search(ctx, collection, location, bbox, provider, days, cloud_cover, limit, all, output, verbose):
    """
    ⚡ Enhanced quick search with silent 3-tier fallback.
    
    Fast search with automatic fallback to get ALL available items.
    Silent by default - use --verbose/-v to see fallback details.
    
    \b
    Examples:
      # Silent unlimited search:
      ogapi search quick sentinel-2-l2a -b "-122.5,47.5,-122.0,48.0"
      
      # Verbose fallback details:
      ogapi search quick sentinel-2-l2a -b "bbox" -v
      
      # Quick preview (limited):
      ogapi search quick sentinel-2-l2a -b "bbox" --limit 10
    """
    import json
    from datetime import datetime, timedelta
    
    bbox_str = bbox or location
    if not bbox_str:
        click.echo("❌ Location is required. Use either:")
        click.echo("   ogapi search quick collection --bbox \"-122.5,47.5,-122.0,48.0\"")
        click.echo("   ogapi search quick collection -b \"-122.5,47.5,-122.0,48.0\"")
        return
    
    try:
        bbox_coords = parse_bbox(bbox_str)
        
        # Handle --all flag or --limit 0 to mean unlimited
        if all or limit == 0:
            actual_limit = None  # Unlimited with fallback
            display_limit = "unlimited (with fallback)"
        else:
            actual_limit = limit
            display_limit = str(limit) if limit else "unlimited (with fallback)"
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        date_range = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
        
        if verbose:
            click.echo(f"⚡ Quick search with 3-tier fallback:")
            click.echo(f"   Collection: {collection}")
            click.echo(f"   Bbox: {bbox_coords}")
            click.echo(f"   Provider: {provider.upper()}")
            click.echo(f"   Date range: {date_range}")
            click.echo(f"   Max cloud cover: {cloud_cover}%")
            click.echo(f"   Limit: {display_limit}")
        
        if not verbose:
            click.echo(f"⚡ Quick search: {collection} (last {days} days, <{cloud_cover}% clouds)")
        
        # Create client with fallback support
        client = create_client_with_fallback(provider, verbose)
        
        # Silent fallback search
        results = client.search(
            collections=[collection],
            bbox=bbox_coords,
            datetime=date_range,
            query={'eo:cloud_cover': {'lt': cloud_cover}},
            limit=actual_limit
        )
        
        # Get all items - triggers silent fallback if needed
        items = results.get_all_items()
        
        if items:
            # Show clean results summary
            if actual_limit is None:
                click.echo(f"\n✅ Found {len(items)} items")
            else:
                click.echo(f"\n✅ Found {len(items)} clear items")
            
            # Only show item details if NO output file is specified
            if not output:
                # Show best item (lowest cloud cover)
                best_item = min(items, key=lambda x: x.properties.get('eo:cloud_cover', 100))
                click.echo(f"\n🏆 Best item (clearest):")
                click.echo(f"   📄 ID: {best_item.id}")
                click.echo(f"   📅 Date: {best_item.properties.get('datetime')}")
                cloud_cover_val = best_item.properties.get('eo:cloud_cover')
                if cloud_cover_val is not None:
                    click.echo(f"   ☁️ Cloud Cover: {cloud_cover_val:.1f}%")
                
                # Show summary (limited to first 5 for console)
                display_items = items[:5] if len(items) > 5 else items
                if len(display_items) > 1:
                    click.echo(f"\n📋 Items summary (showing first {len(display_items)}):")
                    for i, item in enumerate(display_items):
                        date = item.properties.get('datetime', '')[:10]
                        cloud = item.properties.get('eo:cloud_cover', 0)
                        cloud_str = f"{cloud:.1f}%" if cloud is not None else "N/A"
                        click.echo(f"   {i+1}. {date} - {cloud_str} clouds")
                    
                    if len(items) > 5:
                        click.echo(f"   ... and {len(items) - 5} more items")
            
            # Save results if requested
            if output:
                results_data = {
                    'search_params': {
                        'provider': provider,
                        'collections': [collection],
                        'bbox': bbox_coords,
                        'datetime': date_range,
                        'query': {'eo:cloud_cover': {'lt': cloud_cover}},
                        'limit': actual_limit,
                        'unlimited': actual_limit is None,
                        'fallback_strategy': True,
                        'silent_operation': not verbose
                    },
                    'returned_count': len(items),
                    'items': [item.to_dict() for item in items]
                }
                
                with open(output, 'w') as f:
                    json.dump(results_data, f, indent=2)
                click.echo(f"\n💾 Results saved to: {output} ({len(items)} items)")
            
            # Clean next steps suggestions
            click.echo(f"\n💡 Next steps:")
            
            cmd_parts = ["ogapi", "search", "quick", collection]
            
            if bbox:
                cmd_parts.extend(["-b", f'"{bbox_str}"'])
            elif location:
                cmd_parts.extend(["--", f'"{bbox_str}"'])
            
            if provider != 'pc':
                cmd_parts.extend(["-p", provider])
            if days != 30:
                cmd_parts.extend(["--days", str(days)])
            if cloud_cover != 30:
                cmd_parts.extend(["--cloud-cover", str(cloud_cover)])
            if actual_limit:
                cmd_parts.extend(["--limit", str(actual_limit)])
            
            original_command = " ".join(cmd_parts)
            
            if not output:
                click.echo(f"   {original_command} -o results.json")
            else:
                click.echo(f"   ogapi download search-results {output}")
            
            # Alternative suggestions
            bbox_str_display = ",".join(map(str, bbox_coords))
            click.echo(f"   # Alternative using items command:")
            click.echo(f"   ogapi search items -c {collection} -b \"{bbox_str_display}\" -o items_results.json")
            
        else:
            click.echo(f"❌ No clear items found in the last {days} days")
            click.echo(f"\n💡 Try adjusting search parameters:")
            
            cmd_parts = ["ogapi", "search", "quick", collection]
            if bbox:
                cmd_parts.extend(["-b", f'"{bbox_str}"'])
            
            if provider != 'pc':
                cmd_parts.extend(["-p", provider])
            
            base_command = " ".join(cmd_parts)
            
            click.echo(f"   • Increase days: {base_command} --days {days * 2}")
            click.echo(f"   • Relax cloud cover: {base_command} --cloud-cover {min(cloud_cover + 20, 80)}")
            click.echo(f"   • Expand area (make bbox larger)")
            if provider == 'pc':
                click.echo(f"   • Try EarthSearch: {base_command} -p es")
            else:
                click.echo(f"   • Try Planetary Computer: {base_command} -p pc")
    
    except click.BadParameter as e:
        click.echo(f"❌ Invalid bbox format: {e}")
        return
    
    except Exception as e:
        click.echo(f"❌ Quick search failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        click.echo("\n💡 Use --verbose/-v to see detailed fallback information")
        raise click.Abort()

@search_group.command('compare')
@click.option('--collections', '-c',
              required=True,
              help='Comma-separated collection names to compare')
@click.option('--bbox', '-b',
              required=True,
              callback=lambda ctx, param, value: parse_bbox(value),
              help='Bounding box as "west,south,east,north"')
@click.option('--datetime', '-d',
              help='Date range as "YYYY-MM-DD/YYYY-MM-DD" OR number of days back (e.g., 500)')  # 🔥 FLEXIBLE HELP
@click.option('--cloud-cover', '-cc',
              type=float,
              default=50,
              help='Maximum cloud cover percentage (default: 50)')
@click.option('--limit', '-l',
              type=int,
              default=None,
              help='Maximum items per provider (default: unlimited with fallback)')
@click.option('--all', '-a',
              is_flag=True,
              help='Get all available items from both providers using fallback strategy (default)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save comparison results to JSON file')
@click.option('--show-details/--no-details',
              default=False,
              help='Show detailed item information')
@click.option('--verbose', '-v',
              is_flag=True,
              help='Show detailed fallback strategy progress')
@click.pass_context
def compare_providers(ctx, collections, bbox, datetime, cloud_cover, limit, all, output, show_details, verbose):
    """
    🔄 Enhanced provider comparison with flexible datetime input.
    
    Compare both providers using the same fallback strategy for fair comparison.
    Silent by default - use --verbose/-v to see fallback details.
    
    \b
    🔥 FLEXIBLE DATETIME: Supports both formats
    • Date range: "2023-01-01/2023-12-31"
    • Days back: 500 (integer for previous days)
    
    \b
    Examples:
      # Silent comparison:
      ogapi search compare -c sentinel-2-l2a -b "-122,47,-121,48"
      
      # Compare last 500 days (integer format):
      ogapi search compare -c sentinel-2-l2a -b "bbox" -d 500
      
      # Compare specific date range (date format):
      ogapi search compare -c sentinel-2-l2a -b "bbox" -d "2023-01-01/2023-12-31"
      
      # Compare last year with verbose details:
      ogapi search compare -c sentinel-2-l2a -b "bbox" -d 365 -v
      
      # Compare with cloud filter:
      ogapi search compare -c sentinel-2-l2a -b "bbox" -d 500 -cc 30
    """
    from datetime import datetime as dt, timedelta
    
    # Handle --all flag or --limit 0 to mean unlimited
    if all or limit == 0:
        actual_limit = None  # Unlimited with fallback
        display_limit = "unlimited (with fallback)"
    else:
        actual_limit = limit
        display_limit = str(limit) if limit else "unlimited (with fallback)"
    
    try:
        collections_list = [c.strip() for c in collections.split(',')]
        
        # 🔥 FLEXIBLE DATETIME PROCESSING: Handle both formats
        processed_datetime = datetime
        datetime_type = "original"
        
        if datetime and '/' not in datetime and '-' not in datetime:
            try:
                # If it's just a number, treat it as days back
                days = int(datetime)
                end_date = dt.now()
                start_date = end_date - timedelta(days=days)
                processed_datetime = f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}"
                datetime_type = "days_converted"
                
                if verbose:
                    click.echo(f"🔥 Converted {days} days to date range: {processed_datetime}")
            except ValueError:
                # If conversion fails, use as-is (might be a single date)
                datetime_type = "single_date"
                if verbose:
                    click.echo(f"🔥 Using datetime as-is: {datetime}")
        elif '/' in datetime:
            datetime_type = "date_range"
            if verbose:
                click.echo(f"🔥 Using date range: {datetime}")
        
        if verbose:
            click.echo(f"🔄 Enhanced provider comparison with 3-tier fallback:")
        else:
            click.echo(f"🔄 Provider comparison:")
        
        click.echo(f"   📁 Collections: {', '.join(collections_list)}")
        click.echo(f"   📍 Area: {bbox}")
        
        # 🔥 ENHANCED DATETIME DISPLAY
        if processed_datetime:
            if datetime_type == "days_converted":
                original_days = datetime
                start_date, end_date = processed_datetime.split('/')
                click.echo(f"   📅 Period: Last {original_days} days ({start_date} to {end_date})")
            elif datetime_type == "date_range":
                start_date, end_date = processed_datetime.split('/')
                click.echo(f"   📅 Period: {start_date} to {end_date}")
            else:
                click.echo(f"   📅 Period: {processed_datetime}")
        else:
            click.echo(f"   📅 Period: All available data")
            
        click.echo(f"   ☁️ Max clouds: {cloud_cover}%")
        
        if verbose:
            click.echo(f"   📏 Limit per provider: {display_limit}")
            click.echo(f"   🔧 DateTime type: {datetime_type}")
        
        search_params = {
            'collections': collections_list,
            'bbox': bbox,
            'datetime': processed_datetime,  # 🔥 Use processed datetime
            'query': {'eo:cloud_cover': {'lt': cloud_cover}},
            'limit': actual_limit
        }
        
        results = {}
        
        # Search Planetary Computer with silent fallback
        try:
            if verbose:
                click.echo("\n🌍 Searching Planetary Computer with 3-tier fallback...")
            else:
                click.echo("\n🌍 Searching Planetary Computer...")
                
            pc = create_client_with_fallback('pc', verbose)
            pc_results = pc.search(**search_params)
            pc_items = pc_results.get_all_items()
            
            results['planetary_computer'] = {
                'items_found': len(pc_items),
                'items': [item.to_dict() for item in pc_items] if pc_items else [],
                'fallback_strategy': True,
                'datetime_type': datetime_type
            }
            
            click.echo(f"🌍 Planetary Computer: {len(pc_items)} items")
                
        except Exception as e:
            results['planetary_computer'] = {
                'error': str(e), 
                'items_found': 0, 
                'fallback_strategy': False,
                'datetime_type': datetime_type
            }
            click.echo(f"❌ Planetary Computer error: {e}")
        
        # Search EarthSearch with silent fallback
        try:
            if verbose:
                click.echo("🔗 Searching EarthSearch with 3-tier fallback...")
            else:
                click.echo("🔗 Searching EarthSearch...")
                
            es = create_client_with_fallback('es', verbose)
            es_results = es.search(**search_params)
            es_items = es_results.get_all_items()
            
            results['earthsearch'] = {
                'items_found': len(es_items),
                'items': [item.to_dict() for item in es_items] if es_items else [],
                'fallback_strategy': True,
                'datetime_type': datetime_type
            }
            
            click.echo(f"🔗 EarthSearch: {len(es_items)} items")
                
        except Exception as e:
            results['earthsearch'] = {
                'error': str(e), 
                'items_found': 0, 
                'fallback_strategy': False,
                'datetime_type': datetime_type
            }
            click.echo(f"❌ EarthSearch error: {e}")
        
        # Enhanced comparison summary
        pc_count = results['planetary_computer']['items_found']
        es_count = results['earthsearch']['items_found']
        
        click.echo(f"\n📊 Comparison Summary:")
        click.echo(f"   🌍 Planetary Computer: {pc_count} items")
        click.echo(f"   🔗 EarthSearch: {es_count} items")
        
        # Show detailed comparison if requested
        if not output and show_details and (pc_count > 0 or es_count > 0):
            click.echo(f"\n📋 Detailed Comparison:")
            
            if pc_count > 0:
                pc_items_obj = results['planetary_computer']['items']
                pc_dates = [item.get('properties', {}).get('datetime') for item in pc_items_obj 
                           if item.get('properties', {}).get('datetime')]
                if pc_dates:
                    click.echo(f"   🌍 PC Date range: {min(pc_dates)[:10]} to {max(pc_dates)[:10]}")
                
                # Show cloud cover stats
                pc_clouds = [item.get('properties', {}).get('eo:cloud_cover') for item in pc_items_obj 
                            if item.get('properties', {}).get('eo:cloud_cover') is not None]
                if pc_clouds:
                    avg_cloud = sum(pc_clouds) / len(pc_clouds)
                    click.echo(f"   🌍 PC Cloud cover: {min(pc_clouds):.1f}% - {max(pc_clouds):.1f}% (avg: {avg_cloud:.1f}%)")
            
            if es_count > 0:
                es_items_obj = results['earthsearch']['items']
                es_dates = [item.get('properties', {}).get('datetime') for item in es_items_obj 
                           if item.get('properties', {}).get('datetime')]
                if es_dates:
                    click.echo(f"   🔗 ES Date range: {min(es_dates)[:10]} to {max(es_dates)[:10]}")
                
                # Show cloud cover stats
                es_clouds = [item.get('properties', {}).get('eo:cloud_cover') for item in es_items_obj 
                            if item.get('properties', {}).get('eo:cloud_cover') is not None]
                if es_clouds:
                    avg_cloud = sum(es_clouds) / len(es_clouds)
                    click.echo(f"   🔗 ES Cloud cover: {min(es_clouds):.1f}% - {max(es_clouds):.1f}% (avg: {avg_cloud:.1f}%)")
        
        # Enhanced comparison analysis
        if pc_count > 0 and es_count > 0:
            if pc_count > es_count:
                diff = pc_count - es_count
                percentage_diff = (diff / es_count) * 100
                click.echo(f"   🏆 PC has {diff} more items ({percentage_diff:.1f}% more than ES)")
            elif es_count > pc_count:
                diff = es_count - pc_count
                percentage_diff = (diff / pc_count) * 100
                click.echo(f"   🏆 ES has {diff} more items ({percentage_diff:.1f}% more than PC)")
            else:
                click.echo(f"   🤝 Both providers offer equal coverage ({pc_count} items each)")
        elif pc_count > 0 and es_count == 0:
            click.echo(f"   🏆 PC has all {pc_count} items, ES has none")
        elif es_count > 0 and pc_count == 0:
            click.echo(f"   🏆 ES has all {es_count} items, PC has none")
        elif pc_count == 0 and es_count == 0:
            click.echo(f"   ❌ No items found on either provider for this time period")
        
        # Save enhanced results
        if output:
            comparison_data = {
                'comparison_metadata': {
                    'search_params': search_params,
                    'original_datetime_input': datetime,
                    'processed_datetime': processed_datetime,
                    'datetime_type': datetime_type,
                    'datetime_conversion_applied': datetime_type == "days_converted",
                    'comparison_timestamp': dt.now().isoformat(),
                    'limit_per_provider': actual_limit,
                    'unlimited_search': actual_limit is None,
                    'fallback_strategy': True,
                    'silent_operation': not verbose
                },
                'search_params': search_params,
                'results': results,
                'summary': {
                    'pc_items_found': pc_count,
                    'es_items_found': es_count,
                    'total_items': pc_count + es_count,
                    'difference': abs(pc_count - es_count),
                    'percentage_difference': abs(pc_count - es_count) / max(pc_count, es_count, 1) * 100,
                    'best_provider': 'planetary_computer' if pc_count > es_count else 'earthsearch' if es_count > pc_count else 'equal',
                    'coverage_analysis': {
                        'pc_advantage': pc_count - es_count if pc_count > es_count else 0,
                        'es_advantage': es_count - pc_count if es_count > pc_count else 0,
                        'equal_coverage': pc_count == es_count and pc_count > 0
                    }
                }
            }
            
            # Generate recommendation
            if pc_count > es_count:
                comparison_data['summary']['recommendation'] = f"Use Planetary Computer - {pc_count - es_count} more items available"
            elif es_count > pc_count:
                comparison_data['summary']['recommendation'] = f"Use EarthSearch - {es_count - pc_count} more items available"
            else:
                comparison_data['summary']['recommendation'] = "Both providers offer equal coverage"
            
            with open(output, 'w') as f:
                json.dump(comparison_data, f, indent=2)
            click.echo(f"\n💾 Enhanced comparison saved to: {output}")
            
            if pc_count > 100 or es_count > 100:
                click.echo(f"   🔥 3-tier fallback retrieved {pc_count + es_count} total items")
        
        # Enhanced recommendations with datetime awareness
        click.echo(f"\n💡 Recommendations:")
        if pc_count > es_count and pc_count > 0:
            click.echo("   • Use Planetary Computer for this search")
            click.echo(f"   • PC offers {pc_count - es_count} more items")
            best_collection = collections_list[0]
            bbox_str = ",".join(map(str, bbox))
            
            # 🔥 SMART COMMAND SUGGESTIONS based on datetime type
            if datetime_type == "days_converted":
                click.echo(f"   ogapi search quick {best_collection} -b \"{bbox_str}\" -d {datetime} -p pc -o pc_results.json")
            elif datetime_type == "date_range":
                click.echo(f"   ogapi search items -c {best_collection} -b \"{bbox_str}\" -d \"{datetime}\" -p pc -o pc_results.json")
            else:
                click.echo(f"   ogapi search quick {best_collection} -b \"{bbox_str}\" -p pc -o pc_results.json")
                
        elif es_count > pc_count and es_count > 0:
            click.echo("   • Use EarthSearch for this search")
            click.echo(f"   • ES offers {es_count - pc_count} more items")
            best_collection = collections_list[0]
            bbox_str = ",".join(map(str, bbox))
            
            # 🔥 SMART COMMAND SUGGESTIONS based on datetime type
            if datetime_type == "days_converted":
                click.echo(f"   ogapi search quick {best_collection} -b \"{bbox_str}\" -d {datetime} -p es -o es_results.json")
            elif datetime_type == "date_range":
                click.echo(f"   ogapi search items -c {best_collection} -b \"{bbox_str}\" -d \"{datetime}\" -p es -o es_results.json")
            else:
                click.echo(f"   ogapi search quick {best_collection} -b \"{bbox_str}\" -p es -o es_results.json")
                
        elif pc_count == es_count and pc_count > 0:
            click.echo(f"   • Both providers offer equal coverage ({pc_count} items)")
            click.echo("   • Choose based on your workflow needs:")
            click.echo("     - PC: Auto-signed URLs, potentially faster access")
            click.echo("     - ES: Open access, no authentication required")
        else:
            click.echo("   • No items found on either provider")
            click.echo("   • Try adjusting search parameters:")
            
            if datetime_type == "days_converted":
                suggested_days = int(datetime) * 2
                click.echo(f"     - Extend time period: -d {suggested_days}")
            elif datetime_type == "date_range":
                click.echo("     - Extend the date range")
            else:
                click.echo("     - Add a date range: -d 365 (for last year)")
                
            click.echo("     - Expand the bounding box area")
            click.echo("     - Increase cloud cover threshold")
            click.echo("     - Check collection names with 'ogapi collections list'")
    
    except Exception as e:
        click.echo(f"❌ Comparison failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        
        click.echo("\n💡 Troubleshooting tips:")
        click.echo("   • Use --verbose/-v to see detailed fallback information")
        click.echo("   • Try different datetime formats:")
        click.echo("     - Days back: -d 500")
        click.echo("     - Date range: -d \"2023-01-01/2023-12-31\"")
        
        raise click.Abort()
