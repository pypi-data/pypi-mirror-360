"""
Utility functions for open-geodata-api
"""

from .filters import (
    filter_by_cloud_cover,
    filter_by_date_range,
    filter_by_geometry,
    filter_by_platform,
    filter_by_collection,
    apply_filters
)

from .download import (
    download_datasets,
    download_url,
    download_from_json,
    download_seasonal,
    download_single_file,
    download_url_dict,
    download_items,
    download_seasonal_data,
    create_download_summary,
    is_url_expired,
    is_signed_url,
    re_sign_url_if_needed
)

from .url_management import (
    validate_urls
)

from .data_processing import (
    export_urls_to_json
)

from .batch_processing import (
    process_items_in_batches,
    parallel_download
)

from .analysis import (
    calculate_ndvi,
    get_statistics
)

from .error_handling import (
    handle_download_errors,
    validate_inputs
)

from .config import (
    set_global_config,
    get_global_config,
    optimize_for_large_datasets
)

__all__ = [
    # Filtering functions
    'filter_by_cloud_cover',
    'filter_by_date_range',
    'filter_by_geometry',
    'filter_by_platform',
    'filter_by_collection',
    'apply_filters',
    
    # Download functions
    'download_datasets',
    'download_url',
    'download_from_json',
    'download_seasonal',
    'download_single_file',
    'download_url_dict',
    'download_items',
    'download_seasonal_data',
    'create_download_summary',
    
    # URL management
    'is_url_expired',
    'is_signed_url',
    're_sign_url_if_needed',
    'validate_urls',
    
    # Data processing
    'export_urls_to_json',
    
    # Batch processing
    'process_items_in_batches',
    'parallel_download',
    
    # Analysis helpers
    'calculate_ndvi',
    'get_statistics',
    
    # Error handling
    'handle_download_errors',
    'validate_inputs',
    
    # Configuration
    'set_global_config',
    'get_global_config',
    'optimize_for_large_datasets'
]
