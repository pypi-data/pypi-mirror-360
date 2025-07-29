"""
Analysis utilities for open-geodata-api
"""

import numpy as np
import warnings
from typing import Dict, List, Optional, Union, Any
try:
    import rioxarray
    RIOXARRAY_AVAILABLE = True
except ImportError:
    RIOXARRAY_AVAILABLE = False


def calculate_ndvi(nir_url: str, red_url: str, output_path: Optional[str] = None):
    """
    Calculate NDVI from NIR and Red band URLs.
    
    Args:
        nir_url: URL to Near-Infrared band
        red_url: URL to Red band
        output_path: Optional path to save NDVI result
    
    Returns:
        NDVI data array
    """
    
    if not RIOXARRAY_AVAILABLE:
        raise ImportError("rioxarray is required for NDVI calculation. "
                         "Please install it via 'pip install rioxarray'")
    
    try:
        # Load the bands
        nir = rioxarray.open_rasterio(nir_url).squeeze()
        red = rioxarray.open_rasterio(red_url).squeeze()
        
        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        ndvi = (nir - red) / (nir + red + epsilon)
        
        # Clip NDVI values to valid range [-1, 1]
        ndvi = ndvi.clip(-1, 1)
        
        # Add metadata
        ndvi.attrs['long_name'] = 'Normalized Difference Vegetation Index'
        ndvi.attrs['units'] = 'dimensionless'
        ndvi.attrs['valid_range'] = [-1, 1]
        
        # Save if output path specified
        if output_path:
            ndvi.rio.to_raster(output_path)
            print(f"💾 NDVI saved to: {output_path}")
        
        return ndvi
        
    except Exception as e:
        raise Exception(f"NDVI calculation failed: {e}")


def get_statistics(data_array, percentiles: List[float] = [10, 25, 50, 75, 90]) -> Dict[str, float]:
    """
    Calculate comprehensive statistics for raster data arrays.
    
    Args:
        data_array: Input data array
        percentiles: Percentiles to calculate
    
    Returns:
        Dictionary of statistical measures
    """
    
    try:
        # Handle different input types
        if hasattr(data_array, 'values'):
            # xarray DataArray
            data = data_array.values
        elif hasattr(data_array, '__array__'):
            # numpy array or array-like
            data = np.array(data_array)
        else:
            raise ValueError("Input must be an array-like object")
        
        # Remove NaN and infinite values
        valid_data = data[np.isfinite(data)]
        
        if len(valid_data) == 0:
            warnings.warn("No valid data found in array")
            return {}
        
        # Calculate basic statistics
        stats = {
            'count': len(valid_data),
            'mean': float(np.mean(valid_data)),
            'std': float(np.std(valid_data)),
            'min': float(np.min(valid_data)),
            'max': float(np.max(valid_data)),
            'median': float(np.median(valid_data))
        }
        
        # Calculate percentiles
        for p in percentiles:
            stats[f'p{int(p)}'] = float(np.percentile(valid_data, p))
        
        # Additional statistics
        stats['range'] = stats['max'] - stats['min']
        stats['iqr'] = stats['p75'] - stats['p25']  # Interquartile range
        stats['cv'] = (stats['std'] / stats['mean'] * 100) if stats['mean'] != 0 else 0  # Coefficient of variation
        
        return stats
        
    except Exception as e:
        raise Exception(f"Statistics calculation failed: {e}")
