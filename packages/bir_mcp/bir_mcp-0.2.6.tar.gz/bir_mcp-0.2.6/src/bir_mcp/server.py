import functools
import inspect
import warnings

import fastmcp
import typer

import bir_mcp.git_lab
import bir_mcp.grafana
import bir_mcp.local

# class McpCategory(enum.StrEnum):
#     gitlab = enum.auto()
#     grafana = enum.auto()
#     jira = enum.auto()
#     local = enum.auto()


def build_mcp_server(
    gitlab_private_token: str | None = None,
    grafana_username: str | None = None,
    grafana_password: str | None = None,
    jira_api_key: str | None = None,
    gitlab_url: str = "https://gitlab.kapitalbank.az",
    grafana_url: str = "https://yuno.kapitalbank.az",
    timezone: str = "Asia/Baku",
    max_output_length: int | None = None,
    verify_ssl: bool = True,
    ca_file: str | None = None,
) -> fastmcp.FastMCP:
    ssl_verify = ca_file or verify_ssl  # Workaround because typer doesn't support union types.
    server = fastmcp.FastMCP(
        name="Bir MCP server",
        instructions=inspect.cleandoc("""
            MCP server for BirBank.
        """),
    )
    server.mount(bir_mcp.local.build_mcp_server(max_output_length=max_output_length))
    if gitlab_private_token:
        git_lab = bir_mcp.git_lab.GitLab(
            url=gitlab_url,
            private_token=gitlab_private_token,
            timezone=timezone,
            ssl_verify=ssl_verify,
        )
        subserver = git_lab.build_mcp_server(max_output_length=max_output_length)
        server.mount(subserver, prefix=git_lab.tag)
    else:
        warnings.warn(
            "Since GitLab private token is not provided, the GitLab tools will not be available."
        )

    if grafana_username and grafana_password:
        grafana = bir_mcp.grafana.Grafana(
            url=grafana_url,
            auth=(grafana_username, grafana_password),
            timezone=timezone,
            ssl_verify=ssl_verify,
        )
        subserver = grafana.build_mcp_server(max_output_length=max_output_length)
        server.mount(subserver, prefix=grafana.tag)
    else:
        warnings.warn(
            "Since Grafana username and password are not provided, the Grafana tools will not be available."
        )

    return server


@functools.wraps(build_mcp_server)
def build_and_run(*args, **kwargs):
    server = build_mcp_server(*args, **kwargs)
    server.run()


def main():
    typer.run(build_and_run)


if __name__ == "__main__":
    main()
