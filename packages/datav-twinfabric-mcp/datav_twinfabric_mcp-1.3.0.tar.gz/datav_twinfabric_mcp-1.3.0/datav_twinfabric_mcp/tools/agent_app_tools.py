import logging
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP, Context
import os
from http import HTTPStatus
from dashscope import Application

# Get logger
logger = logging.getLogger("TwinFabricMCP")

def register_agent_app_tools(mcp: FastMCP):
    """Register TwinFabric Studio project tools with the MCP server."""

    user_api_key = os.getenv("DASHSCOPE_API_KEY")
    location_app_id = os.getenv("LOCATION_APP_ID")
    
    @mcp.tool()
    def get_location_from_placename(
        placename: str
    ) -> Dict[str, Any]:
        """Get the longitude and latitude coordinates from the placename."""

        response = Application.call(
            api_key = user_api_key,
            app_id = location_app_id,
            prompt = placename
            )
        
        if response.status_code == HTTPStatus.OK:
            logger.info(f"get_location_from_placename response: {response.output.text}")
            return response.output.text
        else:
            error_msg = f"get_location_from_placename status code: {response.status_code}, error message: {response.message}, 请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("Agent app tools registered successfully") 