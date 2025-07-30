import click
from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext
from tinybird.tb.modules.feedback_manager import FeedbackManager


def deploy_check(ctx: RunContext[TinybirdAgentContext]) -> str:
    """Check that project can be deployed"""
    try:
        ctx.deps.thinking_animation.stop()
        ctx.deps.deploy_check_project()
        ctx.deps.thinking_animation.start()
        return "Project can be deployed"
    except Exception as e:
        ctx.deps.thinking_animation.stop()
        click.echo(FeedbackManager.error(message=e))
        ctx.deps.thinking_animation.start()
        return f"Project cannot be deployed: {e}"
