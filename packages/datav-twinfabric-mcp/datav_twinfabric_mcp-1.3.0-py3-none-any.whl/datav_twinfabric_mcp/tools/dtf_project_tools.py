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

def register_project_tools(mcp: FastMCP):
    """Register TwinFabric Studio project tools with the MCP server."""
    
    @mcp.tool()
    def gather_twinfabric_project_info(
    ) -> Dict[str, Any]:
        """Collect TwinFabric project files, including all the information of a TwinFabric project"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("gather_twinfabric_project_info", {})
            
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
    def set_weather(
        weather:Annotated[int, Field(description="The weather index, from 0 to 11, represents: Sunny, few clouds, cloudy, overcast, light rain, moderate rain, heavy rain, rainstorm, light snow, moderate snow, heavy snow, sandstorm")]=0
    ) -> Dict[str, Any]:
        """Setting the weather in Twin Fabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("set_weather", {"weather":weather})
            
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
    def set_time_of_day(
        TOD:Annotated[float, Field(description="Set the time of day from 0 to 24")]=12.0
    ) -> Dict[str, Any]:
        """Setting the time in Twin Fabric"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("set_time_of_day", {"time":TOD})
            
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
    def execute_custom_function(
        function:Annotated[str, Field(description="The name of the custom function to execute")],
        parameters:Annotated[Dict[str, Any], Field(description="The name of the custom function to execute,If you don't know the parameter list of a custom function, please refer to the Knowledge Base")]
    ) -> Dict[str, Any]:
        """Execute custom functions in TwinFabric by name"""

        # Import inside function to avoid circular imports
        from datav_twinfabric_mcp.twinfabric_mcp_server import get_twinfabric_connection
        
        try:
            TwinFabric = get_twinfabric_connection()
            if not TwinFabric:
                logger.error("Failed to connect to TwinFabric Engine")
                return {"success": False, "message": "Failed to connect to TwinFabric Engine"}
                
            response = TwinFabric.send_command("execute_custom_function", {
                "function":function,
                "parameters":parameters})
            
            if not response:
                logger.error("No response from TwinFabric Engine")
                return {"success": False, "message": "No response from TwinFabric Engine"}
            
            logger.info(f"Blueprint creation response: {response}")
            return response or {}
            
        except Exception as e:
            error_msg = f"Error creating blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("TwinFabric project tools registered successfully") 