# mcp_devtasks MCP Server

This project provides basic development tools as an MCP server, designed to be used with Claude Desktop or any Model Context Protocol (MCP) client. It exposes dev tasks (install, build, lint, test, ci) as callable tools.

# UVX Installation and Usage

This project supports [UVX](https://github.com/astral-sh/uv) for fast, isolated Python package execution, following the Model Context Protocol (MCP) server pattern.

## Prerequisites
- Python 3.10+
- [uvx](https://github.com/astral-sh/uv) installed (`pip install uv` or see uv docs)

## Install from PyPI

```bash
pip install mcp-devtasks
```

## Development Install

```bash
git clone https://github.com/blooop/mcp_devtasks.git
cd mcp_devtasks
pip install -e .
```

## Running the MCP Server with UVX

You can run the MCP server using UVX, which is the recommended approach for integration with tools like Claude Desktop:

```bash
uvx mcp-devtasks
```

- This will launch the MCP server as defined in this package.

### Example Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "devtasks": {
      "command": "uvx",
      "args": [
        "mcp-devtasks"
      ]
    }
  }
}
```

## CLI Usage

You can also run the server directly:

```bash
python -m main
```

or, if installed as a script:

```bash
mcp-devtasks
```

# Available Dev Tasks

The following dev tasks are exposed as MCP tools:

- **install**: Install all dependencies required for the project.
- **build**: Build the project.
- **lint**: Lint the codebase.
- **test**: Run all tests.
- **ci**: Run the full CI pipeline.

You can call these tools from your MCP client or Claude Desktop interface.

# Dev Task Configuration (`mcp_devtasks.yaml`)

The dev tasks exposed by this MCP server are configured via a YAML file named `mcp_devtasks.yaml` in the project root. This file maps task names to the shell commands that will be executed when the corresponding MCP tool is called.

## Example `mcp_devtasks.yaml`

```yaml
# mcp_devtasks.yaml
# YAML file specifying shell commands for each dev task
install: "echo Installing dependencies... && pixi update"
build: "echo Building project... && pixi run build"
lint: "echo Linting code... && pixi run lint"
test: "echo Running tests... && pixi run test"
ci: "echo Running CI checks... && pixi run ci-no-cover"
```

You can customize this file to add, remove, or change the commands for your development workflow. Each key becomes an MCP tool, and the value is the shell command that will be run.
