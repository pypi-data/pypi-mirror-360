from fastmcp import FastMCP
import yaml
import subprocess
from typing import Dict
import os
import logging

# Default commands if YAML config is missing
DEFAULT_COMMANDS = {
    "install": "install",
    "build": "build",
    "lint": "lint",
    "test": "test",
    "ci": "ci",
}


logging.basicConfig(
    level=logging.INFO,
    format="[devtasks][%(levelname)s] %(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("devtasks")


def log(msg, level="info"):
    if level == "info":
        logger.info(msg)
    elif level == "error":
        logger.error(msg)
    elif level == "warning":
        logger.warning(msg)
    elif level == "debug":
        logger.debug(msg)
    else:
        logger.info(msg)


log(f"cwd: {os.getcwd()}")
log(f"__file__: {__file__}")

# Robust config file search
CONFIG_LOCATIONS = [
    os.path.join(os.getcwd(), "mcp_devtasks.yaml"),
    os.path.join(os.path.dirname(__file__), "mcp_devtasks.yaml"),
]
CONFIG_FILE = None
for path in CONFIG_LOCATIONS:
    log(f"Checking config path: {path}")
    if os.path.exists(path):
        CONFIG_FILE = path
        log(f"Found config file: {CONFIG_FILE}")
        break
if not CONFIG_FILE:
    log("No config file found, using DEFAULT_COMMANDS", level="warning")

try:
    if CONFIG_FILE:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            COMMANDS: Dict[str, str] = yaml.safe_load(f)
            log(f"Loaded commands from {CONFIG_FILE}: {COMMANDS}")
    else:
        COMMANDS: Dict[str, str] = DEFAULT_COMMANDS.copy()
        log(f"Using default commands: {COMMANDS}")
except Exception as e:
    log(f"Error loading config file: {e}", level="error")
    COMMANDS: Dict[str, str] = DEFAULT_COMMANDS.copy()

mcp = FastMCP("Devtasks MCP Server")


def run_shell_command(cmd: str) -> str:
    log(f"Running shell command: {cmd}")
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=120, check=False
        )
        log(f"Command stdout: {result.stdout}")
        log(f"Command stderr: {result.stderr}")
        log(f"Command returncode: {result.returncode}")
        return result.stdout + ("\n" + result.stderr if result.stderr else "")
    except Exception as e:
        log(f"Exception running command: {e}", level="error")
        return f"Error: {e}"


@mcp.tool
def list_commands() -> str:
    """
    List all available dev commands with descriptions for when to use them.
    """
    descriptions = {
        "install": "Install all dependencies required for the project. Use this when setting up the project for the first time or when dependencies change.",
        "build": "Build the project. Use this after making changes to source code that require compilation or packaging.",
        "lint": "Lint the codebase. Use this to check for code style and quality issues before committing or pushing changes.",
        "test": "Run all tests. Use this to verify that your code works as expected and nothing is broken.",
        "ci": "Run the full CI pipeline. Use this to perform all checks (formatting, linting, tests) as done in continuous integration.",
    }
    lines = []
    for cmd in COMMANDS:
        desc = descriptions.get(cmd, "No description available.")
        lines.append(f"{cmd}: {desc}")
    return "\n".join(lines)


@mcp.tool
def list_command_names() -> str:
    """
    List just the available command names, one per line.
    """
    return "\n".join(COMMANDS.keys())


@mcp.tool(
    description="Run a dev command by name. Returns the output of the command. Use this to execute project tasks such as build, test, lint, etc."
)
def run_command(command: str) -> str:
    """
    Run a dev command by name. Returns the output of the command. Use this to execute project tasks such as build, test, lint, etc.
    """
    if command not in COMMANDS:
        return f"Unknown command: {command}"
    return run_shell_command(COMMANDS[command])


def main() -> None:
    """Entry point for CLI usage."""
    mcp.run()


if __name__ == "__main__":
    main()
