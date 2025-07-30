import asyncio
import json
import logging
from typing import Callable, List, Set, Optional, Any, Coroutine, Union

import aiohttp
from aiohttp import web, WSMsgType
from websockets.server import WebSocketServerProtocol
from websockets.protocol import State

from .interfaces import NodeDefinition, HandshakeMessage, NanoServer, NodeDefinitionsMessage
from .message_handler import MessageHandler

class ServerInstance:
    def __init__(self,
                 domain: str,
                 server_name: str,
                 server_uid: str,
                 port: int,
                 get_definitions_fn: Callable[[], List[NodeDefinition]],
                 message_handler: MessageHandler,
                 logger: logging.Logger):
        
        self.domain = domain
        self.server_name = server_name
        self.server_uid = server_uid
        self.port = port
        self.get_definitions_fn = get_definitions_fn
        self.message_handler = message_handler
        self.logger = logger
        
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.site: Optional[web.TCPSite] = None
        self.clients: Set[web.WebSocketResponse] = set()
        self._stop_event = asyncio.Event()

    def emit_ready(self):
        """Signal that the server is ready"""
        print('[NANOSERVER_READY]', flush=True)

    async def _handle_root(self, request: web.Request) -> Union[web.Response, web.WebSocketResponse]:
        """Handle both HTTP and WebSocket requests on the root path"""
        # Check if this is a WebSocket upgrade request
        if (request.headers.get('Upgrade', '').lower() == 'websocket' and 
            request.headers.get('Connection', '').lower() == 'upgrade'):
            return await self._handle_websocket(request)
        else:
            return await self._handle_http(request)

    async def _handle_http(self, request: web.Request) -> web.Response:
        """Handle HTTP requests"""
        node_definitions = self.get_definitions_fn()
        node_uids = [defn['uid'] for defn in node_definitions]
        response_data = {
            'message': 'Nano Python Node Server is running',
            'domain': self.domain,
            'serverName': self.server_name,
            'serverUid': self.server_uid,
            'loadedNodes': len(node_uids),
            'nodeUIDs': node_uids
        }
        return web.json_response(response_data)

    async def _handle_websocket(self, request: web.Request) -> web.WebSocketResponse:
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        
        self.clients.add(ws)
        self.logger.info(f"Client connected from {request.remote}")
        
        try:
            # Send handshake message
            definitions_for_client = self.get_definitions_fn()
            handshake_payload = NanoServer(
                domain=self.domain,
                name=self.server_name,
                serverUid=self.server_uid,
                nodeDefinitions=definitions_for_client
            )
            handshake_message = HandshakeMessage(
                type='handshake',
                serverUid=self.server_uid,
                payload=handshake_payload
            )
            handshake_message_json = json.dumps(handshake_message)
            await ws.send_str(handshake_message_json)
            self.logger.info(f"Sent handshake message with {len(definitions_for_client)} node definitions to client {request.remote}")

            # Handle incoming messages
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    message_str = msg.data
                    self.logger.debug(f"Received message: {message_str[:100]}{'...' if len(message_str) > 100 else ''}")
                    await self.message_handler.process_message(message_str, ws)
                elif msg.type == WSMsgType.ERROR:
                    self.logger.error(f"WebSocket error: {ws.exception()}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in WebSocket connection handler for {request.remote}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        finally:
            self.clients.remove(ws)
            self.logger.info(f"Client {request.remote} disconnected. Remaining clients: {len(self.clients)}")
        
        return ws

    async def broadcast(self, message: NodeDefinitionsMessage):
        message_str = json.dumps(message)
        if self.clients:
            self.logger.info(f"Broadcasting definitions_update to {len(self.clients)} client(s).")
            # Create tasks for all send operations
            tasks = [client.send_str(message_str) for client in self.clients if not client.closed]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    client_list = list(self.clients)
                    if i < len(client_list):
                         self.logger.error(f"Error broadcasting to client: {result}")
                    else:
                         self.logger.error(f"Error broadcasting to a client (index out of bounds): {result}")      
        else:
            self.logger.info("No clients connected, skipping broadcast.")

    async def start(self):
        self._stop_event.clear()
        
        # Set up routes - single handler for both HTTP and WebSocket
        self.app.router.add_get('/', self._handle_root)
        
        # Create runner and site
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, '127.0.0.1', self.port)
        await self.site.start()
        
        self.logger.info(f"HTTP and WebSocket server started on port {self.port}")

    async def stop(self):
        self.logger.info("Stopping server...")
        self._stop_event.set()

        # Close all WebSocket connections
        if self.clients:
            self.logger.info(f"Closing {len(self.clients)} remaining client connections.")
            tasks = [client.close() for client in self.clients if not client.closed]
            await asyncio.gather(*tasks, return_exceptions=True)
            self.clients.clear()

        # Stop the server
        if self.site:
            await self.site.stop()
            self.site = None
        
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        
        self.logger.info("Server stopped.")


def create_server(
    domain: str,
    server_name: str,
    server_uid: str,
    port: int,
    get_definitions_fn: Callable[[], List[NodeDefinition]],
    message_handler: MessageHandler, # Changed from on_message callback to the full handler
    logger: Optional[logging.Logger] = None
) -> ServerInstance:
    
    effective_logger = logger or logging.getLogger(f"NanoSDK.Server.{server_uid}")
    if not effective_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'[%(asctime)s] [%(levelname)s] [NanoSDK] @{server_uid} (Server) %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        effective_logger.addHandler(handler)
        effective_logger.propagate = False
        effective_logger.setLevel(logging.INFO)

    return ServerInstance(
        domain=domain,
        server_name=server_name,
        server_uid=server_uid,
        port=port,
        get_definitions_fn=get_definitions_fn,
        message_handler=message_handler,
        logger=effective_logger
    ) 