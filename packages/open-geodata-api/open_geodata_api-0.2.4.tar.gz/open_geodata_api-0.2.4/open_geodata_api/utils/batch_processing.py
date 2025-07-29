"""
Batch processing utilities for open-geodata-api
"""

import gc
from typing import Generator, Callable, Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from .download import download_single_file


def process_items_in_batches(items, batch_size: int = 10, 
                           process_func: Optional[Callable] = None,
                           **kwargs) -> Generator[Any, None, None]:
    """
    Process large collections of items in memory-efficient batches.
    
    Args:
        items: Items to process
        batch_size: Number of items per batch
        process_func: Function to apply to each batch
        **kwargs: Additional arguments for process_func
    
    Yields:
        Batch processing results
    """
    
    # Convert items to list if needed
    if hasattr(items, '__len__'):
        items_list = list(items)
    else:
        items_list = items
    
    total_items = len(items_list)
    
    for i in range(0, total_items, batch_size):
        batch = items_list[i:i + batch_size]
        
        try:
            if process_func:
                result = process_func(batch, **kwargs)
            else:
                result = batch
            
            yield result
            
            # Force garbage collection after each batch
            gc.collect()
            
        except Exception as e:
            print(f"Error processing batch {i//batch_size + 1}: {e}")
            yield {'error': str(e), 'batch_start': i, 'batch_size': len(batch)}


def parallel_download(urls_dict: Dict[str, str], destination: str,
                     max_workers: int = 4, timeout: int = 120,
                     **kwargs) -> Dict[str, Dict[str, Any]]:
    """
    Download multiple URLs in parallel with progress tracking.
    
    Args:
        urls_dict: Dictionary of URLs to download
        destination: Base destination directory
        max_workers: Maximum number of parallel workers
        timeout: Request timeout
        **kwargs: Additional download options
    
    Returns:
        Download results with success/failure status
    """
    
    results = {}
    
    def download_single_url(url_info):
        """Download a single URL with error handling."""
        url_key, url = url_info
        
        try:
            start_time = time.time()
            
            file_path = download_single_file(
                url, 
                destination,
                show_progress=kwargs.get('show_progress', False),
                **kwargs
            )
            
            download_time = time.time() - start_time
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            return url_key, {
                'success': True,
                'path': file_path,
                'size_bytes': file_size,
                'download_time': download_time,
                'url': url
            }
            
        except Exception as e:
            return url_key, {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    print(f"🚀 Starting parallel download of {len(urls_dict)} files with {max_workers} workers...")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all download tasks
        future_to_url = {
            executor.submit(download_single_url, url_info): url_info[0]
            for url_info in urls_dict.items()
        }
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            url_key = future_to_url[future]
            
            try:
                result_key, result_data = future.result(timeout=timeout)
                results[result_key] = result_data
                
                if result_data['success']:
                    print(f"✅ Downloaded: {result_key}")
                else:
                    print(f"❌ Failed: {result_key} - {result_data['error']}")
                    
            except Exception as e:
                results[url_key] = {
                    'success': False,
                    'error': f'Future execution failed: {e}',
                    'url': urls_dict[url_key]
                }
                print(f"❌ Failed: {url_key} - Future execution error")
    
    # Generate summary
    successful = sum(1 for r in results.values() if r.get('success', False))
    total = len(results)
    
    print(f"📊 Parallel download completed: {successful}/{total} successful")
    
    return results
