import json
from pathlib import Path

from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext


def read_fixture_data(ctx: RunContext[TinybirdAgentContext], fixture_pathname: str):
    """Read fixture data in the project folder

    Args:
        fixture_pathname (str): a path to a fixture file. Required.

    Returns:
        str: The content of the fixture data file.
    """
    fixture_path = Path(ctx.deps.folder) / fixture_pathname.lstrip("/")

    if not fixture_path.exists():
        return f"No fixture data found for {fixture_pathname}. Please check the name of the fixture and try again."

    response = ctx.deps.analyze_fixture(fixture_path=str(fixture_path))
    # limit content to first 10 rows
    data = response["preview"]["data"][:10]
    columns = response["analysis"]["columns"]

    return f"#Result of analysis of {fixture_pathname}:\n##Columns:\n{json.dumps(columns)}\n##Data sample:\n{json.dumps(data)}"
