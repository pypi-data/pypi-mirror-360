import json
from pathlib import Path

import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.feedback_manager import FeedbackManager


def read_fixture_data(ctx: RunContext[TinybirdAgentContext], fixture_pathname: str):
    """Read fixture data in the project folder

    Args:
        fixture_pathname (str): a path to a fixture file. Required.

    Returns:
        str: The content of the fixture data file.
    """
    ctx.deps.thinking_animation.stop()
    click.echo(FeedbackManager.highlight(message=f"» Analyzing {fixture_pathname}..."))
    fixture_path = Path(ctx.deps.folder) / fixture_pathname.lstrip("/")

    if not fixture_path.exists():
        click.echo(FeedbackManager.error(message=f"No fixture data found for {fixture_pathname}."))
        ctx.deps.thinking_animation.start()
        return f"No fixture data found for {fixture_pathname}. Please check the name of the fixture and try again."

    response = ctx.deps.analyze_fixture(fixture_path=str(fixture_path))
    click.echo(FeedbackManager.success(message="✓ Done!\n"))
    ctx.deps.thinking_animation.start()
    # limit content to first 10 rows
    data = response["preview"]["data"][:10]
    columns = response["analysis"]["columns"]

    return f"#Result of analysis of {fixture_pathname}:\n##Columns:\n{json.dumps(columns)}\n##Data sample:\n{json.dumps(data)}"
