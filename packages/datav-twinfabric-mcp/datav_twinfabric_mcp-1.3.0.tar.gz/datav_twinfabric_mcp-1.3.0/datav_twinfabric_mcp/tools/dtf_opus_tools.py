"""
DTF Opus Tools for TwinFabric MCP.

This module provides tools to interact with TwinFabric Studio
"""

import logging
from typing import Dict, List, Any
from typing import Annotated
from pydantic import Field
from mcp.server.fastmcp import FastMCP, Context
from dashscope import Application
from http import HTTPStatus
import os
import json
    
# Get logger
logger = logging.getLogger("TwinFabricMCP")

def register_opus_tools(mcp: FastMCP):
    """Register TwinFabric Studio tools with the MCP server."""
    
    @mcp.tool()
    def play_scene(
        uuid: str
    ) -> Dict[str, Any]:
        """play a scene in TwinFabric Studio. uuid is the uuid of the corresponding scene in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("play_scene", {
                "uuid": uuid,
            })
            
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
    def gather_scene_info(
    ) -> Dict[str, Any]:
        """Get all the information of all scenes in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection

        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_scene_info", {})
            
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
    def play_camera(
        uuid: str
    ) -> Dict[str, Any]:
        """switch a camera in TwinFabric Studio. uuid is the uuid of the corresponding camera in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("play_camera", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"play_camera: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error play_camera: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def camera_look_at(
        lng: Annotated[float, Field(description="target position’s longitude")],
        lat: Annotated[float, Field(description="target position’s latitude")],
        height: Annotated[float, Field(description="target position’s height")],
        distance: Annotated[float, Field(description="the distance between the camera and the target point in meters,This parameter should be reasonably calculated according to the size of the target so that the target can be fully displayed in the lens.")]=200,
        blendTime: Annotated[float, Field(description="how long it takes to move to the specified position.")]=1.0,
    ) -> Dict[str, Any]:
        """Let the camera look to a target object. The distance between the camera and the target point should be guaranteed so that the target object is fully presented in the field of view."""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("camera_move_to", {
                "lng": lng,
                "lat": lat,
                "height": height,
                "distance": distance,
                "blendTime": blendTime,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"camera_move_to: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error camera_move_to: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}


    @mcp.tool()
    def gather_camera_info(
    ) -> Dict[str, Any]:
        """Get all the information of all cameras in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_camera_info", {})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"gather_camera_info response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def play_storyline(
        uuid: str
    ) -> Dict[str, Any]:
        """start playing a storyline in TwinFabric Studio. uuid is the uuid of the corresponding storyline in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("play_storyline", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"play_camera: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error play_camera: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def stop_storyline(
        uuid: str
    ) -> Dict[str, Any]:
        """stop playing a storyline in TwinFabric Studio. uuid is the uuid of the corresponding storyline in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("stop_storyline", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"play_camera: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error play_camera: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def gather_storyline_info(
    ) -> Dict[str, Any]:
        """Get all the information of all storylines in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_storyline_info", {})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"gather_storyline_info response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def show_graphics_primitive(
        uuid: str
    ) -> Dict[str, Any]:
        """Set a graphics_primitive visable true in TwinFabric Studio. uuid is the uuid of the corresponding storyline in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("show_graphics_primitive", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"show_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error show_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def create_graphics_primitive(
        name: Annotated[str, Field(description="Name must be one of the following: 1. POI 2. 动态轨迹 3. 地理围栏 4. 柱状层 5. 热力层 6. 装饰雷达 7. Beta_OD飞线3 ")],
        gis_data:Annotated[Dict[str, Any], Field(description="一个geojson,里面包含多条数据，其properties字段中务必添加以下字段：name,title,iconUrl,type【type字段的值务必与title字段一致】. ")],
    ) -> Dict[str, Any]:
        """create a graphics_primitive using a fixed name type and gis_data.Before calling this function, you should first call the preprocess_graphics_primitive_data tool."""
        #gp_data = call_graphics_primitive_gen(str(gis_data))
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
            
            response = TwinFabric.send_command("create_graphics_primitive", {
                "name": name,
                "gis_data": gis_data,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"create_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error create_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def create_graphics_primitive_from_url(
        name: Annotated[str, Field(description="该字段必须从以下中选择: 1. POI 2. 动态轨迹 3. 地理围栏 4. 柱状层 5. 热力层 6. 装饰雷达 7. Beta_OD飞线3 ")],
        data_url:Annotated[str, Field(description="一个内容为geojson的url")],
    ) -> Dict[str, Any]:
        """create a graphics_primitive using a fixed name type and url.Before calling this function."""
        #gp_data = call_graphics_primitive_gen(str(gis_data))
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
            
            response = TwinFabric.send_command("create_graphics_primitive_from_url", {
                "name": name,
                "data_url": data_url,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"create_graphics_primitive_from_url: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error create_graphics_primitive_from_url: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}


    @mcp.tool()  
    def delete_graphics_primitive(
        uuid: str
    ) -> Dict[str, Any]:
        """delete a graphics_primitive with its uuid"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("delete_graphics_primitive", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"delete_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error delete_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def focus_graphics_primitive(
        uuid: str
    ) -> Dict[str, Any]:
        """focus to a graphics_primitive with its uuid"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("delete_graphics_primitive", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"delete_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error delete_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def hide_graphics_primitive(
        uuid: str
    ) -> Dict[str, Any]:
        """Set a graphics_primitive visable false in TwinFabric Studio which means hide a graphic_primitive. uuid is the uuid of the corresponding storyline in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("hide_graphics_primitive", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"play_camera: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error play_camera: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def gather_all_graphics_primitive(
    ) -> Dict[str, Any]:
        """Get all the information of all graphics_primitives in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_all_graphics_primitive", {})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"gather_all_graphics_primitive response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error gather_all_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def get_graphics_primitive_attributes(
        uuid:str
    ) -> Dict[str, Any]:
        """Get all the attribute of graphics_primitive in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("get_graphics_primitive_attribute", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"get_graphics_primitive_attribute response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error get_graphics_primitive_attribute: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_graphics_primitive_attributes(
        uuid:str,
        content:Annotated[Dict[str, Any], Field(description="attribute of graphics_primitive. The format must be consistent with the format obtained by get_graphics_primitive_attributes")]
    ) -> Dict[str, Any]:
        """set the attribute of graphics_primitive in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("set_graphics_primitive_attribute", {
                "uuid": uuid,
                "content":content
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"set_graphics_primitive_attribute response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error set_graphics_primitive_attribute: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}


    @mcp.tool()  
    def show_custom_graphics_primitive(
        uuid: str
    ) -> Dict[str, Any]:
        """Set a custom_graphics_primitive visable true in TwinFabric Studio. uuid is the uuid of the corresponding custom_graphics_primitive in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("show_custom_graphics_primitive", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"show_custom_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error show_custom_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def hide_custom_graphics_primitive(
        uuid: str
    ) -> Dict[str, Any]:
        """Set a custom_graphics_primitive visable false in TwinFabric Studio which means hide a graphic_primitive. uuid is the uuid of the corresponding custom_graphics_primitive in TwinFabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("hide_custom_graphics_primitive", {
                "uuid": uuid,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"hide_custom_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error hide_custom_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def gather_all_custom_graphics_primitive(
    ) -> Dict[str, Any]:
        """Get all the information of all custom_graphics_primitives in TwinFabric."""
        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_all_custom_graphics_primitive", {})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"gather_all_custom_graphics_primitive response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error gather_all_custom_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()  
    def show_digital_human(
        content: str
    ) -> Dict[str, Any]:
        """When you have completed the user's instructions, the last step is to call this function, broadcast the relevant content, and remind the user"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("show_digital_human", {
                "content": content,
            })
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"hide_custom_graphics_primitive: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error hide_custom_graphics_primitive: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("TwinFabric tools registered successfully") 