"""
Configuration management for open-geodata-api
"""

from typing import Any, Dict, Optional
import json
import os
from pathlib import Path


# Global configuration storage
_GLOBAL_CONFIG = {
    'default_provider': 'planetary_computer',
    'auto_sign_urls': True,
    'max_download_workers': 4,
    'default_timeout': 120,
    'cache_size_mb': 256,
    'progress_bar': True,
    'verbose_errors': False,
    'debug_mode': False,
    'retry_attempts': 3,
    'chunk_size': 8192
}


def set_global_config(**config_params) -> Dict[str, Any]:
    """
    Set global configuration parameters for the library.
    
    Args:
        **config_params: Configuration parameters to set
    
    Returns:
        Updated configuration dictionary
    """
    
    global _GLOBAL_CONFIG
    
    # Validate and update configuration
    for key, value in config_params.items():
        if key in _GLOBAL_CONFIG:
            _GLOBAL_CONFIG[key] = value
        else:
            print(f"Warning: Unknown configuration parameter '{key}' - adding to config")
            _GLOBAL_CONFIG[key] = value
    
    # Save to config file if possible
    try:
        config_dir = Path.home() / '.open_geodata_api'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'config.json'
        
        with open(config_file, 'w') as f:
            json.dump(_GLOBAL_CONFIG, f, indent=2)
            
    except Exception as e:
        print(f"Warning: Could not save configuration to file: {e}")
    
    return _GLOBAL_CONFIG.copy()


def get_global_config(key: Optional[str] = None) -> Any:
    """
    Get global configuration parameters.
    
    Args:
        key: Specific configuration key (None for all)
    
    Returns:
        Configuration value or full configuration
    """
    
    global _GLOBAL_CONFIG
    
    # Try to load from config file if not already loaded
    if len(_GLOBAL_CONFIG) == 0:
        try:
            config_file = Path.home() / '.open_geodata_api' / 'config.json'
            if config_file.exists():
                with open(config_file, 'r') as f:
                    _GLOBAL_CONFIG.update(json.load(f))
        except Exception:
            pass  # Use default config
    
    if key is None:
        return _GLOBAL_CONFIG.copy()
    else:
        return _GLOBAL_CONFIG.get(key)


def optimize_for_large_datasets(dataset_size_gb: float, 
                               available_memory_gb: float) -> Dict[str, Any]:
    """
    Optimize library settings for large dataset processing.
    
    Args:
        dataset_size_gb: Expected dataset size in GB
        available_memory_gb: Available system memory in GB
    
    Returns:
        Optimized configuration recommendations
    """
    
    # Calculate optimal settings
    memory_per_worker_mb = (available_memory_gb * 1024) / 8  # Conservative estimate
    max_workers = min(8, max(1, int(available_memory_gb / 2)))  # 2GB per worker
    
    if dataset_size_gb > available_memory_gb * 2:
        # Large dataset strategy
        strategy = "memory_efficient"
        batch_size = max(1, int(available_memory_gb / dataset_size_gb * 100))
        chunk_size = 16384  # Smaller chunks
        
    elif dataset_size_gb > available_memory_gb:
        # Medium dataset strategy
        strategy = "balanced"
        batch_size = max(5, int(available_memory_gb / dataset_size_gb * 500))
        chunk_size = 32768  # Medium chunks
        
    else:
        # Small dataset strategy
        strategy = "performance"
        batch_size = 20
        chunk_size = 65536  # Large chunks
    
    optimization = {
        'strategy': strategy,
        'batch_size': batch_size,
        'max_workers': max_workers,
        'memory_per_worker_mb': memory_per_worker_mb,
        'config': {
            'max_download_workers': max_workers,
            'chunk_size': chunk_size,
            'progress_bar': True,
            'verbose_errors': False
        }
    }
    
    return optimization
