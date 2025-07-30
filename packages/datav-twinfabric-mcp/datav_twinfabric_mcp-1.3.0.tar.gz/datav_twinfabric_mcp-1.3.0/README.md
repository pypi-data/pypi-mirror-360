# DataV TwinFabric MCP server

Python bridge for interacting with DataV TwinFabric using the Model Context Protocol (MCP).

## Setup

1. Make sure Python 3.10+ is installed
2. Install `uv` if you haven't already:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. Create and activate a virtual environment:
   ```bash
   cd datav-twinfabric-mcp
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   source .venv\Scripts\activate     # On Windows
   ```
4. Install dependencies:
   ```bash
   uv pip install -e .
   ```

At this point, you can configure your MCP Client (Claude Desktop, Cursor, Windsurf) to use the Unreal MCP Server as per the [Configuring your MCP Client](README.md#configuring-your-mcp-client).

## Test on Cherry Studio

1. Add MCP server in Settings.
 ```
 {
  "mcpServers": {
    "twinfabric_mcp_server": {
      "name": "DataV TwinFabric MCP",
      "command": "uvx",
      "args": [
        "datav-twinfabric-mcp"
      ],
      "env": {
        "LOG_DIR": "D:/", // Log directory
        "UnrealClientId": "D225E4144B548E5B20463AA2A7D2F7A7",//MCP控制的DataV TwinFabric客户端的机器码，需要从客户端的Setting中获取
      }
    }
  }
}
 ```
2. Save and Start the server.
3. Switch to the default assistant page, add MCP server at the bottom, and start your conversations.
