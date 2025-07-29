import os
from typing import Optional, Dict, TypeVar, Type, Any
import aiohttp
from aiohttp import ClientResponse

T = TypeVar('T')

def get_endpoint_and_token() -> tuple[str, str]:
    """Get the endpoint and token from environment variables."""
    endpoint = os.getenv('NANOCORE_ENDPOINT')
    token = os.getenv('NANOCORE_TOKEN')
    
    if not endpoint:
        raise RuntimeError('NANOCORE_ENDPOINT environment variable is not set')
    if not token:
        raise RuntimeError('NANOCORE_TOKEN environment variable is not set')
    
    return endpoint.rstrip('/'), token

async def create_request(
    path: str,
    method: str = 'GET',
    headers: Optional[Dict[str, str]] = None,
    data: Any = None
) -> ClientResponse:
    """Create and send an HTTP request."""
    endpoint, token = get_endpoint_and_token()
    url = f"{endpoint}{path}"
    
    headers = headers or {}
    headers['Authorization'] = f'Bearer {token}'
    
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, headers=headers, data=data) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise aiohttp.ClientError(f'Request failed: {response.status} {error_text}')
            return response

async def create_json_request(
    path: str,
    method: str = 'GET',
    headers: Optional[Dict[str, str]] = None,
    data: Any = None
) -> Dict:
    """Create and send an HTTP request, expecting JSON response."""
    timeout = aiohttp.ClientTimeout(total=300)  # 5 minutes timeout for file uploads
    async with aiohttp.ClientSession(timeout=timeout) as session:
        endpoint, token = get_endpoint_and_token()
        url = f"{endpoint.rstrip('/')}{path}"
        
        headers = headers or {}
        headers['Authorization'] = f'Bearer {token}'
        
        async with session.request(method, url, headers=headers, data=data) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise aiohttp.ClientError(f'Request failed: {response.status} {error_text}')
            
            # For file uploads, ensure the response is fully read before parsing
            if method == 'POST' and data is not None:
                # Read the response content first
                content = await response.read()
                try:
                    import json
                    return json.loads(content.decode('utf-8'))
                except Exception as e:
                    raise ValueError(f'Failed to parse response as JSON: {e}')
            else:
                try:
                    return await response.json()
                except Exception as e:
                    raise ValueError(f'Failed to parse response as JSON: {e}') 