from tinybird.tb.modules.agent.utils import Datafile


def preview_datafile(name: str, type: str, description: str, content: str, pathname: str) -> Datafile:
    """Preview the content of a datafile before creating it

    Args:
        name (str): The name of the datafile. Required.
        type (str): The type of the datafile. Options: datasource, endpoint, materialized, sink, copy, connection. Required.
        description (str): The description of the datafile. Required.
        content (str): The content of the datafile. Required.
        pathname (str): The pathname of the datafile where the file will be created. Required.

    Returns:
        Datafile: The datafile preview.
    """

    return Datafile(
        type=type,
        name=name,
        content=content,
        description=description,
        pathname=pathname,
    )
