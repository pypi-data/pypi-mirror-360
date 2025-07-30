"""Main MCP server implementation."""

from fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("PyPI Demo MCP")


# Add an addition tool
@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


def main():
    """Main entry point for the MCP server."""
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        # Install the MCP server to Claude Desktop
        install_to_claude()
    else:
        # Run the server
        mcp.run()


def install_to_claude():
    """Install the MCP server configuration to Claude Desktop."""
    import json
    import os
    import sys
    from pathlib import Path
    
    # Claude Desktop config path
    if sys.platform == "win32":
        config_path = Path.home() / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    elif sys.platform == "darwin":
        config_path = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    else:
        config_path = Path.home() / ".config" / "claude" / "claude_desktop_config.json"
    
    # Ensure directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        config = {"mcpServers": {}}
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add our server configuration
    server_config = {
        "command": "uv",
        "args": ["--directory", str(Path(__file__).parent.parent), "run", "pypi-demo-mcp"]
    }
    
    config["mcpServers"]["pypi-demo-mcp"] = server_config
    
    # Write updated config
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ PyPI Demo MCP server installed to Claude Desktop!")
    print(f"📁 Config file: {config_path}")
    print("🔄 Please restart Claude Desktop to use the server.")


if __name__ == "__main__":
    main()
