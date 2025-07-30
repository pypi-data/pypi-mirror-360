import asyncio
import logging
import os
from typing import Callable, List, Set, Optional, Coroutine, Any, TYPE_CHECKING

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent

# TYPE_CHECKING block can be removed if Observer is directly imported and no other specific type hints need it.
# if TYPE_CHECKING:
#     pass

from .interfaces import NodeDefinition, NodeDefinitionsMessage

# Assuming websockets.WebSocketServerProtocol for type hinting connected clients if needed for direct broadcast
# For simplicity, we'll pass a callable to send messages to clients, abstracting WebSocket details.

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self,
                 domain: str,
                 server_uid: str,
                 nodes_path: str,
                 reload_nodes_fn: Callable[[], Coroutine[Any, Any, None]],
                 get_definitions_for_client_fn: Callable[[], List[NodeDefinition]],
                 broadcast_fn: Callable[[NodeDefinitionsMessage], Coroutine[Any, Any, None]],
                 debounce_time: float, # seconds
                 logger: logging.Logger):
        super().__init__()
        self.domain = domain
        self.server_uid = server_uid
        self.nodes_path = nodes_path # Absolute path
        self.reload_nodes_fn = reload_nodes_fn
        self.get_definitions_for_client_fn = get_definitions_for_client_fn
        self.broadcast_fn = broadcast_fn
        self.debounce_time = debounce_time
        self.logger = logger
        self._debounce_timer: Optional[asyncio.TimerHandle] = None
        self._loop = asyncio.get_event_loop() # Get loop in the thread where handler is created

    def on_any_event(self, event):
        if event.is_directory:
            return
        
        # Only react to actual modifications
        if event.event_type not in ['modified', 'created', 'moved']:
            return
        
        # Process only .py files that are not __init__.py or dunder files
        src_path = event.src_path
        if isinstance(event, FileMovedEvent):
            # For moved events, also check the destination path if relevant
            # However, watchdog often fires created/deleted for moves anyway.
            # We are interested if the new path is a .py file or old path was.
            dest_path = event.dest_path
            is_relevant_change = (src_path.endswith('.py') and not os.path.basename(src_path).startswith('__')) or \
                                 (dest_path.endswith('.py') and not os.path.basename(dest_path).startswith('__'))
        else:
            is_relevant_change = src_path.endswith('.py') and not os.path.basename(src_path).startswith('__')

        if is_relevant_change:
            self.logger.info(f"File change detected: {event.event_type} - {src_path}")
            if self._debounce_timer:
                self._debounce_timer.cancel()
            
            # Schedule the _handle_change on the event loop where the SDK runs
            self._debounce_timer = self._loop.call_later(self.debounce_time, 
                                                        lambda: asyncio.run_coroutine_threadsafe(self._handle_change(), self._loop))

    async def _handle_change(self):
        self.logger.info("Debounced file change: Reloading node definitions...")
        try:
            await self.reload_nodes_fn()
            updated_definitions = self.get_definitions_for_client_fn()
            
            update_message: NodeDefinitionsMessage = {
                'type': 'definitions_update',
                'serverUid': self.server_uid,
                'payload': {
                    'nodeDefinitions': updated_definitions
                }
            }
            await self.broadcast_fn(update_message)
            self.logger.info(f"Sent definitions_update with {len(updated_definitions)} nodes.")

        except Exception as e:
            self.logger.error(f"Error processing file change: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

def start_file_watcher(
    domain: str,
    server_uid: str,
    nodes_path: str, # Relative path from CWD
    reload_nodes_fn: Callable[[], Coroutine[Any, Any, None]],
    get_definitions_for_client_fn: Callable[[], List[NodeDefinition]],
    broadcast_fn: Callable[[NodeDefinitionsMessage], Coroutine[Any, Any, None]],
    debounce_time: int = 500, # milliseconds
    logger: Optional[logging.Logger] = None
) -> Optional['Observer']: # type: ignore[name-defined] # Revert to string literal and add type ignore
    
    effective_logger = logger or logging.getLogger(f"NanoSDK.FileWatcher.{server_uid}")
    if not effective_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            f'[%(asctime)s] [%(levelname)s] [NanoSDK] @{server_uid} (FileWatcher) %(message)s',
            '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        effective_logger.addHandler(handler)
        effective_logger.propagate = False
        effective_logger.setLevel(logging.INFO)

    abs_nodes_path = os.path.normpath(os.path.join(os.getcwd(), nodes_path))

    if not os.path.isdir(abs_nodes_path):
        effective_logger.warning(f"Directory not found, not watching: {abs_nodes_path}")
        return None

    effective_logger.info(f"Watching for file changes in {abs_nodes_path}")
    
    event_handler = FileChangeHandler(
        domain=domain,
        server_uid=server_uid,
        nodes_path=abs_nodes_path,
        reload_nodes_fn=reload_nodes_fn,
        get_definitions_for_client_fn=get_definitions_for_client_fn,
        broadcast_fn=broadcast_fn,
        debounce_time=float(debounce_time / 1000.0), # watchdog uses seconds
        logger=effective_logger
    )
    
    observer = Observer()
    observer.schedule(event_handler, abs_nodes_path, recursive=True)
    observer.start()
    effective_logger.info("File watcher started.")
    return observer 