import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_options
from tinybird.tb.modules.feedback_manager import FeedbackManager


def get_deploy_confirmation() -> bool:
    """Get user confirmation for deploying the project"""
    while True:
        result = show_options(
            options=["Yes, deploy the project", "No, and tell Tinybird Code what to do"],
            title="Do you want to deploy the project?",
        )

        if result is None:  # Cancelled
            return False

        if result.startswith("Yes"):
            return True
        elif result.startswith("No"):
            return False

        return False


def deploy(ctx: RunContext[TinybirdAgentContext]) -> str:
    """Deploy the project"""
    try:
        ctx.deps.thinking_animation.stop()
        confirmation = ctx.deps.dangerously_skip_permissions or get_deploy_confirmation()
        ctx.deps.thinking_animation.start()

        if not confirmation:
            return "User cancelled deployment."

        ctx.deps.thinking_animation.stop()
        ctx.deps.deploy_project()
        ctx.deps.thinking_animation.start()
        return "Project deployed successfully"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Error depoying project: {e}"
