from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeding(name: str) -> str:
    """Get a greeting for a given name"""
    return f"Hello, {name}!"

def main() -> None:
    mcp.run(transport="stdio")
