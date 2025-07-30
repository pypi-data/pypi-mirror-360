import asyncio
import functools
from typing import Optional, Dict, Any, Union
from geopandas import GeoDataFrame
from shapely.geometry.base import BaseGeometry as ShapelyGeometry
from .async_client import AsyncClient
from typing import Dict


def sync_wrapper(async_func):
    """
    Decorator to convert async functions to sync functions.
    """
    @functools.wraps(async_func)
    def wrapper(*args, **kwargs):
        # Get or create event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                return future.result()
        except RuntimeError:
            # No running loop, we can create a new one
            return asyncio.run(async_func(*args, **kwargs))
    return wrapper


class SyncWrapper:
    """
    Generic synchronous wrapper for any async object.
    Automatically converts all async methods to sync using __getattr__.
    """
    
    def __init__(self, async_obj, sync_client):
        self._async_obj = async_obj
        self._sync_client = sync_client
    
    def __getattr__(self, name):
        """
        Dynamically wrap any method call to convert async to sync.
        """
        attr = getattr(self._async_obj, name)
        
        # If it's a callable (method), wrap it
        if callable(attr):
            def sync_wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                # If the result is a coroutine, run it synchronously
                if hasattr(result, '__await__'):
                    return self._sync_client._run_async(result)
                return result
            return sync_wrapper
        
        # If it's not a callable (like a property), return as-is
        return attr


class SyncClient:
    """
    Synchronous wrapper around AsyncClient that converts all async methods to sync.
    Uses the AsyncClient as a context manager to properly handle session lifecycle.
    """
    
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None, verbose: bool = False):
        """
        Initialize the synchronous client.
        
        Args:
            url (Optional[str]): The API base URL
            api_key (Optional[str]): The API key for authentication
            verbose (bool): Whether to enable verbose logging
        """
        self._async_client = AsyncClient(url=url, api_key=api_key, verbose=verbose)
        self._context_entered = False
        self._closed = False
        
        # Initialize endpoint managers
        self._init_endpoints()
        
        # Register cleanup on exit
        import atexit
        atexit.register(self._cleanup)

    def __getattr__(self, name):
        """
        Delegate attribute access to the underlying async client.
        """
        if hasattr(self._async_client, name):
            attr = getattr(self._async_client, name)
            
            # If it's a callable (method), wrap it to run synchronously
            if callable(attr):
                def sync_method(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    # If the result is a coroutine, run it synchronously
                    if hasattr(result, '__await__'):
                        return self._run_async(result)
                    return result
                return sync_method
            
            # If it's not a callable (like a property), return as-is
            return attr
        
        # If the attribute doesn't exist, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    async def _ensure_context(self):
        """Ensure the async client context is entered."""
        if not self._context_entered and not self._closed:
            await self._async_client.__aenter__()
            self._context_entered = True
    
    async def _exit_context(self):
        """Exit the async client context."""
        if self._context_entered and not self._closed:
            await self._async_client.__aexit__(None, None, None)
            self._context_entered = False
    
    def _run_async(self, coro):
        """
        Run an async coroutine and return the result synchronously.
        Ensures the AsyncClient context is properly managed.
        """
        async def run_with_context():
            await self._ensure_context()
            return await coro
        
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, run in a new thread
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, run_with_context())
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            return asyncio.run(run_with_context())
    
    def _run_async_single_use(self, coro):
        """
        Run an async coroutine with its own context manager for one-off operations.
        This is useful when you don't want to maintain a persistent session.
        """
        async def run_with_own_context():
            async with self._async_client:
                return await coro
        
        try:
            loop = asyncio.get_running_loop()
            # If we're already in an async context, run in a new thread
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, run_with_own_context())
                return future.result()
        except RuntimeError:
            # No running loop, create a new one
            return asyncio.run(run_with_own_context())
    
    def geoquery(
        self,
        expr: str,
        feature: Union[Dict[str, Any], ShapelyGeometry],
        in_crs: str = "epsg:4326",
        out_crs: str = "epsg:4326",
        resolution: int = -1,
        geom_fix: bool = False,
        **kwargs
    ):
        """
        Compute WCS query for a single geometry (synchronous version).

        Args:
            expr (str): The WCS expression to evaluate
            feature (Union[Dict[str, Any], ShapelyGeometry]): The geographic feature
            in_crs (str): Input coordinate reference system
            out_crs (str): Output coordinate reference system
            resolution (int): Resolution parameter
            geom_fix (bool): Whether to fix the geometry (default False)
            **kwargs: Additional parameters to pass to the WCS request
            
        Returns:
            Union[pd.DataFrame, xr.Dataset, bytes]: The response data in the requested format

        Raises:
            APIError: If the API request fails
        """
        coro = self._async_client.geoquery(
            expr=expr,
            feature=feature,
            in_crs=in_crs,
            out_crs=out_crs,
            output="netcdf",
            resolution=resolution,
            geom_fix=geom_fix,
            **kwargs
        )
        return self._run_async(coro)
    
    def zonal_stats(
        self,
        gdf: GeoDataFrame,
        expr: str,
        conc: int = 20,
        inplace: bool = False,
        in_crs: str = "epsg:4326",
        out_crs: str = "epsg:4326",
        resolution: int = -1,
        geom_fix: bool = False,
    ):
        """
        Compute zonal statistics for all geometries in a GeoDataFrame (synchronous version).

        Args:
            gdf (GeoDataFrame): GeoDataFrame containing geometries
            expr (str): Terrakio expression to evaluate, can include spatial aggregations
            conc (int): Number of concurrent requests to make
            inplace (bool): Whether to modify the input GeoDataFrame in place
            in_crs (str): Input coordinate reference system
            out_crs (str): Output coordinate reference system
            resolution (int): Resolution parameter
            geom_fix (bool): Whether to fix the geometry (default False)
            
        Returns:
            geopandas.GeoDataFrame: GeoDataFrame with added columns for results, or None if inplace=True

        Raises:
            ValueError: If concurrency is too high
            APIError: If the API request fails
        """
        coro = self._async_client.zonal_stats(
            gdf=gdf,
            expr=expr,
            conc=conc,
            inplace=inplace,
            in_crs=in_crs,
            out_crs=out_crs,
            resolution=resolution,
            geom_fix=geom_fix
        )
        return self._run_async(coro)
    
    def create_dataset_file(
        self,
        aoi: str,
        expression: str,
        output: str,
        in_crs: str = "epsg:4326",
        res: float = 0.0001,
        region: str = "aus",
        to_crs: str = "epsg:4326",
        overwrite: bool = True,
        skip_existing: bool = False,
        non_interactive: bool = True,
        poll_interval: int = 30,
        download_path: str = "/home/user/Downloads",
    ) -> dict:
        """
        Create a dataset file using mass stats operations (synchronous version).

        Args:
            aoi (str): Area of interest
            expression (str): Terrakio expression to evaluate
            output (str): Output format
            in_crs (str): Input coordinate reference system (default "epsg:4326")
            res (float): Resolution (default 0.0001)
            region (str): Region (default "aus")
            to_crs (str): Target coordinate reference system (default "epsg:4326")
            overwrite (bool): Whether to overwrite existing files (default True)
            skip_existing (bool): Whether to skip existing files (default False)
            non_interactive (bool): Whether to run non-interactively (default True)
            poll_interval (int): Polling interval in seconds (default 30)
            download_path (str): Download path (default "/home/user/Downloads")

        Returns:
            dict: Dictionary containing generation_task_id and combine_task_id

        Raises:
            ConfigurationError: If mass stats client is not properly configured
            RuntimeError: If job fails
        """
        coro = self._async_client.create_dataset_file(
            aoi=aoi,
            expression=expression,
            output=output,
            in_crs=in_crs,
            res=res,
            region=region,
            to_crs=to_crs,
            overwrite=overwrite,
            skip_existing=skip_existing,
            non_interactive=non_interactive,
            poll_interval=poll_interval,
            download_path=download_path,
        )
        return self._run_async(coro)
    
    def close(self):
        """
        Close the underlying async client session (synchronous version).
        """
        if not self._closed:
            async def close_async():
                await self._exit_context()
            
            try:
                loop = asyncio.get_running_loop()
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, close_async())
                    future.result()
            except RuntimeError:
                asyncio.run(close_async())
            
            self._closed = True
    
    def _cleanup(self):
        """Internal cleanup method called by atexit."""
        if not self._closed:
            try:
                self.close()
            except Exception:
                # Ignore errors during cleanup
                pass
    
    def __enter__(self):
        """Context manager entry."""
        # Ensure context is entered when used as context manager
        async def enter_async():
            await self._ensure_context()
        
        try:
            loop = asyncio.get_running_loop()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, enter_async())
                future.result()
        except RuntimeError:
            asyncio.run(enter_async())
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Destructor to ensure session is closed when object is garbage collected."""
        if not self._closed:
            try:
                self._cleanup()
            except Exception:
                # If we can't close gracefully, ignore the error during cleanup
                pass
    
    # Initialize endpoint managers (these can be overridden by subclasses)
    def _init_endpoints(self):
        """Initialize endpoint managers. Can be overridden by subclasses."""
        self.datasets = SyncWrapper(self._async_client.datasets, self)
        self.users = SyncWrapper(self._async_client.users, self)
        self.mass_stats = SyncWrapper(self._async_client.mass_stats, self)
        self.groups = SyncWrapper(self._async_client.groups, self)
        self.space = SyncWrapper(self._async_client.space, self)
        self.model = SyncWrapper(self._async_client.model, self)
        self.auth = SyncWrapper(self._async_client.auth, self)