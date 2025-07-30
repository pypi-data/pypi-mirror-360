"""Tools for interacting with Grasshopper through socket connection."""
from mcp.server.fastmcp import FastMCP, Context, Image
import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Optional, Union
import json
import socket
import time
import re

# Configure logging
logger = logging.getLogger("GrasshopperTools")

def preprocess_llm_input(input_str: str) -> str:
    """Preprocess LLM input to handle common formatting issues."""
    return "{}"

def extract_payload_fields(raw_input: str) -> Dict[str, Any]:
    """Extract fields from a complex LLM payload."""
    return {}

def sanitize_json(json_str_or_dict: Union[str, Dict]) -> Dict[str, Any]:
    """Sanitize JSON input from LLM."""
    return {}

class GrasshopperConnection:
    """Handles socket connection to Grasshopper script."""
    
    def __init__(self, host='localhost', port=9999):  # Using port 9999 to match gh_socket_server.py
        self.host = host
        self.port = port
        self.socket = None
        self.timeout = 30.0
    
    def check_server_available(self) -> bool:
        """Check if the Grasshopper server is available."""
        return False
    
    def connect(self):
        """Connect to the Grasshopper script's socket server"""
        pass
    
    def disconnect(self):
        """Disconnect from the Grasshopper script"""
        pass
    
    def send_command(self, command_type: str, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        """Send a command to the Grasshopper script and wait for response"""
        return {}

# Global connection instance
_grasshopper_connection = None

def get_grasshopper_connection() -> GrasshopperConnection:
    """Get or create the Grasshopper connection"""
    global _grasshopper_connection
    if _grasshopper_connection is None:
        _grasshopper_connection = GrasshopperConnection()
    return _grasshopper_connection

class GrasshopperTools:
    """Collection of tools for interacting with Grasshopper."""
    
    def __init__(self, app):
        self.app = app
        self._register_tools()
    
    def _register_tools(self):
        """Register all Grasshopper tools with the MCP server."""
        self.app.tool()(self.is_server_available)
        self.app.tool()(self.execute_code_in_gh)
        self.app.tool()(self.get_gh_context)
        self.app.tool()(self.get_objects)
        self.app.tool()(self.get_selected)
        self.app.tool()(self.update_script)
        self.app.tool()(self.expire_and_get_info)
        self.app.tool()(self.recompute_all)
        self.app.tool()(self.add_slider_to_canvas)
        self.app.tool()(self.connect_components)
        self.app.tool()(self.add_component_to_canvas)
        self.app.tool()(self.get_all_component_proxies)
        self.app.tool()(self.remove_node)
        self.app.tool()(self.set_component_parameter)
        self.app.tool()(self.get_panel_content)
    
    def is_server_available(self, ctx: Context) -> bool:
        """Grasshopper: Check if the Grasshopper server is available.
        
        This is a quick check to see if the Grasshopper socket server is running
        and available for connections.
        
        Returns:
            bool: True if the server is available, False otherwise
        """
        return False
    
    def execute_code_in_gh(self, ctx: Context, code: str) -> str:
        """Grasshopper: Execute arbitrary Python code in Grasshopper.
        """
        return "{}"

    def get_gh_context(self, ctx: Context, simplified: bool = False) -> str:
        """Grasshopper: Get current Grasshopper document state and definition graph, sorted by execution order.
        """
        return "{}"

    def get_objects(self, ctx: Context, instance_guids: List[str], simplified: bool = False, context_depth: int = 0) -> str:
        """Grasshopper: Get information about specific components by their GUIDs.
        """
        return "{}"

    def get_selected(self, ctx: Context, simplified: bool = False, context_depth: int = 0) -> str:
        """Grasshopper: Get information about currently selected components.
        """
        return "{}"

    def update_script(self, ctx: Context, instance_guid: str = "", code: str = "", description: str = "", 
                     message_to_user: str = "", param_definitions: List[Dict[str, Any]] = []) -> str:
        """Grasshopper: Update a script component with new code, description, user feedback message, and optionally redefine its parameters.
        """
        return "{}"

    def expire_and_get_info(self, ctx: Context, instance_guid: str) -> str:
        """Grasshopper: Expire a specific component and get its updated information.
        """
        return "{}"

    def recompute_all(self, ctx: Context, instance_guid: str) -> str:
        """Grasshopper: Explicitly trigger recompute (expire) of a component by GUID. Returns only status/result, not full info."""
        return "{}"

    def add_slider_to_canvas(self, ctx: Context, name: str, min_value: float, max_value: float, value: float, position_x: int = 100, position_y: int = 100, integer: bool = False) -> str:
        """Add a slider to the Grasshopper canvas via MCP."""
        return "{}"

    def connect_components(self, ctx: Context, source_guid: str, source_output: str, target_guid: str, target_input: str) -> str:
        """Connect the output port of one component (or slider) to the input port of another via MCP. Sliders are now supported as sources."""
        return "{}"

    def add_component_to_canvas(self, ctx: Context, component_name: str, position_x: int = 100, position_y: int = 100) -> str:
        """Add a component to the Grasshopper canvas via MCP by exact name or nickname. Category filtering is handled on the server side via the component's currentCategoryFilter property."""
        return "{}"

    def remove_node(self, ctx: Context, instance_guid: str) -> str:
        """Remove a component or parameter from the Grasshopper canvas by its instance GUID."""
        return "{}"

    def get_all_component_proxies(self, ctx: Context, limit: int = 1000, filter: Optional[Union[str, Dict[str, str]]] = None, refresh: bool = False) -> str:
        """Get all Grasshopper component information (with caching and filtering), returned as a nested JSON grouped by Category and SubCategory: {Category: {SubCategory: [component_dicts]}}. The filter can be a string (name filter) or a dict with 'name' and/or 'category' keys (substring match, case-insensitive)."""
        return "{}"

    def get_all_component_library(self, ctx: Context) -> str:
        """Get all available Grasshopper components from the library."""
        return "{}"

    def set_component_parameter(self, ctx: Context, instance_guid: str = "", param_name: str = "", value: str = "") -> str:
        """Set a parameter value, supporting all major Grasshopper types and UI widgets (sliders, color swatches, boolean toggles).
        Always sends the set_component_parameter command to the backend, which will handle the logic for the specific UI type.
        """
        return "{}"

    def get_panel_content(self, ctx: Context, instance_guid: str) -> str:
        """Grasshopper: Get the content and properties of a Panel component. """
        return "{}" 