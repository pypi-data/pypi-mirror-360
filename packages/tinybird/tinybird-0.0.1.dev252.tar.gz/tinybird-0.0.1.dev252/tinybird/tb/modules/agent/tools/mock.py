from typing import Optional

import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_confirmation, show_input
from tinybird.tb.modules.datafile.fixture import persist_fixture
from tinybird.tb.modules.feedback_manager import FeedbackManager


def mock(
    ctx: RunContext[TinybirdAgentContext],
    datasource_name: str,
    data_format: str,
    rows: int,
    context: Optional[str] = None,
) -> str:
    """Create mock data for a datasource

    Args:
        datasource_name: Name of the datasource to create mock data for
        data_format: Format of the mock data to create. Options: ndjson, csv
        rows: Number of rows to create. If not provided, the default is 10
        context: Extra context to be used to generate the mock data. Optional.

    Returns:
        str: Message indicating the success or failure of the mock data generation
    """
    try:
        ctx.deps.thinking_animation.stop()
        confirmation = show_confirmation(
            title=f"Generate mock data for datasource '{datasource_name}'?",
            skip_confirmation=ctx.deps.dangerously_skip_permissions,
        )

        if confirmation == "review":
            click.echo()
            feedback = show_input(ctx.deps.workspace_name)
            ctx.deps.thinking_animation.start()
            return f"User did not confirm mock data generation and gave the following feedback: {feedback}"

        if confirmation == "cancel":
            ctx.deps.thinking_animation.start()
            return "User cancelled mock data generation. Stop mock data generation."

        click.echo(FeedbackManager.highlight(message=f"\n» Generating mock data for {datasource_name}..."))
        data = ctx.deps.mock_data(datasource_name=datasource_name, data_format=data_format, rows=rows, context=context)
        fixture_path = persist_fixture(datasource_name, data, ctx.deps.folder, format=data_format)
        ctx.deps.append_data(datasource_name=datasource_name, path=str(fixture_path))
        click.echo(FeedbackManager.success(message=f"✓ Data generated for {datasource_name}"))
        ctx.deps.thinking_animation.start()
        return f"Mock data generated successfully for datasource {datasource_name}"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        error_message = str(e)
        click.echo(FeedbackManager.error(message=error_message))
        try:
            if "in quarantine" in error_message:
                click.echo(
                    FeedbackManager.highlight(message=f"\n» Looking for errors in {datasource_name}_quarantine...")
                )
                query = f"select * from {datasource_name}_quarantine order by insertion_date desc limit 5 FORMAT CSVWithNames"
                quarantine_data = ctx.deps.execute_local_query(query=query)
                error_message = (
                    error_message
                    + f"\nThese are the first 5 rows of the quarantine table for datasource '{datasource_name}':\n{quarantine_data}. Use again `mock` tool but add this issue to the context."
                )

        except Exception as quarantine_error:
            error_message = error_message + f"\nError accessing to {datasource_name}_quarantine: {quarantine_error}"

        ctx.deps.thinking_animation.start()
        return f"Error generating mock data: {error_message}"
