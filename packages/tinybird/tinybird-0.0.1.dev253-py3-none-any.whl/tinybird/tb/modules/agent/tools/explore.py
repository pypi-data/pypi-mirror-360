from pydantic_ai import RunContext

from tinybird.tb.modules.agent.utils import TinybirdAgentContext


def explore_data(ctx: RunContext[TinybirdAgentContext], prompt: str):
    """Explore production data in the current workspace

    Args:
        prompt (str): The prompt to explore data with. Required.

    Returns:
        str: The result of the exploration.
    """
    return ctx.deps.explore_data(prompt)
