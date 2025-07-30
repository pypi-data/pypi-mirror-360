import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.feedback_manager import FeedbackManager


def get_endpoint_stats(
    ctx: RunContext[TinybirdAgentContext], endpoint_name: str, interval_days: int = 1, cloud: bool = True
):
    """Get stats for an endpoint:

    Args:
        endpoint_name (str): The name of the endpoint to get stats for. Required.
        interval_days (int): The number of days to get stats for. Optional.
        cloud (bool): Whether to get stats from cloud or local. Optional.

    Returns:
        str: The result of the stats.
    """
    if interval_days == 1:
        pipe_stats = "tinybird.pipe_stats_rt"
        date_column = "start_datetime"
    else:
        pipe_stats = "tinybird.pipe_stats"
        date_column = "date"

    days = "day" if interval_days == 1 else "days"
    cloud_or_local = "cloud" if cloud else "local"
    ctx.deps.thinking_animation.stop()

    click.echo(
        FeedbackManager.highlight(
            message=f"» Analyzing {cloud_or_local} requests in the last {interval_days} {days} for '{endpoint_name}' endpoint"
        )
    )

    query = f"""SELECT * FROM {pipe_stats} 
    WHERE {date_column} > NOW() - INTERVAL {interval_days} DAY
    AND pipe_name = '{endpoint_name}'
    LIMIT 100
    FORMAT JSON
    """

    execute_query = ctx.deps.execute_cloud_query if cloud else ctx.deps.execute_local_query

    result = execute_query(query=query)
    click.echo(FeedbackManager.success(message="✓ Done!"))
    click.echo()
    ctx.deps.thinking_animation.start()
    return f"Result for {endpoint_name} in the last {interval_days} {days}: {result}"
