"""
TwinFabric MCP Server

A simple MCP server for interacting with TwinFabric.
"""

import logging
import requests
import sys
import os
import json
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional
from fastmcp import FastMCP
import struct
from importlib import metadata

# 获取指定包的版本号
package_name = "datav-twinFabric-mcp"
version = metadata.version(package_name)

# Configure logging with more detailed format
log_dir = os.getenv("LOG_DIR", "./logs")
log_file = os.path.join(log_dir, "TwinFabric_mcp.log")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # 如果目录不存在，则创建
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG level for more details
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        # logging.StreamHandler(sys.stdout) # Remove this handler to unexpected non-whitespace characters in JSON
    ]
)
logger = logging.getLogger("TwinFabricMCP")

# Configuration
PROXY_HOST = os.getenv("TwinFabricHost", "8.149.237.145")
PROXY_PORT = os.getenv("TwinFabricPort", "3333")

UNREAL_CLIENTID = os.getenv("UnrealClientId", "ue-666")
logger.info(f"--------------------------------------{package_name} version: {version} ----------------------------------------")
logger.info(f"--------------------------------------UNREAL_CLIENTID version: {UNREAL_CLIENTID} ---------------------------------")

class TwinFabricConnection:
    """Connection to an TwinFabric instance."""
    
    def __init__(self):
        """Initialize the connection."""
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to the TwinFabric instance."""
        logger.info("Connected to TwinFabric Engine")
        return True
    
    def disconnect(self):
        """Disconnect from the TwinFabric Engine instance."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False
 
    def send_command(self, command: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send a command to TwinFabric Engine and get the response."""
        # Always reconnect for each command, since TwinFabric closes the connection after each command
        
        # Send command to TwinFabric
        url = f"http://{PROXY_HOST}:{PROXY_PORT}/proxy"

        # Match Unity's command format exactly
        data = {
            "clientId": UNREAL_CLIENTID,
            "data": {
                "type": command,  # Use "type" instead of "command"
                "params": params or {}  # Use Unity's params or {} pattern
            }
        }            
        
        # Send without newline, exactly like Unity
        data_json = json.dumps(data)
        logger.info(f"Sending command: {data_json}")
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, data=data_json, headers=headers, timeout=(60, 300))
        
            # Log complete response for debugging
            logger.info(f"Complete response from TwinFabric: {response.status_code} | {response.json()}")

            # Check for both error formats: {"status": "error", ...} and {"success": false, ...}
            if response.status_code == 200:
                response = response.json()
            else:
                response = {
                    "status": "error",
                    "error": response.json()
                }
            return response
        except Exception as e:
            logger.error(f"Error getting TwinFabric connection: {e}")
            return None

# Global connection state
_twin_fabric_connection: TwinFabricConnection = None

def get_twinfabric_connection() -> Optional[TwinFabricConnection]:
    """Get the connection to TwinFabric Engine."""
    global _twin_fabric_connection
    try:
        if _twin_fabric_connection is None:
            _twin_fabric_connection = TwinFabricConnection()
            if not _twin_fabric_connection.connect():
                logger.warning("Could not connect to TwinFabric Engine")
                _twin_fabric_connection = None
        else:
            # Verify connection is still valid with a ping-like test
            try:
                # Simple test by sending an empty buffer to check if socket is still connected
                _twin_fabric_connection.socket.sendall(b'\x00')
                logger.debug("Connection verified with ping test")
            except Exception as e:
                logger.warning(f"Existing connection failed: {e}")
                _twin_fabric_connection.disconnect()
                _twin_fabric_connection = None
                # Try to reconnect
                _twin_fabric_connection = TwinFabricConnection()
                if not _twin_fabric_connection.connect():
                    logger.warning("Could not reconnect to TwinFabric Engine")
                    _twin_fabric_connection = None
                else:
                    logger.info("Successfully reconnected to TwinFabric Engine")
        
        return _twin_fabric_connection
    except Exception as e:
        logger.error(f"Error getting TwinFabric connection: {e}")
        return None

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Handle server startup and shutdown."""
    global _twin_fabric_connection
    logger.info("UnrealMCP server starting up")
    try:
        _twin_fabric_connection = get_twinfabric_connection()
        if _twin_fabric_connection:
            logger.info("Connected to TwinFabric Engine on startup")
        else:
            logger.warning("Could not connect to TwinFabric Engine on startup")
    except Exception as e:
        logger.error(f"Error connecting to TwinFabric Engine on startup: {e}")
        _twin_fabric_connection = None
    
    try:
        yield {}
    finally:
        if _twin_fabric_connection:
            _twin_fabric_connection.disconnect()
            _twin_fabric_connection = None
        logger.info("TwinFabric MCP server shut down")

# Initialize server
mcp = FastMCP(
    "TwinFabricMCP")

sys.path.append(os.path.abspath(__file__))
# Import and register tools
from datav_twinfabric_mcp.tools.dtf_opus_tools import register_opus_tools
from datav_twinfabric_mcp.tools.dtf_project_tools import register_project_tools
from datav_twinfabric_mcp.tools.dtf_twin_tools import register_twin_system_tools
from datav_twinfabric_mcp.tools.agent_app_tools import register_agent_app_tools
from datav_twinfabric_mcp.tools.dtf_bailian_tools import register_bailian_tools
# Register tools 
register_bailian_tools(mcp)
register_opus_tools(mcp)
register_project_tools(mcp)
register_twin_system_tools(mcp)
register_agent_app_tools(mcp)
@mcp.prompt()
def info():
    """Information about available TwinFabric MCP tools and best practices."""
    return """
    # How to operate
    1. determine the type of user needs (such as "information query" or "operation execution")
    2. match the corresponding tool set according to the type
    3. generate specific parameters
    4. Prioritize calling related tools
    # TwinFabric MCP Server Tools and Best Practices
    ## Basic Concepts 
    1. Camera
    - Similar to the camera in 3D games, including basic camera parameters and playback duration
    2. Graphics_primitive
    - Use Graphics_primitive to visualize geographic data including point, line and surface data. The main types are POI, geo-fence, fly line, radar, etc.
    3. Custom_graphics_primitive
    - Use custom_graphics_primitive to visualize other data, such as 2D web pages, etc.
    4. Scene
    - The scene in TwinFabric contains the basic 3D scene + Camera + graphics_primitives + custom_graphics_primitive, which is a basic unit for demonstration switching.
    5. Storyline
    - The storyline consists of a series of scenes. Play a storyline means play these scenes in order.
    6. TwinPrefab
    - Twin Prefab is an abstract concept. It consists of multiple twin components. Each twin component has its own function. For example, the model component is used to display a model, etc.
    7. TwinActor
    - When TwinPrefab is instantiated to the scene, it forms a TwinActor
    ## TwinFabric Studio Tools
    - `play_scene(uuid)`
      Play a scene in TwinFabric Studio with its uuid
    - `gather_scene_info()`
      gather all scenes info in TwinFabric Studio
    - `play_camera(uuid)`
      switch to a camera in TwinFabric Studio with its uuid
    - `gather_scene_info()`
      gather all cameras info in TwinFabric Studio
    - `gather_all_graphics_primitive()`
      gather all graphics_primitive info in TwinFabric Studio  
    - `show_graphics_primitive(uuid)`
      set graphics_primitive visibility true in TwinFabric Studio with its uuid  
    - `hide_graphics_primitive(uuid)`
      set graphics_primitive visibility false in TwinFabric Studio with its uuid 
    - `gather_all_custom_graphics_primitive()`
      gather all custom_graphics_primitive info in TwinFabric Studio  
    - `show_custom_graphics_primitive(uuid)`
      set custom_graphics_primitive visibility true in TwinFabric Studio with its uuid  
    - `hide_custom_graphics_primitive(uuid)`
      set custom_graphics_primitive visibility false in TwinFabric Studio with its uuid 
    - `gather_storyline_info()`
      gather all storyline info in TwinFabric Studio  
    - `play_storyline(uuid)`
      start playing a storyline in TwinFabric Studio with its uuid  
    - `stop_storyline(uuid)`
      stop playing a storyline in TwinFabric Studio with its uuid 
    ## TwinFabric TwinSystem Tools
    - `gather_all_twin_prefab_info()`
      gather all twin_prefabs info in TwinFabric
    - `gather_all_twin_actor_info()`
      gather all twin_actors info in TwinFabric  
    ## Best Practices
    ### Scene
    - When the user says I want to watch a certain content, you should find the scene that best matches what the user said based on the collected TwinFabric scenes, and then call play_scene(uuid), where uuid is the uuid field of the scene
    
    ### Error Handling
    - Check command responses for success
    - Handle errors gracefully
    - Log important operations
    - Validate parameters
    - Clean up resources on errors
    """

def run():
    logger.info("Starting MCP server with stdio transport")
    mcp.run(transport='stdio') 
# Run the server
if __name__ == "__main__":
   run()
    #mcp.run(transport="streamable-http",host="30.232.92.111", port=9000, path="/mcp")