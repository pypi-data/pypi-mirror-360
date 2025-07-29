import re
from typing import Optional, Union, List
import aiohttp
from urllib.parse import urlencode

from ..types.assets import (
    Asset,
    AssetFilter,
    AssetRef,
    ResolveAssetOptions,
    AssetPresignedUrl
)
from .asset_utils import get_endpoint_and_token, create_request, create_json_request

def parse_asset_ref(ref: str) -> Optional[AssetRef]:
    """Parse a nanocore asset reference URI into domain and UUID."""
    match = re.match(r'^nanocore://([^/]+)/asset/([a-fA-F0-9\-]+)$', ref)
    if not match:
        return None
    return {'domain': match.group(1), 'uuid': match.group(2)}

async def list_assets(filter: Optional[AssetFilter] = None) -> List[Asset]:
    """
    List assets with optional filtering.
    
    Args:
        filter: Optional filter by type and/or hash
    
    Returns:
        List of assets matching the filter
    """
    filter = filter or {}
    path = '/assets'
    if filter:
        path = f"{path}?{urlencode(filter)}"
    
    return await create_json_request(path)

async def resolve_asset(ref: str, options: Optional[ResolveAssetOptions] = None) -> Union[aiohttp.StreamReader, bytes]:
    """
    Resolve an asset reference to either a stream or buffer of data.
    
    Args:
        ref: The asset reference URI
        options: Optional configuration including as_buffer flag
    
    Returns:
        Either an aiohttp.StreamReader for streaming or bytes for buffer
    
    Raises:
        ValueError: If the asset reference is invalid
        RuntimeError: If environment variables are not set
        aiohttp.ClientError: If the HTTP request fails
    """
    options = options or {}
    parsed = parse_asset_ref(ref)
    if not parsed:
        raise ValueError('Invalid asset reference URI')
    
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout for large files
    async with aiohttp.ClientSession(timeout=timeout) as session:
        endpoint, token = get_endpoint_and_token()
        url = f"{endpoint}/assets/{parsed['uuid']}/download"
        headers = {'Authorization': f'Bearer {token}'}
        
        async with session.get(url, headers=headers) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise aiohttp.ClientError(f'Request failed: {response.status} {error_text}')
            
            if options.get('as_buffer', False):
                return await response.read()
            
            return response.content

def get_asset_download_url(ref: str) -> str:
    """Get the direct download URL for an asset."""
    parsed = parse_asset_ref(ref)
    if not parsed:
        raise ValueError('Invalid asset reference URI')
    
    endpoint, _ = get_endpoint_and_token()
    return f"{endpoint}/assets/{parsed['uuid']}/download"

async def get_asset_presigned_url(ref: str) -> AssetPresignedUrl:
    """
    Get a presigned URL for accessing an asset.
    
    Args:
        ref: The asset reference URI
    
    Returns:
        Dict containing the presigned URL and its expiration time
    
    Raises:
        ValueError: If the asset reference is invalid
        RuntimeError: If environment variables are not set
        aiohttp.ClientError: If the HTTP request fails
    """
    parsed = parse_asset_ref(ref)
    if not parsed:
        raise ValueError('Invalid asset reference URI')
    
    return await create_json_request(f"/assets/{parsed['uuid']}/presigned") 