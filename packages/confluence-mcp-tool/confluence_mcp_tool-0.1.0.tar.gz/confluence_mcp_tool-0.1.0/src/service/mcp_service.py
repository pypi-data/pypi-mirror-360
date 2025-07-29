from pydantic import BaseModel
from confluence.main import ConfluenceTool, ConfluenceToolInputSchema
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("confluence_mcp")

class ToolInput(BaseModel):
    """Input model for the Confluence tool endpoint."""

    input: str  # e.g., Confluence page URL
    args: dict = {}  # optional, more args from user
    
@mcp.tool()
async def get_confluence_content(tool_input: ToolInput):
    """Fetch content from a Confluence page using the page's URL."""
    try:
        page_url = tool_input.input
        confluence_tool = ConfluenceTool()
        content = confluence_tool.run(ConfluenceToolInputSchema(page_url=page_url))
        return {
            "output": content,
        }
    except Exception as e:
        return {"error": f"Failed to process Confluence page: {str(e)}"}

def main() -> None:
    """Start the MCP service."""
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()