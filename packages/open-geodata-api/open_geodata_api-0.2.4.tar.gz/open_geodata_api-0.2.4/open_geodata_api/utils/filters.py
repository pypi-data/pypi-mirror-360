"""
Common filtering utilities for both PC and EarthSearch
Enhanced with intelligent date and geometry filtering capabilities
"""

from typing import List, Dict, Union, Optional
from datetime import datetime
import warnings

from ..core.collections import STACItemCollection


def filter_by_date_range(item_collection: STACItemCollection, start_date=None, end_date=None) -> STACItemCollection:
    """
    🧠 INTELLIGENT: Filter items by date range with flexible input formats.
    
    Accepts start_date and end_date as:
    - datetime objects
    - ISO 8601 strings ("2023-01-01", "2023-01-01T12:00:00Z")
    - Various date string formats (automatically parsed)
    - None (no filtering for that boundary)
    
    Args:
        item_collection: STACItemCollection to filter
        start_date: Start date (datetime, string, or None)
        end_date: End date (datetime, string, or None)
    
    Returns:
        STACItemCollection: Filtered collection
    
    Examples:
        # Using datetime objects
        filtered = filter_by_date_range(items, datetime(2023, 1, 1), datetime(2023, 12, 31))
        
        # Using ISO strings
        filtered = filter_by_date_range(items, "2023-01-01", "2023-12-31")
        
        # Using various date formats
        filtered = filter_by_date_range(items, "Jan 1, 2023", "Dec 31, 2023")
        
        # One-sided filtering
        filtered = filter_by_date_range(items, start_date="2023-01-01")  # Only start
        filtered = filter_by_date_range(items, end_date="2023-12-31")    # Only end
    """
    try:
        import dateutil.parser
    except ImportError:
        raise ImportError("python-dateutil is required for intelligent date parsing. "
                         "Please install it via 'pip install python-dateutil'")
    
    from datetime import timezone

    def normalize_timezone(dt1, dt2):
        """🔥 FIX: Normalize timezone information for comparison."""
        if dt1 is None or dt2 is None:
            return dt1, dt2
            
        # If one is offset-aware and the other is offset-naive
        if dt1.tzinfo is None and dt2.tzinfo is not None:
            # Make dt1 offset-aware (assume UTC)
            dt1 = dt1.replace(tzinfo=timezone.utc)
        elif dt1.tzinfo is not None and dt2.tzinfo is None:
            # Make dt2 offset-aware (assume UTC)
            dt2 = dt2.replace(tzinfo=timezone.utc)
        elif dt1.tzinfo is None and dt2.tzinfo is None:
            # Both are naive, leave as-is
            pass
        # If both are offset-aware, leave as-is (Python can compare them)
        
        return dt1, dt2
    
    # 🧠 INTELLIGENT: Parse start_date with flexible input handling
    if start_date is not None and not isinstance(start_date, datetime):
        try:
            if isinstance(start_date, str):
                start_date = dateutil.parser.parse(start_date)
            else:
                # Try to convert other types to string first
                start_date = dateutil.parser.parse(str(start_date))
        except Exception as e:
            raise ValueError(f"Invalid start_date format '{start_date}': {e}")

    # 🧠 INTELLIGENT: Parse end_date with flexible input handling
    if end_date is not None and not isinstance(end_date, datetime):
        try:
            if isinstance(end_date, str):
                end_date = dateutil.parser.parse(end_date)
            else:
                # Try to convert other types to string first
                end_date = dateutil.parser.parse(str(end_date))
        except Exception as e:
            raise ValueError(f"Invalid end_date format '{end_date}': {e}")

    filtered_items = []
    
    for item_data in item_collection._raw_items:
        # Get item date with multiple fallback paths
        item_date_str = None
        properties = item_data.get('properties', {})
        
        # Try different datetime property names
        for date_field in ['datetime', 'start_datetime', 'end_datetime', 'created', 'updated']:
            if date_field in properties:
                item_date_str = properties[date_field]
                break
        
        if not item_date_str:
            continue  # Skip items without date information

        # Parse item date
        try:
            item_date = dateutil.parser.parse(item_date_str)
        except Exception:
            continue  # Skip items with unparseable dates

        # 🔥 FIX: Normalize timezone information before comparison
        normalized_start_date, normalized_item_date = normalize_timezone(start_date, item_date)
        normalized_end_date, normalized_item_date = normalize_timezone(end_date, normalized_item_date)

        # Apply date range filtering with normalized dates
        try:
            if normalized_start_date and normalized_item_date < normalized_start_date:
                continue
            if normalized_end_date and normalized_item_date > normalized_end_date:
                continue
        except TypeError as e:
            # If comparison still fails, skip this item and warn
            warnings.warn(f"Date comparison failed for item {item_data.get('id', 'unknown')}: {e}")
            continue

        filtered_items.append(item_data)
    
    return STACItemCollection(filtered_items, provider=item_collection.provider)



def filter_by_geometry(item_collection: STACItemCollection, geometry) -> STACItemCollection:
    """
    🧠 INTELLIGENT: Filter items by geometry with automatic type detection.
    
    Automatically detects and handles various geometry types and formats:
    
    Geometry Types:
    - Point, LineString, Polygon
    - MultiPoint, MultiLineString, MultiPolygon
    - GeometryCollection
    
    Input Formats:
    - Shapely geometries (Point, Polygon, etc.)
    - GeoPandas GeoSeries/GeoDataFrame
    - GeoJSON-like dictionaries
    - Bounding box as [minx, miny, maxx, maxy]
    - Extent as [minx, miny, maxx, maxy]
    - Two diagonal points as [[x1, y1], [x2, y2]]
    - WKT strings (if shapely available)
    
    Args:
        item_collection: STACItemCollection to filter
        geometry: Input geometry in various formats
    
    Returns:
        STACItemCollection: Filtered collection
    
    Examples:
        # Using shapely geometry
        from shapely.geometry import Point, Polygon
        filtered = filter_by_geometry(items, Point(-122, 47))
        filtered = filter_by_geometry(items, Polygon([...]))
        
        # Using bbox
        filtered = filter_by_geometry(items, [-122.5, 47.5, -122.0, 48.0])
        
        # Using GeoDataFrame
        filtered = filter_by_geometry(items, gdf.geometry[0])
        
        # Using GeoJSON-like dict
        filtered = filter_by_geometry(items, {"type": "Point", "coordinates": [-122, 47]})
    """
    # 🧠 INTELLIGENT: Try to import required packages
    try:
        from shapely.geometry import shape, box, Point, Polygon
        from shapely.wkt import loads as wkt_loads
        SHAPELY_AVAILABLE = True
    except ImportError:
        SHAPELY_AVAILABLE = False

    # Try to import geopandas if available
    try:
        import geopandas as gpd
        GEOPANDAS_AVAILABLE = True
    except ImportError:
        GEOPANDAS_AVAILABLE = False
        gpd = None

    if not SHAPELY_AVAILABLE:
        raise ImportError("shapely is required for filter_by_geometry. "
                         "Please install it via 'pip install shapely'")

    # 🧠 INTELLIGENT: Detect and convert input geometry type
    geom = None
    
    # 1. Check for GeoPandas geometries
    if GEOPANDAS_AVAILABLE:
        if hasattr(gpd, 'GeoSeries') and isinstance(geometry, gpd.GeoSeries):
            if len(geometry) == 1:
                geom = geometry.iloc[0]
            else:
                geom = geometry.unary_union
        elif hasattr(gpd, 'GeoDataFrame') and isinstance(geometry, gpd.GeoDataFrame):
            geom = geometry.geometry.unary_union
    
    # 2. Check for Shapely geometries
    if geom is None and hasattr(geometry, 'geom_type') and hasattr(geometry, 'intersects'):
        geom = geometry
    
    # 3. Check for GeoJSON-like dictionary
    elif geom is None and isinstance(geometry, dict):
        if 'type' in geometry and 'coordinates' in geometry:
            try:
                geom = shape(geometry)
            except Exception as e:
                raise ValueError(f"Invalid GeoJSON geometry: {e}")
        else:
            raise ValueError("Invalid geometry dictionary format. Expected GeoJSON-like structure.")
    
    # 4. Check for bounding box or coordinate arrays
    elif geom is None and isinstance(geometry, (list, tuple)):
        if len(geometry) == 4 and all(isinstance(x, (int, float)) for x in geometry):
            # Bounding box: [minx, miny, maxx, maxy]
            try:
                geom = box(*geometry)
            except Exception as e:
                raise ValueError(f"Invalid bounding box coordinates: {e}")
        
        elif len(geometry) == 2 and all(isinstance(x, (int, float)) for x in geometry):
            # 🔥 FIX: Single point [x, y] - check this FIRST when len==2
            try:
                geom = Point(geometry)
            except Exception as e:
                raise ValueError(f"Invalid point coordinates: {e}")
        
        elif len(geometry) == 2:
            # 🔥 FIX: Two points diagonal - check this AFTER single point
            # Two points diagonal: [[x1, y1], [x2, y2]] or [(x1, y1), (x2, y2)]
            try:
                if all(isinstance(pt, (list, tuple)) and len(pt) == 2 for pt in geometry):
                    x1, y1 = geometry[0]
                    x2, y2 = geometry[1]
                    minx, maxx = min(x1, x2), max(x1, x2)
                    miny, maxy = min(y1, y2), max(y1, y2)
                    geom = box(minx, miny, maxx, maxy)
                else:
                    raise ValueError("Two-point format requires [[x1, y1], [x2, y2]]")
            except Exception as e:
                raise ValueError(f"Invalid two-point diagonal format: {e}")
        
        elif len(geometry) == 2 and all(isinstance(x, (int, float)) for x in geometry):
            # Single point: [x, y]
            try:
                geom = Point(geometry)
            except Exception as e:
                raise ValueError(f"Invalid point coordinates: {e}")
        
        else:
            # Try to interpret as polygon coordinates
            try:
                if len(geometry) >= 3:  # Minimum for polygon
                    geom = Polygon(geometry)
                else:
                    raise ValueError("Insufficient coordinates for geometry")
            except Exception as e:
                raise ValueError(f"Invalid coordinate list format: {e}")
    
    # 5. Check for WKT string
    elif geom is None and isinstance(geometry, str):
        try:
            geom = wkt_loads(geometry)
        except Exception as e:
            raise ValueError(f"Invalid WKT string: {e}")
    
    # 6. Unknown format
    if geom is None:
        raise ValueError(f"Unsupported geometry type: {type(geometry)}. "
                        f"Supported formats: shapely geometries, geopandas geometries, "
                        f"GeoJSON dictionaries, bounding boxes [minx,miny,maxx,maxy], "
                        f"coordinate arrays, WKT strings")

    filtered_items = []
    
    for item_data in item_collection._raw_items:
        # 🧠 INTELLIGENT: Get item geometry with multiple fallback strategies
        item_geom_dict = item_data.get('geometry')
        if not item_geom_dict:
            # Try alternative geometry locations
            bbox = item_data.get('bbox')
            if bbox and len(bbox) == 4:
                try:
                    item_geom = box(*bbox)
                except Exception:
                    continue  # Skip this item
            else:
                continue  # Skip this item
        else:
            try:
                item_geom = shape(item_geom_dict)
            except Exception:
                continue  # Skip this item

        # 🧠 INTELLIGENT: Perform intersection check with error handling
        try:
            if geom.intersects(item_geom):
                filtered_items.append(item_data)
        except Exception as e:
            warnings.warn(f"Geometry intersection failed for item {item_data.get('id', 'unknown')}: {e}")
            continue
    
    return STACItemCollection(filtered_items, provider=item_collection.provider)


def filter_by_cloud_cover(item_collection: STACItemCollection, max_cloud_cover: float) -> STACItemCollection:
    """Filter items by maximum cloud cover percentage."""
    filtered_items = []
    
    for item_data in item_collection._raw_items:
        cloud_cover = item_data.get('properties', {}).get('eo:cloud_cover')
        if cloud_cover is None or cloud_cover <= max_cloud_cover:
            filtered_items.append(item_data)
    
    return STACItemCollection(filtered_items, provider=item_collection.provider)


def filter_by_platform(item_collection: STACItemCollection, platforms: Union[str, List[str]]) -> STACItemCollection:
    """
    Filter items by platform/satellite.
    
    Args:
        item_collection: STACItemCollection to filter
        platforms: String or list of platform names
    
    Returns:
        STACItemCollection: Filtered collection
    """
    if isinstance(platforms, str):
        platforms = [platforms]
    
    platform_names = [p.lower() for p in platforms]
    filtered_items = []
    
    for item_data in item_collection._raw_items:
        properties = item_data.get('properties', {})
        item_platform = properties.get('platform') or properties.get('constellation')
        
        if item_platform and item_platform.lower() in platform_names:
            filtered_items.append(item_data)
    
    return STACItemCollection(filtered_items, provider=item_collection.provider)


def filter_by_collection(item_collection: STACItemCollection, collections: Union[str, List[str]]) -> STACItemCollection:
    """
    Filter items by collection ID.
    
    Args:
        item_collection: STACItemCollection to filter
        collections: String or list of collection IDs
    
    Returns:
        STACItemCollection: Filtered collection
    """
    if isinstance(collections, str):
        collections = [collections]
    
    filtered_items = []
    
    for item_data in item_collection._raw_items:
        item_collection_id = item_data.get('collection')
        if item_collection_id and item_collection_id in collections:
            filtered_items.append(item_data)
    
    return STACItemCollection(filtered_items, provider=item_collection.provider)


def apply_filters(item_collection: STACItemCollection, **filters) -> STACItemCollection:
    """
    🧠 INTELLIGENT: Apply multiple filters to a STACItemCollection.
    
    Args:
        item_collection: STACItemCollection to filter
        **filters: Filter parameters
    
    Filter Parameters:
        start_date: Start date for filtering
        end_date: End date for filtering
        geometry: Geometry for spatial filtering
        max_cloud_cover: Maximum cloud cover percentage
        platforms: Platform names for filtering
        collections: Collection IDs for filtering
    
    Returns:
        STACItemCollection: Filtered collection
    
    Example:
        filtered_items = apply_filters(
            items,
            start_date="2023-01-01",
            end_date="2023-12-31",
            geometry=[-122.5, 47.5, -122.0, 48.0],
            max_cloud_cover=20,
            platforms=["sentinel-2a", "sentinel-2b"]
        )
    """
    result = item_collection
    
    # Apply date range filter
    if 'start_date' in filters or 'end_date' in filters:
        start_date = filters.get('start_date')
        end_date = filters.get('end_date')
        result = filter_by_date_range(result, start_date, end_date)
    
    # Apply geometry filter
    if 'geometry' in filters:
        geometry = filters['geometry']
        result = filter_by_geometry(result, geometry)
    
    # Apply cloud cover filter
    if 'max_cloud_cover' in filters:
        max_cloud_cover = filters['max_cloud_cover']
        result = filter_by_cloud_cover(result, max_cloud_cover)
    
    # Apply platform filter
    if 'platforms' in filters:
        platforms = filters['platforms']
        result = filter_by_platform(result, platforms)
    
    # Apply collection filter
    if 'collections' in filters:
        collections = filters['collections']
        result = filter_by_collection(result, collections)
    
    return result
