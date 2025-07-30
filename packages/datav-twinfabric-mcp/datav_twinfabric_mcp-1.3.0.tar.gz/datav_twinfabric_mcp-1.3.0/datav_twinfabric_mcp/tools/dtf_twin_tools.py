"""
DTF Opus Tools for TwinFabric MCP.

This module provides tools to interact with TwinFabric Studio
"""

import logging
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP, Context
from typing import Annotated
from pydantic import Field
# Get logger
logger = logging.getLogger("TwinFabricMCP")

def register_twin_system_tools(mcp: FastMCP):
    """Register TwinFabric Studio tools with the MCP server."""
    
    @mcp.tool()
    def gather_all_twin_prefabs(
    ) -> Dict[str, Any]:
        """Get all the information of all twinPrefabs in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_all_twin_prefabs", {})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"Blueprint creation response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def gather_all_twin_actors(
    ) -> Dict[str, Any]:
        """Get all the information of all twinActors in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_all_twin_actors", {})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"Blueprint creation response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}  
        
    @mcp.tool()  
    def gather_twin_prefab_info(
        uuid: str
    ) -> Dict[str, Any]:
        """get information of twin prefab with its uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin prefab in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_twin_prefab_info", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"gather_twin_prefab_info: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error gather_twin_prefab_info: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()  
    def gather_twin_actor_info(
        uuid: str
    ) -> Dict[str, Any]:
        """get information of twin actor with its uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin prefab in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_twin_actor_info", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"gather_twin_actor_info: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error gather_twin_actor_info: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()  
    def create_twin_actor(
        uuid: str
    ) -> Dict[str, Any]:
        """create a twin actor with its parent twinprefab's uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin prefab in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("create_twin_actor", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"create_twin_actor: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error create_twin_actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
    @mcp.tool()  
    def delete_twin_actor(
        uuid: str
    ) -> Dict[str, Any]:
        """delete a twin actor with its uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin actor in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("delete_twin_actor", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"delete_twin_actor: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error delete_twin_actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()  
    def set_twin_actor_visibility(
        visible: bool
    ) -> Dict[str, Any]:
        """set a twin actor visibility with its uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin actor in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("set_twin_actor_visibility", {
                "visible": visible,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"set_twin_actor_visibility: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error set_twin_actor_visibility: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def create_twin_prefab(
        name: str
    ) -> Dict[str, Any]:
        """create a twin prefab with its name in TwinFabric Studio."""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("create_twin_prefab", {
                "name": name,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"create_twin_prefab: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error create_twin_prefab: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def delete_twin_prefab(
        uuid: str
    ) -> Dict[str, Any]:
        """delete a twin prefab with its uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin prefab in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("delete_twin_prefab", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"delete_twin_prefab: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error delete_twin_prefab: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def set_twin_actor_transform(
        uuid:str,
        transform: str
    ) -> Dict[str, Any]:
        """set twin actor transform with its uuid in TwinFabric Studio. uuid is the uuid of the corresponding twin actor in TwinFabric,transform is a json liks:{"rotation":{"x":0,"y":0,"z":0,"w":1},"translation":{"x":0,"y":0,"z":0},"scale3D":{"x":1,"y":1,"z":1} } """

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("set_twin_actor_transform", {
                "uuid": uuid,
                "transform":transform
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"set_twin_actor_transform: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error set_twin_actor_transform: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
        
    @mcp.tool()  
    def focus_twin_actor(
        uuid:Annotated[str, Field(description="uuid of twin actor")],
        info:Annotated[str, Field(description="要观看的物体的部位描述")],
        camera_view: Annotated[str, Field(description="相机的视角：该变量的值只能是：正视、俯视、仰视、鸟瞰中的一种")],
        camera_angle: Annotated[float, Field(description="精确设置相对于物体的forward轴的角度（0-360°，顺时针）,0°为物体的正面；180度为物体的背面。0-180度为物体的右侧，180-360度为物体的左侧")],
        camera_pitch: Annotated[float, Field(description="相机的pitch角")],
        target_position:Annotated[str, Field(description=" 从“物体中心”、“顶部中心”、“物体上半部”、“物体下半部”中选择最适合的视点位置")],

    ) -> Dict[str, Any]:
        """以指定的相机语义位置设置相机，使得相机能够聚焦到孪生体上去"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("focus_twin_actor", {
                "uuid": uuid,
                "info": info,
                "view":camera_view,
                "angle":camera_angle,
                "pitch":camera_pitch,
                "target_position":target_position
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"focus_twin_actor: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error focus_twin_actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def focus_twin_actor_with_camera_slot(
        uuid:Annotated[str, Field(description="uuid of twin actor")],
        camera_slot: Annotated[str, Field(description="孪生体中的相机位的名字")],
    ) -> Dict[str, Any]:
        """切换相机到孪生体指定的相机位"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("focus_twin_actor_with_camera_slot", {
                "uuid": uuid,
                "camera_slot":camera_slot
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"focus_twin_actor_with_camera_slot: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error focus_focus_twin_actor_with_camera_slottwin_actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("TwinFabric tools registered successfully") 