import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_confirmation, show_input


def plan(ctx: RunContext[TinybirdAgentContext], plan: str) -> str:
    """Given a plan, ask the user for confirmation to implement it

    Args:
        plan (str): The plan to implement. Required.

    Returns:
        str: If the plan was implemented or not.
    """
    try:
        ctx.deps.thinking_animation.stop()
        click.echo(plan)
        confirmation = show_confirmation(
            title="Do you want to implement the plan?", skip_confirmation=ctx.deps.dangerously_skip_permissions
        )

        if confirmation == "review":
            click.echo()
            feedback = show_input(ctx.deps.workspace_name)
            ctx.deps.thinking_animation.start()
            return f"User did not confirm the proposed plan and gave the following feedback: {feedback}"

        ctx.deps.thinking_animation.start()

        if confirmation == "cancel":
            return "User cancelled the plan. Stop the process."

        return "User confirmed the plan. Implementing..."

    except Exception as e:
        return f"Error implementing the plan: {e}"
