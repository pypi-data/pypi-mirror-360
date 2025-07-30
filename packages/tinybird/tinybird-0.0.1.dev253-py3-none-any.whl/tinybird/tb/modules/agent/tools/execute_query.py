import click
import humanfriendly
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.common import echo_safe_humanfriendly_tables_format_smart_table
from tinybird.tb.modules.feedback_manager import FeedbackManager


def execute_query(ctx: RunContext[TinybirdAgentContext], query: str, task: str, cloud: bool = True):
    """Execute a query:

    Args:
        query (str): The query to execute. Required.
        task (str): The purpose of the query. Required.
        cloud (bool): Whether to execute the query on cloud or local. Optional.

    Returns:
        str: The result of the query.
    """
    try:
        cloud_or_local = "cloud" if cloud else "local"
        ctx.deps.thinking_animation.stop()

        click.echo(FeedbackManager.highlight(message=f"» Executing query to {cloud_or_local}:\n{query}\n"))

        is_templating = query.strip().startswith("%")
        query_format = "FORMAT JSON"
        if is_templating:
            query = query.strip()
            query = f"%\nSELECT * FROM ({query}) {query_format}"
        else:
            query = f"SELECT * FROM ({query}) {query_format}"

        execute_query = ctx.deps.execute_cloud_query if cloud else ctx.deps.execute_local_query
        result = execute_query(query=query)
        stats = result["statistics"]
        seconds = stats["elapsed"]
        rows_read = humanfriendly.format_number(stats["rows_read"])
        bytes_read = humanfriendly.format_size(stats["bytes_read"])

        click.echo(FeedbackManager.info_query_stats(seconds=seconds, rows=rows_read, bytes=bytes_read))

        if not result["data"]:
            click.echo(FeedbackManager.info_no_rows())
        else:
            echo_safe_humanfriendly_tables_format_smart_table(
                data=[d.values() for d in result["data"]], column_names=result["data"][0].keys()
            )
        ctx.deps.thinking_animation.start()
        result["data"] = result["data"][:10]
        return f"Result for task '{task}' in {cloud_or_local} environment: {result}. The user is being shown the full result in the console but this message only contains the first 10 rows."
    except Exception as e:
        error = str(e)
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=error))
        ctx.deps.thinking_animation.start()
        if "not found" in error.lower() and cloud:
            return f"Error executing query: {error}. Please run the query against Tinybird local instead of cloud."
        else:
            return f"Error executing query: {error}. Please try again."
