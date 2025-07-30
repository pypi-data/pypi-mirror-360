import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_confirmation, show_input
from tinybird.tb.modules.datafile.fixture import persist_fixture
from tinybird.tb.modules.feedback_manager import FeedbackManager


def mock(ctx: RunContext[TinybirdAgentContext], datasource_name: str, data_format: str, rows: int) -> str:
    """Create mock data for a datasource

    Args:
        datasource_name: Name of the datasource to create mock data for
        data_format: Format of the mock data to create. Options: ndjson, csv
        rows: Number of rows to create. If not provided, the default is 10

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
        data = ctx.deps.mock_data(datasource_name=datasource_name, data_format=data_format, rows=rows)
        fixture_path = persist_fixture(datasource_name, data, ctx.deps.folder, format=data_format)
        ctx.deps.append_data(datasource_name=datasource_name, path=str(fixture_path))
        click.echo(FeedbackManager.success(message=f"✓ Data generated for {datasource_name}"))
        ctx.deps.thinking_animation.start()
        return f"Mock data generated successfully for datasource {datasource_name}"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error generating mock data: {e}"
