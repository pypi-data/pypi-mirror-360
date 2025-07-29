import inspect
from typing import Annotated

import detect_secrets
import fastmcp.tools
import git
import mcp
import pydantic

from bir_mcp.utils import to_fastmcp_tool


def get_mcp_tools(max_output_length: int | None = None) -> list[fastmcp.tools.FunctionTool]:
    tools = [
        find_secrets,
        get_local_repo_metadata,
    ]
    tools = [
        to_fastmcp_tool(
            tool,
            tags={"local"},
            annotations=mcp.types.ToolAnnotations(readOnlyHint=True, destructiveHint=False),
            max_output_length=max_output_length,
        )
        for tool in tools
    ]
    return tools


def build_mcp_server(max_output_length: int | None = None) -> fastmcp.FastMCP:
    tools = get_mcp_tools(max_output_length=max_output_length)
    server = fastmcp.FastMCP(
        name="MCP server with local tools",
        instructions=inspect.cleandoc("""
            Contains tool to work with local files.
        """),
        tools=tools,
    )
    return server


def find_secrets(
    file_path: Annotated[
        str,
        pydantic.Field(description="The path to the file to scan for secrets."),
    ],
) -> dict:
    """
    Scans a file for secrets using the [detect-secrets](https://github.com/Yelp/detect-secrets) tool.
    """
    secrets = detect_secrets.SecretsCollection()
    with detect_secrets.settings.default_settings():
        secrets.scan_file(file_path)

    secrets = {
        file_path: {
            "secret_type": secret.type,
            "line_number": secret.line_number,
        }
        for file_path, secret in secrets.data.items()
    }
    secrets = {"detected_secrets": secrets}
    return secrets


def get_local_repo_metadata(
    repo_path: Annotated[str, pydantic.Field(description="The filesystem path to the repo.")],
) -> dict:
    """Retrieves metadata about the Git repo in the local filesystem, such as branch names and remote urls."""
    repo = git.Repo(repo_path, search_parent_directories=True)
    branch_names = [b.name for b in repo.branches]
    remotes = [{"name": r.name, "urls": list(r.urls)} for r in repo.remotes]
    metadata = {
        "remotes": remotes,
        "branch_names": branch_names,
        "active_branch_name": repo.active_branch.name,
    }
    return metadata
