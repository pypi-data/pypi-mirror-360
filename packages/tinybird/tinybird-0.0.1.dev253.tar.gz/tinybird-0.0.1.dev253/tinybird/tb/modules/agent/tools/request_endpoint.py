from typing import Optional

import click
import humanfriendly
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.common import echo_safe_humanfriendly_tables_format_smart_table
from tinybird.tb.modules.feedback_manager import FeedbackManager


def request_endpoint(
    ctx: RunContext[TinybirdAgentContext],
    endpoint_name: str,
    params: Optional[dict[str, str]] = None,
    cloud: bool = True,
):
    """Request an endpoint:

    Args:
        endpoint_name (str): The name of the endpoint to request. Required.
        params (dict): The parameters to pass to the endpoint. Optional.
        cloud (bool): Whether to request the endpoint on cloud or local. Optional.

    Returns:
        str: The result of the query.
    """
    try:
        cloud_or_local = "cloud" if cloud else "local"
        ctx.deps.thinking_animation.stop()

        click.echo(
            FeedbackManager.highlight(
                message=f"» Calling endpoint {endpoint_name} in {cloud_or_local} environment with params {params}"
            )
        )

        request_endpoint = ctx.deps.request_endpoint_cloud if cloud else ctx.deps.request_endpoint_local
        result = request_endpoint(endpoint_name=endpoint_name, params=params)
        stats = result["statistics"]
        seconds = stats["elapsed"]
        rows_read = humanfriendly.format_number(stats["rows_read"])
        bytes_read = humanfriendly.format_size(stats["bytes_read"])

        click.echo(FeedbackManager.success_print_pipe(pipe=endpoint_name))
        click.echo(FeedbackManager.info_query_stats(seconds=seconds, rows=rows_read, bytes=bytes_read))

        if not result["data"]:
            click.echo(FeedbackManager.info_no_rows())
        else:
            echo_safe_humanfriendly_tables_format_smart_table(
                data=[d.values() for d in result["data"][:5]], column_names=result["data"][0].keys()
            )
            click.echo("Showing first 5 results\n")
        ctx.deps.thinking_animation.start()
        return f"Result for endpoint {endpoint_name} with params {params} in {cloud_or_local} environment: {result}. Do not show result is already shown in the console."
    except Exception as e:
        error = str(e)
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=error))
        ctx.deps.thinking_animation.start()
        if "not found" in error.lower() and cloud:
            return f"Error executing query: {error}. Please run the query against Tinybird local instead of cloud."
        else:
            return f"Error executing query: {error}. Please try again."
