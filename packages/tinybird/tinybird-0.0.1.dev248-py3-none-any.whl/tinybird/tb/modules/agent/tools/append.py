import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_options
from tinybird.tb.modules.feedback_manager import FeedbackManager


def get_append_confirmation(datasource_name: str) -> bool:
    """Get user confirmation for appending existing fixture"""
    while True:
        result = show_options(
            options=["Yes, append existing fixture", "No, and tell Tinybird Code what to do"],
            title=f"Do you want to append existing fixture for datasource {datasource_name}?",
        )

        if result is None:  # Cancelled
            return False

        if result.startswith("Yes"):
            return True
        elif result.startswith("No"):
            return False

        return False


def append(ctx: RunContext[TinybirdAgentContext], datasource_name: str, fixture_pathname: str) -> str:
    """Append existing fixture to a datasource

    Args:
        datasource_name: Name of the datasource to append fixture to
        fixture_pathname: Path to the fixture file to append

    Returns:
        str: Message indicating the success or failure of the appending
    """
    try:
        ctx.deps.thinking_animation.stop()
        confirmation = ctx.deps.dangerously_skip_permissions or get_append_confirmation(datasource_name)
        ctx.deps.thinking_animation.start()

        if not confirmation:
            return "User rejected appending existing fixture. Skipping..."

        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.highlight(message=f"\n» Appending {fixture_pathname} to {datasource_name}..."))
        ctx.deps.append_data(datasource_name=datasource_name, path=fixture_pathname)
        click.echo(FeedbackManager.success(message=f"✓ Data appended to {datasource_name}"))
        ctx.deps.thinking_animation.start()
        return f"Data appended to {datasource_name}"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error appending fixture {fixture_pathname} to {datasource_name}: {e}"
