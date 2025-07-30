from typing import Dict

import click
from dotenv import dotenv_values

from tinybird.tb.client import TinyB
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.project import Project


def load_secrets(project: Project, client: TinyB):
    try:
        env_vars: Dict[str, str] = {}

        # Load secrets from .env file
        env_file = ".env"
        env_path = project.path / env_file

        if env_path.exists():
            env_values = dotenv_values(env_path)
            if env_values:
                env_vars.update({k: v for k, v in env_values.items() if v is not None})

        # Load secrets from .env.local file
        env_file = ".env.local"
        env_path = project.path / env_file

        if env_path.exists():
            env_values = dotenv_values(env_path)
            if env_values:
                env_vars.update({k: v for k, v in env_values.items() if v is not None})

        if len(env_vars.keys()) == 0:
            return

        click.echo(FeedbackManager.highlight(message="\n» Loading secrets from .env files..."))

        for name, value in env_vars.items():
            if not value:
                continue

            try:
                existing_secret = client.get_secret(name)
            except Exception:
                existing_secret = None
            try:
                if existing_secret:
                    client.update_secret(name, value)
                else:
                    client.create_secret(name, value)
            except Exception as e:
                click.echo(FeedbackManager.error(message=f"✗ Error setting secret '{name}': {e}"))

        click.echo(FeedbackManager.success(message="✓ Secrets loaded!"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))
