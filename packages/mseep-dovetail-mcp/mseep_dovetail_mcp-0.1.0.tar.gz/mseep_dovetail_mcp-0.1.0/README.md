# Dovetail MCP Server 🚀

This project is a simple Model Context Protocol (MCP) server that provides API endpoints for interacting with Dovetail's project, insight, and data resources. It acts as a bridge between the MCP ecosystem and Dovetail's API, exposing useful tools for querying project highlights, insights, and data.

This is purely a MVP, mean't to show what we can do with MCP and Dovetail, and is mean't to inspire and to be expanded upon.

## Features
- List Dovetail projects
- Get project highlights
- List and get project insights
- List and get project data
- Export data content as markdown

## Requirements
- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (for dependency management and running)

## Installation
1. Clone this repository:
   ```sh
   git clone <your-repo-url>
   cd dovetail-mcp
   ```
2. (Recommended) Install [uv](https://github.com/astral-sh/uv):
   ```sh
   pip install uv
   # or, with Homebrew:
   brew install uv
   ```
3. Install dependencies with uv:
   ```sh
    uv sync
   ```

## Usage
To start the MCP server with uv, run:
```sh
uv run main.py
```
The server will start and expose the registered tools for use via the MCP protocol.

You can also add this into any client (like Claude for Desktop) and have that manage it for you.

## Configuration
API credentials and endpoint URLs are set in `main.py`. Update these as needed for your environment.

## Credits
Created by Rhys Johns.
