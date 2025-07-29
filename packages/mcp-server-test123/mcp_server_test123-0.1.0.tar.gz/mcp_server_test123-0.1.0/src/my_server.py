from fastmcp import FastMCP

server = FastMCP("My MCP Server")

@server.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    server.run()