"""Rhino integration through the Model Context Protocol."""
from mcp.server.fastmcp import FastMCP, Context, Image
import logging
import os
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List, Optional
import json
import io
from PIL import Image as PILImage
from pathlib import Path
import importlib

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        logging.info(f"Loaded environment variables from {env_path}")
except ImportError:
    logging.warning("python-dotenv not installed. Install it to use .env files: pip install python-dotenv")

# Import our tool modules
from .rhino_tools import RhinoTools, get_rhino_connection
from .grasshopper_tools import GrasshopperTools, get_grasshopper_connection

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("RhinoMCPServer")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    rhino_conn = None
    gh_conn = None
    
    try:
        logger.info("RhinoMCP server starting up")
        
        # Try to connect to Rhino script
        try:
            rhino_conn = get_rhino_connection()
            rhino_conn.connect()
            logger.info("Successfully connected to Rhino script")
        except Exception as e:
            logger.warning("Could not connect to Rhino script: {0}".format(str(e)))
        
        # Try to connect to Grasshopper script
        try:
            gh_conn = get_grasshopper_connection()
            # Just check if the server is available - don't connect yet
            if gh_conn.check_server_available():
                logger.info("Grasshopper server is available")
            else:
                logger.warning("Grasshopper server is not available. Start the GHPython component in Grasshopper to enable Grasshopper integration.")
        except Exception as e:
            logger.warning("Error checking Grasshopper server availability: {0}".format(str(e)))
        
        yield {}
    finally:
        logger.info("RhinoMCP server shut down")
        
        # Clean up connections
        if rhino_conn:
            try:
                rhino_conn.disconnect()
                logger.info("Disconnected from Rhino script")
            except Exception as e:
                logger.warning("Error disconnecting from Rhino: {0}".format(str(e)))
        
        if gh_conn:
            try:
                gh_conn.disconnect()
                logger.info("Disconnected from Grasshopper script")
            except Exception as e:
                logger.warning("Error disconnecting from Grasshopper: {0}".format(str(e)))

# Create the MCP server with lifespan support
app = FastMCP(
    "RhinoMCP",
    description="Rhino integration through the Model Context Protocol",
    lifespan=server_lifespan
)

def load_tools(app, tool_names):
    tool_map = {
        "rhino": ("rhino_gh_mcp_uv.rhino_tools", "RhinoTools"),
        "grasshopper": ("rhino_gh_mcp_uv.grasshopper_tools", "GrasshopperTools"),
    }
    loaded = {}
    for name in tool_names:
        if name in tool_map:
            module_name, class_name = tool_map[name]
            module = importlib.import_module(module_name)
            tool_class = getattr(module, class_name)
            loaded[name] = tool_class(app)
    return loaded
def main(tools="grasshopper"):
    """Run the MCP server with dynamic tool loading"""
    if tools == "all":
        tool_names = ["rhino", "grasshopper", "replicate", "utility"]
    else:
        tool_names = [t.strip() for t in tools.split(",") if t.strip()]
    load_tools(app, tool_names)
    app.run(transport='stdio')

if __name__ == "__main__":
    main()