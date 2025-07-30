import click
import requests
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.feedback_manager import FeedbackManager


def get_openapi_definition(ctx: RunContext[TinybirdAgentContext], cloud: bool = True):
    """Get the OpenAPI definition for all endpoints in the project:

    Args:
        cloud (bool): Whether to get the OpenAPI spec from cloud or local. Optional.

    Returns:
        str: The OpenAPI spec for all endpoints in the project.
    """

    cloud_or_local = "Cloud" if cloud else "Local"
    ctx.deps.thinking_animation.stop()

    click.echo(FeedbackManager.highlight(message=f"» Accessing Tinybird {cloud_or_local} endpoints"))
    try:
        url = f"{ctx.deps.host}/v0/pipes/openapi.json"

        result = requests.get(url, headers={"Authorization": f"Bearer {ctx.deps.token}"})
        if result.status_code != 200:
            raise Exception(f"Failed to get OpenAPI spec: {result.status_code} {result.text}")

        openapi_spec = result.text

        click.echo(FeedbackManager.success(message="✓ Done!"))
        click.echo()
        ctx.deps.thinking_animation.start()
        return f"OpenAPI spec for {cloud_or_local} endpoints: {openapi_spec}. <dev_note>Add the base url to each path so the user can copy paste if needed: {ctx.deps.host}</dev_note>"
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Error getting OpenAPI spec: {e}"))
        ctx.deps.thinking_animation.start()
        return f"Error getting OpenAPI spec: {e}"
