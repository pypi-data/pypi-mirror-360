"""
Collections management CLI commands with comprehensive help
"""
import click
import json
import open_geodata_api as ogapi


@click.group(name='collections')
def collections_group():
    """
    🗂️ Collection discovery and management commands.
    
    Collections are groups of related satellite datasets (e.g., Sentinel-2, Landsat).
    Use these commands to explore available data collections from different providers.
    
    \b
    Examples:
      ogapi collections list                        # List all collections
      ogapi collections list --provider pc         # PC collections only
      ogapi collections search sentinel            # Find Sentinel collections
      ogapi collections info sentinel-2-l2a       # Get collection details
    """
    pass


@collections_group.command('list')
@click.option('--provider', '-p', 
              type=click.Choice(['pc', 'es', 'both'], case_sensitive=False), 
              default='both',
              help='Provider to list collections from (pc=Planetary Computer, es=EarthSearch)')
@click.option('--filter', '-f', 'filter_term',
              help='Filter collections by keyword (case-insensitive)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save results to JSON file')
@click.pass_context
def list_collections(ctx, provider, filter_term, output):
    """
    📋 List available collections from data providers.
    
    Shows all available satellite data collections that can be searched.
    Each collection represents a specific dataset (e.g., Sentinel-2 Level-2A).
    
    \b
    Examples:
      ogapi collections list                        # All collections from both providers
      ogapi collections list -p pc                 # Planetary Computer only
      ogapi collections list -f sentinel           # Collections with "sentinel" in name
      ogapi collections list -o collections.json   # Save to file
    
    \b
    Provider abbreviations:
      pc   = Microsoft Planetary Computer
      es   = AWS Element84 EarthSearch  
      both = Both providers (default)
    """
    verbose = ctx.obj.get('verbose', False)
    
    if verbose:
        click.echo(f"📋 Listing collections from: {provider}")
    
    results = {}
    
    try:
        if provider in ['pc', 'both']:
            if verbose:
                click.echo("🌍 Fetching Planetary Computer collections...")
            pc = ogapi.planetary_computer()
            pc_collections = pc.list_collections()
            
            if filter_term:
                pc_collections = [c for c in pc_collections if filter_term.lower() in c.lower()]
            
            results['planetary_computer'] = pc_collections
            
            click.echo(f"\n🌍 Planetary Computer ({len(pc_collections)} collections):")
            for collection in pc_collections:
                click.echo(f"  • {collection}")
        
        if provider in ['es', 'both']:
            if verbose:
                click.echo("🔗 Fetching EarthSearch collections...")
            es = ogapi.earth_search()
            es_collections = es.list_collections()
            
            if filter_term:
                es_collections = [c for c in es_collections if filter_term.lower() in c.lower()]
            
            results['earthsearch'] = es_collections
            
            click.echo(f"\n🔗 EarthSearch ({len(es_collections)} collections):")
            for collection in es_collections:
                click.echo(f"  • {collection}")
        
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2)
            click.echo(f"\n💾 Results saved to: {output}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise click.Abort()


@collections_group.command('info')
@click.argument('collection_name')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es'], case_sensitive=False),
              default='pc',
              help='Provider to get collection info from (default: pc)')
@click.option('--output', '-o',
              type=click.Path(),
              help='Save detailed info to JSON file')
def collection_info(collection_name, provider, output):
    """
    📊 Get detailed information about a specific collection.
    
    Shows comprehensive metadata including:
    - Collection title and description
    - Temporal and spatial extent
    - Available assets/bands
    - Data licensing information
    
    \b
    Examples:
      ogapi collections info sentinel-2-l2a        # Get Sentinel-2 info from PC
      ogapi collections info sentinel-2-l2a -p es  # Get from EarthSearch
      ogapi collections info landsat-c2-l2 -o info.json  # Save to file
    
    COLLECTION_NAME: The ID of the collection to get info for
    """
    try:
        if provider == 'pc':
            client = ogapi.planetary_computer()
        else:
            client = ogapi.earth_search()
        
        info = client.get_collection_info(collection_name)
        
        if info:
            click.echo(f"\n📊 Collection: {collection_name}")
            click.echo(f"🔗 Provider: {provider.upper()}")
            click.echo(f"📝 Title: {info.get('title', 'N/A')}")
            click.echo(f"📄 Description: {info.get('description', 'N/A')[:200]}...")
            
            if 'extent' in info:
                temporal = info['extent'].get('temporal', {})
                if temporal:
                    click.echo(f"📅 Temporal extent: {temporal}")
                
                spatial = info['extent'].get('spatial', {})
                if spatial:
                    click.echo(f"🗺️ Spatial extent: {spatial}")
            
            if 'item_assets' in info:
                assets = list(info['item_assets'].keys())[:5]
                click.echo(f"🎯 Available assets: {', '.join(assets)}")
                if len(info['item_assets']) > 5:
                    click.echo(f"                     ... and {len(info['item_assets'])-5} more")
            
            if output:
                with open(output, 'w') as f:
                    json.dump(info, f, indent=2)
                click.echo(f"💾 Full info saved to: {output}")
        else:
            click.echo(f"❌ Collection '{collection_name}' not found in {provider.upper()}")
            click.echo(f"💡 Try: ogapi collections list -p {provider}")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()


@collections_group.command('search')
@click.argument('keyword')
@click.option('--provider', '-p',
              type=click.Choice(['pc', 'es', 'both'], case_sensitive=False),
              default='both',
              help='Provider to search collections in (default: both)')
def search_collections(keyword, provider):
    """
    🔍 Search collections by keyword.
    
    Finds collections containing the specified keyword in their name or ID.
    Useful for discovering related datasets.
    
    \b
    Examples:
      ogapi collections search sentinel             # Find all Sentinel collections
      ogapi collections search landsat -p pc       # Find Landsat in PC only
      ogapi collections search modis               # Find MODIS collections
    
    KEYWORD: Search term to look for in collection names (case-insensitive)
    """
    try:
        found_any = False
        
        if provider in ['pc', 'both']:
            pc = ogapi.planetary_computer()
            pc_results = pc.search_collections(keyword)
            
            if pc_results:
                found_any = True
                click.echo(f"\n🌍 Planetary Computer matches for '{keyword}':")
                for collection in pc_results:
                    click.echo(f"  • {collection}")
        
        if provider in ['es', 'both']:
            es = ogapi.earth_search()
            es_results = es.search_collections(keyword)
            
            if es_results:
                found_any = True
                click.echo(f"\n🔗 EarthSearch matches for '{keyword}':")
                for collection in es_results:
                    click.echo(f"  • {collection}")
        
        if not found_any:
            click.echo(f"❌ No collections found matching '{keyword}'")
            click.echo(f"💡 Try: ogapi collections list")
    
    except Exception as e:
        click.echo(f"❌ Error: {e}")
        raise click.Abort()
