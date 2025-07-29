import inspect


def get_prompts() -> list[callable]:
    prompts = [
        get_merge_request_prompt,
    ]
    return prompts


def get_merge_request_prompt(merge_request_url: str) -> str:
    """A prompt for reviewing a GitLab merge request."""
    prompt = inspect.cleandoc(f"""
        Your job is to conduct a thorough review of a GitLab merge request.
        The merge request url is "{merge_request_url}".
        Follow these steps:
        - Fetch the details for the GitLab merge request using provided MCP tool and merge request url.
        - Review the changes in the merge request, evaluate the quality of the code, check for any potential bugs and security issues.
        - Give a final verdict, whether the merge request is ready to be merged, if not, provide reasons and suggest next actions.
    """)
    return prompt
