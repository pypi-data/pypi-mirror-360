"""
DTF Opus Tools for TwinFabric MCP.

This module provides tools to interact with TwinFabric Studio
"""

import logging
from typing import Dict, List, Any
from mcp.server.fastmcp import FastMCP, Context
import os
from http import HTTPStatus
from dashscope import Application
from typing import Annotated
from pydantic import Field
# Get logger
logger = logging.getLogger("TwinFabricMCP")
def register_bailian_tools(mcp: FastMCP):
    """Register TwinFabric Studio project tools with the MCP server."""
    
    @mcp.tool()
    def gather_twinfabric_knowledge_info(
        content:Annotated[str, Field(description="The user's complete input")],
    ) -> Dict[str, Any]:
        """Collect TwinFabric knowedge, including all the information of a TwinFabric project"""

        response = Application.call(
        # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        #app_id='92b025bcb361425598b18fbe4f6eeb22',# 替换为实际的应用 ID
        app_id='81406788e0ae40c1b7effd63d6c7359d',# 替换为实际的应用 ID 使用qwen3-1.7b
        prompt=content)

        if response.status_code != HTTPStatus.OK:
            print(f'request_id={response.request_id}')
            print(f'code={response.status_code}')
            print(f'message={response.message}')
            print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
            return {}
        else:
            print(response.output.text)
            return response.output.text
        
    @mcp.tool()
    def generate_camera_semantic_position(
        content:str
    ) -> Dict[str, Any]:
        """Generate camera semantic position"""

        response = Application.call(
        # 若没有配置环境变量，可用百炼API Key将下行替换为：api_key="sk-xxx"。但不建议在生产环境中直接将API Key硬编码到代码中，以减少API Key泄露风险。
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        #app_id='92b025bcb361425598b18fbe4f6eeb22',# 替换为实际的应用 ID
        app_id='4d19ad3395ac41f1b4d895f89dae7948',# 替换为实际的应用 ID 使用qwen3-1.7b
        prompt=content)

        if response.status_code != HTTPStatus.OK:
            print(f'request_id={response.request_id}')
            print(f'code={response.status_code}')
            print(f'message={response.message}')
            print(f'请参考文档：https://help.aliyun.com/zh/model-studio/developer-reference/error-code')
            return {}
        else:
            print(response.output.text)
            return response.output.text
    logger.info("TwinFabric project tools registered successfully") 