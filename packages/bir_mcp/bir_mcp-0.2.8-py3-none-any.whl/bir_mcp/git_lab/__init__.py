import base64
import inspect
import zoneinfo
from typing import Annotated

import fastmcp.tools
import gitlab.v4.objects
import httpx
import mcp
import pydantic

from bir_mcp.git_lab.prompts import get_prompts
from bir_mcp.git_lab.utils import GitLabUrl, MergeRequest, aget_merge_request_data
from bir_mcp.utils import (
    araise_for_status,
    build_mcp_server,
    filter_dict_by_keys,
    format_datetime_for_ai,
    to_fastmcp_tool,
    to_maybe_ssl_context,
)

ProjectPathOrUrlType = Annotated[
    str,
    pydantic.Field(
        description=inspect.cleandoc("""
            Either the filesystem-like path to a GitLab project with variable depth, for example:
            "organization/project_name" or "organization/namespace/subgroup/project_name",
            or a full url to a GitLab project in the format:
            "https://{gitlab_domain}/{project_path}/[.git]".
        """)
    ),
]
BranchType = Annotated[
    str,
    pydantic.Field(description="The branch name to fetch files from."),
]


class GitLab:
    def __init__(
        self,
        url: str,
        private_token: str,
        ssl_verify: bool | str = True,
        timezone: str = "UTC",
        tag: str | None = "gitlab",
    ):
        """
        GitLab GraphQL docs: https://docs.gitlab.com/api/graphql/
        Local instance GraphQL explorer: https://gitlab.kapitalbank.az/-/graphql-explorer
        """
        self.api_version = 4
        self.gitlab = gitlab.Gitlab(
            url=url,
            private_token=private_token,
            ssl_verify=ssl_verify,
            api_version=str(self.api_version),
        )
        self.gitlab.auth()
        self.ahttpx = httpx.AsyncClient(
            base_url=url,
            headers={"PRIVATE-TOKEN": private_token},
            verify=to_maybe_ssl_context(ssl_verify),
            event_hooks={"response": [araise_for_status]},
        )
        self.agraphql = gitlab.AsyncGraphQL(
            url=url,
            token=private_token,
            ssl_verify=ssl_verify,
        )
        self.timezone = zoneinfo.ZoneInfo(timezone)
        self.gitlab_url = GitLabUrl(base_url=url)
        self.tag = tag
        self.tags = {tag} if tag else set()

    def build_mcp_server(self, max_output_length: int | None = None) -> fastmcp.FastMCP:
        server = build_mcp_server(
            name="Bir GitLab MCP server",
            instructions=inspect.cleandoc("""
                GitLab related tools.
            """),
            tools=self.get_tools(max_output_length=max_output_length),
            prompts=self.get_prompts(),
        )
        return server

    def get_tools(self, max_output_length: int | None = None) -> list[fastmcp.tools.FunctionTool]:
        tools = [
            self.get_project_metadata,
            self.list_all_repo_branch_files,
            self.get_file_content,
            self.search_in_repository,
            self.get_latest_pipeline_info,
            self.get_merge_request_data,
            self.get_merge_request_data_from_url,
        ]
        tools = [
            to_fastmcp_tool(
                tool,
                tags=self.tags,
                annotations=mcp.types.ToolAnnotations(readOnlyHint=True, destructiveHint=False),
                max_output_length=max_output_length,
            )
            for tool in tools
        ]
        return tools

    def get_prompts(self) -> list[fastmcp.prompts.Prompt]:
        prompts = get_prompts()
        prompts = [
            fastmcp.prompts.Prompt.from_function(function, tags=self.tags) for function in prompts
        ]
        return prompts

    def get_project_from_url(self, project_path_or_url: str) -> gitlab.v4.objects.Project:
        project_path = self.gitlab_url.extract_project_path(project_path_or_url)
        project = self.gitlab.projects.get(project_path)
        return project

    def get_project_metadata(self, project_path_or_url: ProjectPathOrUrlType) -> dict:
        """
        Retrieves metadata about a GitLab project identified by the repo url,
        such as name, description, last activity, topics (tags), etc.
        """
        project = self.get_project_from_url(project_path_or_url)
        metadata = {
            "name_with_namespace": project.name_with_namespace,
            "topics": project.topics,
            "description": project.description,
            "last_activity_at": format_datetime_for_ai(
                project.last_activity_at, timezone=self.timezone
            ),
            "web_url": project.web_url,
        }
        return metadata

    def list_all_repo_branch_files(
        self,
        project_path_or_url: ProjectPathOrUrlType,
        branch: BranchType,
    ) -> dict:
        """Recursively lists all files and directories in the repository."""
        project = self.get_project_from_url(project_path_or_url)
        tree = project.repository_tree(ref=branch, get_all=True, recursive=True)
        tree = {"files": [{"path": item["path"], "type": item["type"]} for item in tree]}
        return tree

    def get_file_content(
        self,
        project_path_or_url: ProjectPathOrUrlType,
        branch: BranchType,
        file_path: Annotated[
            str,
            pydantic.Field(
                description="The path to the file relative to the root of the repository."
            ),
        ],
    ) -> str:
        """Retrieves the text content of a specific file."""
        project = self.get_project_from_url(project_path_or_url)
        file = project.files.get(file_path=file_path, ref=branch)
        content = base64.b64decode(file.content).decode()
        return content

    def search_in_repository(
        self,
        project_path_or_url: ProjectPathOrUrlType,
        branch: BranchType,
        query: Annotated[
            str,
            pydantic.Field(description="The text query to search for."),
        ],
    ) -> dict:
        """
        Performs a basic search for a text query within the repo's files.
        Doesn't support regex, but is case-insensitive.
        Returns a list of occurences within files, with file path, starting line in the file
        and a snippet of the contextual window in which the query was found.
        For details see the [API docs](https://docs.gitlab.com/api/search/#project-search-api).
        """
        project = self.get_project_from_url(project_path_or_url)
        results = project.search(scope="blobs", search=query, ref=branch)
        results = [
            {
                "file_path": result["path"],
                "starting_line_in_file": result["startline"],
                "snippet": result["data"],
            }
            for result in results
        ]
        results = {
            "query": query,
            "search_results": results,
        }
        return results

    def get_latest_pipeline_info(self, project_path_or_url: ProjectPathOrUrlType) -> dict:
        """Retrieves the latest pipeline info, such as url, status, duration, commit, jobs, etc."""
        project = self.get_project_from_url(project_path_or_url)
        pipeline = project.pipelines.latest()

        commit = project.commits.get(pipeline.sha)
        commit = filter_dict_by_keys(
            commit.attributes,
            ["title", "author_name", "web_url"],
        )

        jobs = pipeline.jobs.list(all=True)
        jobs = [
            filter_dict_by_keys(
                job.attributes,
                ["name", "status", "stage", "allow_failure", "web_url"],
            )
            for job in jobs
        ]

        info = {
            "web_url": pipeline.web_url,
            "created_at": format_datetime_for_ai(pipeline.created_at, timezone=self.timezone),
            "status": pipeline.status,
            "source": pipeline.source,
            "duration_seconds": pipeline.duration,
            "queued_duration_seconds": pipeline.queued_duration,
            "commit_sha": pipeline.sha,
            "commit": commit,
            "jobs": jobs,
        }
        return info

    async def get_merge_request_data(
        self,
        project_path_or_url: ProjectPathOrUrlType,
        merge_request_iid: Annotated[
            int,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The internal id of a GitLab merge request, can be extracted from a merge request url
                    if it ends in the following suffix: "/-/merge_requests/{merge_request_iid}".
                """)
            ),
        ],
    ) -> dict:
        """Fetch some details about a GitLab merge request, like diffs, title, description."""
        project_path = self.gitlab_url.extract_project_path(project_path_or_url)
        merge_request_data = await aget_merge_request_data(
            project=project_path,
            merge_request_iid=merge_request_iid,
            agraphql=self.agraphql,
            ahttpx_client=self.ahttpx,
        )
        return merge_request_data

    async def get_merge_request_data_from_url(
        self,
        merge_request_url: Annotated[
            str,
            pydantic.Field(
                description=inspect.cleandoc("""
                    The url for merge request, in the format:
                    "https://{gitlab_domain}/{project_path}/-/merge_requests/{merge_request_iid}".
                """)
            ),
        ],
    ) -> dict:
        """Fetch some details about a GitLab merge request, like diffs, title, description."""
        merge_request: MergeRequest = self.gitlab_url.extract_merge_request(merge_request_url)
        merge_request_data = await self.get_merge_request_data(
            project_path_or_url=merge_request.project_path,
            merge_request_iid=merge_request.merge_request_iid,
        )
        return merge_request_data
