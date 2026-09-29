import asyncio
from mcp.server.fastapi import FastApiServer
from mcp.types import Tool, TextContent, CallToolResult
from app.tools import run_in_sandbox
import uvicorn

# Initialize the MCP FastApi server definition
mcp_app = FastApiServer(name="secure-sandbox-mcp")

@mcp_app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Exposes available sandbox commands dynamically to the LLM agent."""
    return [
        Tool(
            name="execute_sandbox_tests",
            description="Runs code files, linters, and pytest pipelines securely inside an isolated container environment.",
            inputSchema={
                "type": "object",
                "properties": {
                    "commands": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of shell commands to execute sequential verifications."
                    },
                    "code_files": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                        "description": "A dictionary mapping file paths to their target source code values."
                    }
                },
                "required": ["commands", "code_files"]
            }
        )
    ]

@mcp_app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> CallToolResult:
    """Executes the specific code parsing action requested via standard JSON-RPC protocol layers."""
    if name == "execute_sandbox_tests":
        commands = arguments.get("commands", [])
        code_files = arguments.get("code_files", {})
        
        # Execute using our pre-built isolated container infrastructure
        result = run_in_sandbox(commands=commands, code_files=code_files)
        
        status_str = "SUCCESS" if result["success"] else "FAILED"
        return CallToolResult(
            content=[
                TextContent(
                    type="text",
                    text=f"Sandbox execution status: {status_str}\n\nExecution Logs:\n{result['log']}"
                )
            ],
            isError=not result["success"]
        )
    raise ValueError(f"Requested tool identifier '{name}' is not currently active on this MCP transport node.")

if __name__ == "__main__":
    # Host the MCP server layer on port 8001
    uvicorn.run(mcp_app, host="127.0.0.1", port=8001)
