"""FastAPI service for the Confluence tool."""

from fastapi import FastAPI
from pydantic import BaseModel

from confluence.main import ConfluenceTool, ConfluenceToolInputSchema

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


class ToolInput(BaseModel):
    """Input model for the Confluence tool endpoint."""

    input: str  # e.g., Confluence page URL
    args: dict = {}  # optional, more args from user


@app.post("/tool/confluence_reader/run")
async def run_tool(tool_input: ToolInput):
    """Run the Confluence tool with the given input.

    Args:
        tool_input: The input parameters for the tool

    Returns:
        The tool's output or an error message
    """
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
    """Start the FastAPI service.

    Launches the service on 0.0.0.0:8000 so it is accessible from outside the container.
    """
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()