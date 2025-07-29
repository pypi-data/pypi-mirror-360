import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_options


def get_plan_confirmation() -> bool:
    """Get user confirmation for implementing a plan"""
    while True:
        result = show_options(
            options=["Yes, implement the plan", "No, and tell Tinybird Code what to do"],
            title="Do you want to implement the plan?",
        )

        if result is None:  # Cancelled
            return False

        if result.startswith("Yes"):
            return True
        elif result.startswith("No"):
            return False

        return False


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
        confirmation = ctx.deps.dangerously_skip_permissions or get_plan_confirmation()
        ctx.deps.thinking_animation.start()

        if not confirmation:
            return "Plan was not implemented. User cancelled implementation."

        return "User confirmed the plan. Implementing..."

    except Exception as e:
        return f"Error implementing the plan: {e}"
