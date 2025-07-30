import os
import importlib.util
import glob
import logging
from typing import Dict, Optional, List
import asyncio

from .interfaces import NodeInstance, NodeDefinition

class NodeRegistry:
    def __init__(self, server_uid: str, logger: Optional[logging.Logger] = None):
        self.server_uid = server_uid
        self.nodes_map: Dict[str, NodeInstance] = {}
        self.initial_load_complete = False
        self.logger = logger or logging.getLogger(f"NanoSDK.NodeRegistry.{server_uid}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                f'[%(asctime)s] [%(levelname)s] [NanoSDK] @{self.server_uid} (NodeRegistry) %(message)s',
                '%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.propagate = False # Avoid duplicate logs if root logger also has handler
            self.logger.setLevel(logging.INFO)

    def register_node(self, node: NodeInstance, silent: bool = False) -> NodeInstance:
        uid = node['definition']['uid']
        if uid in self.nodes_map and not silent:
            self.logger.warning(f'Overwriting node with UID {uid}')
        self.nodes_map[uid] = node
        if not silent:
            self.logger.info(f'Found node "{node["definition"]["name"]}" ({uid})')
        return node

    async def load_node_definitions(self, nodes_path: str, silent: bool = False) -> None:
        abs_path = os.path.normpath(os.path.join(os.getcwd(), nodes_path))
        self.logger.info(f'Loading node definitions from: {abs_path}')

        if not os.path.isdir(abs_path):
            self.logger.warning(f'Nodes directory not found: {abs_path}. No nodes will be loaded from path.')
            if not self.initial_load_complete:
                self.initial_load_complete = True
            return

        pattern = os.path.join(abs_path, '**', 'node.py')
        entries = [
            f for f in glob.glob(pattern, recursive=True)
            if os.path.isfile(f) and 
               not os.path.basename(f).startswith('disabled.') and 
               not '.disabled.' in os.path.basename(f)
        ]

        self.logger.info(f'Found {len(entries)} potential node definition files (matching "node.py").')

        initial_node_count = len(self.nodes_map)
        nodes_loaded_this_run = 0

        if self.initial_load_complete and not silent:
            self.logger.info('Clearing existing dynamically loaded nodes for reload.')
            # Be careful here: only clear nodes that were dynamically loaded previously?
            # For now, simple clear. If static registration is mixed, this needs refinement.
            # Keep statically registered nodes.
            # This requires knowing which nodes are static vs dynamic.
            # Simplification: if a node file is changed, it will be re-registered.
            # If a node file is deleted, it wont be cleared by this logic if not handled by caller.
            # (Caller sdk.py handles clearing before non-silent reloads)
            pass # Static nodes are not cleared by this method, dynamic ones will be overwritten or added

        for abs_file_path in entries:
            module_name = f"nanosdk_node_{os.path.splitext(os.path.basename(abs_file_path))[0]}_{hash(abs_file_path)}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, abs_file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # sys.modules[module_name] = module # Add to sys.modules before exec
                    spec.loader.exec_module(module) # Nodes register themselves on import
                    
                    if hasattr(module, 'export'):
                        node_instance = module.export
                        if hasattr(module, 'init') and asyncio.iscoroutinefunction(module.init):
                            self.logger.info(f'Executing init function for node {node_instance["definition"]["uid"]}')
                            await module.init(node_instance)
                        elif hasattr(module, 'init'):
                            self.logger.warning(f'Found "init" function in {abs_file_path}, but it is not an async function. Skipping.')
                    
                    nodes_loaded_this_run +=1 # Assuming registration happens correctly
                else:
                    self.logger.error(f'Could not create spec for module from {abs_file_path}')
            except Exception as e:
                self.logger.error(f'Error loading node definition from {abs_file_path}: {e}')
                import traceback
                self.logger.error(traceback.format_exc())

        if not self.initial_load_complete:
            self.initial_load_complete = True
        
        current_node_count = len(self.nodes_map)
        action = 'Reloaded' if self.initial_load_complete and not silent else 'Loaded'
        if silent and self.initial_load_complete:
             action = 'Statically registered or updated'

        # For reloads, diff_count should represent newly found/updated from files
        # For initial load, it's just total from files
        diff_count = nodes_loaded_this_run 
        self.logger.info(f'{action} {diff_count} node definitions from files (total registered: {current_node_count})')

    def clear_nodes(self) -> None:
        # This should ideally only clear nodes loaded from files if we want to keep pre-registered ones.
        # For now, it clears all. This might need adjustment depending on SDK usage patterns.
        self.nodes_map.clear()
        self.initial_load_complete = False 
        self.logger.info('Cleared all node definitions from registry.')

    def get_node(self, uid: str) -> Optional[NodeInstance]:
        return self.nodes_map.get(uid)

    def get_all_definitions_for_client(self) -> List[NodeDefinition]:
        return [node['definition'] for node in self.nodes_map.values()]

    def get_node_count(self) -> int:
        return len(self.nodes_map) 