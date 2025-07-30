# PyPI Demo MCP

A demonstration Model Context Protocol (MCP) server showcasing basic tool and resource functionality that can be easily installed to Claude Desktop.

## Overview

This project demonstrates how to create a simple MCP server using the FastMCP framework. It includes:

- A basic addition tool that adds two numbers
- A dynamic greeting resource that provides personalized greetings
- **Automatic Claude Desktop integration** - installs directly to your Claude Desktop configuration
- Proper packaging configuration for PyPI distribution

## Features

### Tools

- **sum**: Adds two integers and returns the result

### Resources

- **greeting**: Dynamic resource that generates personalized greetings based on a name parameter

## Quick Installation for Claude Desktop

### Option 1: Automatic Installation (Recommended)

```bash
# Install the package
pip install pypi-demo-mcp

# Automatically configure Claude Desktop
pypi-demo-mcp install
```

### Option 2: Manual Installation

```bash
# Install the package
pip install pypi-demo-mcp

# Run the setup script
python -m pypi_demo_mcp.server install
```

After installation, **restart Claude Desktop** to use the new MCP server!

- **greeting**: Dynamic resource that generates personalized greetings based on a name parameter

## Installation

### From PyPI (when published)

```bash
pip install pypi-demo-mcp
```

### From Source

```bash
git clone <repository-url>
cd pypi_demo_mcp
pip install .
```

### Using uv (recommended)

```bash
uv sync
```

## Usage

### Running the Server

```bash
python main.py
```

### Using the Tools

The server provides the following MCP tools:

#### Addition Tool

```python
# Tool: sum
# Description: Add two numbers
# Parameters: a (int), b (int)
# Returns: int
```

#### Greeting Resource

```python
# Resource: greeting://{name}
# Description: Get a personalized greeting
# Parameters: name (str)
# Returns: str
```

## Development

### Project Structure

```text
pypi_demo_mcp/
├── main.py           # Main MCP server implementation
├── pyproject.toml    # Project configuration
├── README.md         # This file
└── uv.lock          # Lock file for dependencies
```

### Dependencies

- Python >= 3.10
- mcp[cli] >= 1.10.1

### Configuration

The project uses `pyproject.toml` for configuration following modern Python packaging standards.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## License

This project is intended for demonstration purposes.

## About MCP

The Model Context Protocol (MCP) is a protocol for connecting AI models with various tools and resources. This demo showcases basic MCP server functionality using the FastMCP framework.

For more information about MCP, visit: <https://github.com/modelcontextprotocol>
