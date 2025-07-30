from typing import Optional
import aiohttp
from pathlib import Path
from io import BytesIO

from ..types.assets import (
    AssetUploadInput,
    UploadAssetOptions,
    AssetUploadResult
)
from .asset_utils import create_json_request

async def upload_asset(
    file: AssetUploadInput,
    options: Optional[UploadAssetOptions] = None
) -> AssetUploadResult:
    """
    Upload an asset to the nanocore asset server.
    
    Args:
        file: The file to upload (path string, bytes, or file-like object)
        options: Optional configuration including type, metadata, and filename
    
    Returns:
        Information about the uploaded asset
    """
    options = options or {}
    
    # Prepare the file data
    data = aiohttp.FormData()
    
    filename = options.get('filename')
    
    if isinstance(file, str):
        path = Path(file)
        if not path.exists():
            raise ValueError(f'File not found: {file}')
        data.add_field('file', open(file, 'rb'), filename=filename)
    elif isinstance(file, bytes):
        data.add_field('file', BytesIO(file), filename=filename)
    else:  # file-like object
        data.add_field('file', file, filename=filename)
    
    # Add optional fields
    if options.get('type'):
        data.add_field('type', options['type'])
    if options.get('meta'):
        data.add_field('meta', str(options['meta']))
    
    return await create_json_request('/assets', method='POST', data=data) 