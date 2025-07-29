"""
Error handling utilities for open-geodata-api
"""

import time
from typing import Dict, Any, Optional, List, Union
import requests


def handle_download_errors(error: Exception, retry_count: int = 0, 
                          max_retries: int = 3) -> Dict[str, Any]:
    """
    Intelligent error handling for download operations with retry logic.
    
    Args:
        error: Exception object to handle
        retry_count: Current retry attempt number
        max_retries: Maximum number of retry attempts
    
    Returns:
        Retry decision and suggested action
    """
    
    error_analysis = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'should_retry': False,
        'suggested_wait_time': 1,
        'suggested_action': 'none',
        'retry_count': retry_count,
        'description': 'Unknown error'
    }
    
    # Analyze different types of errors
    if isinstance(error, requests.exceptions.Timeout):
        error_analysis.update({
            'error_type': 'timeout',
            'should_retry': retry_count < max_retries,
            'suggested_wait_time': min(30, 5 * (retry_count + 1)),
            'suggested_action': 'increase_timeout',
            'description': 'Request timed out'
        })
    
    elif isinstance(error, requests.exceptions.ConnectionError):
        error_analysis.update({
            'error_type': 'connection_error',
            'should_retry': retry_count < max_retries,
            'suggested_wait_time': min(60, 10 * (retry_count + 1)),
            'suggested_action': 'check_network',
            'description': 'Network connection failed'
        })
    
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = getattr(error.response, 'status_code', 0)
        
        if status_code == 429:  # Too Many Requests
            error_analysis.update({
                'error_type': 'rate_limited',
                'should_retry': retry_count < max_retries,
                'suggested_wait_time': min(300, 60 * (retry_count + 1)),
                'suggested_action': 'reduce_concurrency',
                'description': 'Rate limited by server'
            })
        elif status_code in [500, 502, 503, 504]:  # Server errors
            error_analysis.update({
                'error_type': 'server_error',
                'should_retry': retry_count < max_retries,
                'suggested_wait_time': min(120, 30 * (retry_count + 1)),
                'suggested_action': 'retry_later',
                'description': f'Server error {status_code}'
            })
        elif status_code in [401, 403]:  # Authentication errors
            error_analysis.update({
                'error_type': 'authentication_error',
                'should_retry': False,
                'suggested_action': 'check_credentials',
                'description': f'Authentication failed {status_code}'
            })
        elif status_code == 404:  # Not found
            error_analysis.update({
                'error_type': 'not_found',
                'should_retry': False,
                'suggested_action': 'check_url',
                'description': 'Resource not found'
            })
    
    elif isinstance(error, FileNotFoundError):
        error_analysis.update({
            'error_type': 'file_not_found',
            'should_retry': False,
            'suggested_action': 'check_path',
            'description': 'Local file or directory not found'
        })
    
    elif isinstance(error, PermissionError):
        error_analysis.update({
            'error_type': 'permission_error',
            'should_retry': False,
            'suggested_action': 'check_permissions',
            'description': 'Insufficient permissions'
        })
    
    return error_analysis


def validate_inputs(items=None, bbox: Optional[List[float]] = None,
                   datetime: Optional[str] = None,
                   collections: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate input parameters for STAC operations.
    
    Args:
        items: STAC items to validate
        bbox: Bounding box to validate
        datetime: Date range to validate
        collections: Collection names to validate
    
    Returns:
        Validation results with detailed feedback
    """
    
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }
    
    # Validate bounding box
    if bbox is not None:
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            validation_result['valid'] = False
            validation_result['errors'].append("Bounding box must be a list/tuple of 4 numbers [west, south, east, north]")
        else:
            try:
                west, south, east, north = [float(x) for x in bbox]
                
                if not (-180 <= west <= 180) or not (-180 <= east <= 180):
                    validation_result['valid'] = False
                    validation_result['errors'].append("Longitude values must be between -180 and 180")
                
                if not (-90 <= south <= 90) or not (-90 <= north <= 90):
                    validation_result['valid'] = False
                    validation_result['errors'].append("Latitude values must be between -90 and 90")
                
                if west >= east:
                    validation_result['valid'] = False
                    validation_result['errors'].append("West longitude must be less than east longitude")
                
                if south >= north:
                    validation_result['valid'] = False
                    validation_result['errors'].append("South latitude must be less than north latitude")
                
                # Check for reasonable size
                bbox_area = (east - west) * (north - south)
                if bbox_area > 180 * 90:  # Very large area
                    validation_result['warnings'].append("Bounding box covers a very large area - consider smaller regions")
                
            except (ValueError, TypeError):
                validation_result['valid'] = False
                validation_result['errors'].append("Bounding box values must be numeric")
    
    # Validate datetime
    if datetime is not None:
        if not isinstance(datetime, str):
            validation_result['valid'] = False
            validation_result['errors'].append("Datetime must be a string")
        else:
            # Check for common datetime formats
            if '/' in datetime:
                # Date range format
                parts = datetime.split('/')
                if len(parts) != 2:
                    validation_result['warnings'].append("Date range should have format 'start/end'")
            elif datetime.isdigit():
                # Number of days
                days = int(datetime)
                if days > 3650:  # > 10 years
                    validation_result['warnings'].append("Very large number of days specified")
    
    # Validate collections
    if collections is not None:
        if isinstance(collections, str):
            collections = [collections]
        
        if not isinstance(collections, list):
            validation_result['valid'] = False
            validation_result['errors'].append("Collections must be a string or list of strings")
        else:
            if len(collections) == 0:
                validation_result['valid'] = False
                validation_result['errors'].append("At least one collection must be specified")
            
            # Check for common collection names
            known_collections = ['sentinel-2-l2a', 'landsat-c2-l2', 'sentinel-1-grd']
            unknown_collections = [c for c in collections if c not in known_collections]
            if unknown_collections:
                validation_result['warnings'].append(f"Unknown collections: {unknown_collections}")
    
    # Validate items
    if items is not None:
        if hasattr(items, '__len__'):
            if len(items) == 0:
                validation_result['warnings'].append("No items provided")
            elif len(items) > 1000:
                validation_result['warnings'].append("Large number of items - consider processing in batches")
    
    # Generate suggestions
    if validation_result['errors']:
        validation_result['suggestions'].append("Fix the errors above before proceeding")
    
    if validation_result['warnings']:
        validation_result['suggestions'].append("Review warnings for potential issues")
    
    return validation_result
