import shlex
import subprocess
import sys
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Optional

import click
from pydantic_ai import Agent, Tool
from pydantic_ai.messages import ModelMessage

from tinybird.prompts import (
    connection_instructions,
    copy_pipe_instructions,
    datasource_example,
    datasource_instructions,
    gcs_connection_example,
    kafka_connection_example,
    materialized_pipe_instructions,
    pipe_example,
    pipe_instructions,
    s3_connection_example,
    sink_pipe_instructions,
)
from tinybird.tb.client import TinyB
from tinybird.tb.modules.agent.animations import ThinkingAnimation
from tinybird.tb.modules.agent.banner import display_banner
from tinybird.tb.modules.agent.memory import clear_history
from tinybird.tb.modules.agent.models import create_model, model_costs
from tinybird.tb.modules.agent.prompts import (
    datafile_instructions,
    plan_instructions,
    resources_prompt,
    sql_instructions,
)
from tinybird.tb.modules.agent.tools.append import append
from tinybird.tb.modules.agent.tools.build import build
from tinybird.tb.modules.agent.tools.create_datafile import create_datafile
from tinybird.tb.modules.agent.tools.deploy import deploy
from tinybird.tb.modules.agent.tools.deploy_check import deploy_check
from tinybird.tb.modules.agent.tools.explore import explore_data
from tinybird.tb.modules.agent.tools.get_endpoint_stats import get_endpoint_stats
from tinybird.tb.modules.agent.tools.get_openapi_definition import get_openapi_definition
from tinybird.tb.modules.agent.tools.mock import mock
from tinybird.tb.modules.agent.tools.plan import plan
from tinybird.tb.modules.agent.tools.preview_datafile import preview_datafile
from tinybird.tb.modules.agent.tools.read_fixture_data import read_fixture_data
from tinybird.tb.modules.agent.utils import TinybirdAgentContext, show_input
from tinybird.tb.modules.build_common import process as build_process
from tinybird.tb.modules.common import _analyze, _get_tb_client
from tinybird.tb.modules.config import CLIConfig
from tinybird.tb.modules.deployment_common import create_deployment
from tinybird.tb.modules.exceptions import CLIBuildException, CLIMockException
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.local_common import get_tinybird_local_client
from tinybird.tb.modules.login_common import login
from tinybird.tb.modules.mock_common import append_mock_data, create_mock_data
from tinybird.tb.modules.project import Project


class TinybirdAgent:
    def __init__(
        self,
        token: str,
        user_token: str,
        host: str,
        workspace_id: str,
        project: Project,
        dangerously_skip_permissions: bool,
    ):
        self.token = token
        self.user_token = user_token
        self.host = host
        self.dangerously_skip_permissions = dangerously_skip_permissions
        self.project = project
        self.messages: list[ModelMessage] = []
        self.agent = Agent(
            model=create_model(user_token, host, workspace_id),
            deps_type=TinybirdAgentContext,
            system_prompt=f"""
You are a Tinybird Code, an agentic CLI that can help users to work with Tinybird.

You are an interactive CLI tool that helps users with data engineering tasks. Use the instructions below and the tools available to you to assist the user.

# Tone and style
You should be concise, direct, and to the point. 
Remember that your output will be displayed on a command line interface. Your responses can use Github-flavored markdown for formatting. Do not use emojis.
Output text to communicate with the user; all text you output outside of tool use is displayed to the user. Only use tools to complete tasks. Never use tools like Bash or code comments as means to communicate with the user during the session.
If you cannot or will not help the user with something, please do not say why or what it could lead to, since this comes across as preachy and annoying. Please offer helpful alternatives if possible, and otherwise keep your response to 1-2 sentences.
IMPORTANT: You should minimize output tokens as much as possible while maintaining helpfulness, quality, and accuracy. Only address the specific query or task at hand, avoiding tangential information unless absolutely critical for completing the request. If you can answer in 1-3 sentences or a short paragraph, please do.
IMPORTANT: You should NOT answer with unnecessary preamble or postamble (such as explaining your code or summarizing your action), unless the user asks you to.
IMPORTANT: Keep your responses short, since they will be displayed on a command line interface. You MUST answer concisely with fewer than 4 lines (not including tool use or code generation), unless user asks for detail. Answer the user's question directly, without elaboration, explanation, or details. One word answers are best. Avoid introductions, conclusions, and explanations. You MUST avoid text before/after your response, such as "The answer is <answer>.", "Here is the content of the file..." or "Based on the information provided, the answer is..." or "Here is what I will do next...". Here are some examples to demonstrate appropriate verbosity:

# Proactiveness
You are allowed to be proactive, but only when the user asks you to do something. You should strive to strike a balance between:
Doing the right thing when asked, including taking actions and follow-up actions
Not surprising the user with actions you take without asking
For example, if the user asks you how to approach something, you should do your best to answer their question first, and not immediately jump into taking actions.
Do not add additional code explanation summary unless requested by the user. After working on a file, just stop, rather than providing an explanation of what you did.

# Code style
IMPORTANT: DO NOT ADD ANY COMMENTS unless asked by the user.

# Tools
You have access to the following tools:
1. `explore_data` - Explore data in the current workspace
2. `preview_datafile` - Preview the content of a datafile (datasource, endpoint, materialized, sink, copy, connection).
3. `create_datafile` - Create a file in the project folder. Confirmation will be asked by the tool before creating the file.
4. `plan` - Plan the creation or update of resources.
5. `build` - Build the project.
6. `deploy` - Deploy the project to Tinybird Cloud.
7. `deploy_check` - Check if the project can be deployed to Tinybird Cloud before deploying it.
8. `mock` - Create mock data for a landing datasource.
9. `read_fixture_data` - Read a fixture data file present in the project folder.
10. `append` - Append existing fixture to a datasource.
11. `get_endpoint_stats` - Get metrics of the requests to an endpoint.
12. `get_openapi_definition` - Get the OpenAPI definition for all endpoints that are built/deployed to Tinybird Cloud or Local.

# When creating or updating datafiles:
1. Use `plan` tool to plan the creation or update of resources.
2. If the user confirms the plan, go from 3 to 7 steps until all the resources are created, updated or skipped.
3. Use `preview_datafile` tool to preview the content of a datafile.
4. Without asking, use the `create_datafile` tool to create the datafile, because it will ask for confirmation before creating the file.
5. Check the result of the `create_datafile` tool to see if the datafile was created successfully.
6. If the datafile was created successfully, report the result to the user.
7. If the datafile was not created, finish the process and just wait for a new user prompt.
8. If the datafile was created successfully, but the built failed, try to fix the error and repeat the process.

# When creating a landing datasource given a .ndjson file:
- If the user does not specify anything about the desired schema, create a schema like this:
SCHEMA >
    `data` String `json:$`
- Use always json paths with .ndjson files.

# When user wants to optimize an endpoint:
First check if the query is optimized. E.g is filtering by a column present in the sorting key.
Avoid when possible to not update the landing datasource.
Check endpoint stats to analyze how the endpoint is performing. Use `get_endpoint_stats` tool to get the stats.
When your data is in Tinybird, you can create intermediate data sources to preprocess data and make the endpoints faster. This can be done by using materialized views or copy pipes.
- Copy pipes capture the result of a pipe at a specific point in time and write it to a target data source. They can run on a schedule or run on demand, making them ideal for event-sourced snapshots, data experimentation, and deduplication with snapshots.
- Materialized views continuously re-evaluate a query as new events are inserted, maintaining an always up-to-date derived dataset. Unlike copy pipes which create point-in-time snapshots, materialized views provide real-time transformations of your data.
Each approach has its own strengths and use cases:
- Use copy pipes when you need scheduled or on-demand snapshots of your data.
- Use materialized views when you need continuous, real-time transformations.
Finally, update the existing endpoint itself, do not add a new one.

IMPORTANT: If the user cancels some of the steps or there is an error in file creation, DO NOT continue with the plan. Stop the process and wait for the user before using any other tool.
IMPORTANT: Every time you finish a plan and start a new resource creation or update process, create a new plan before starting with the changes.

# When planning the creation or update of resources:
{plan_instructions}
{datafile_instructions}

# Working with datasource files:
{datasource_instructions}
{datasource_example}

# Working with any type of pipe file:
{pipe_instructions}
{pipe_example}

# Working with materialized pipe files:
{materialized_pipe_instructions}

# Working with sink pipe files:
{sink_pipe_instructions}

# Working with copy pipe files:
{copy_pipe_instructions}

# Working with SQL queries:
{sql_instructions}

# Working with connections files:
{connection_instructions}

# Connection examples:
Kafka: {kafka_connection_example}
S3: {s3_connection_example}
GCS: {gcs_connection_example}

# Info
Today is {datetime.now().strftime("%Y-%m-%d")}
""",
            tools=[
                Tool(explore_data, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(preview_datafile, docstring_format="google", require_parameter_descriptions=True, takes_ctx=False),
                Tool(create_datafile, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(plan, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(build, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(deploy, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(deploy_check, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(mock, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(read_fixture_data, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(append, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True),
                Tool(
                    get_endpoint_stats, docstring_format="google", require_parameter_descriptions=True, takes_ctx=True
                ),
                Tool(
                    get_openapi_definition,
                    docstring_format="google",
                    require_parameter_descriptions=True,
                    takes_ctx=True,
                ),
            ],
        )

    def _keep_recent_messages(self) -> list[ModelMessage]:
        """Keep only the last 5 messages to manage token usage."""
        return self.messages[-5:] if len(self.messages) > 5 else self.messages

    def run(self, user_prompt: str, config: dict[str, Any], project: Project) -> None:
        user_prompt = f"{user_prompt}\n\n{resources_prompt(project)}"
        client = TinyB(token=self.token, host=self.host)
        folder = self.project.folder
        click.echo()
        thinking_animation = ThinkingAnimation(message="Chirping", delay=0.15)
        thinking_animation.start()
        result = self.agent.run_sync(
            user_prompt,
            deps=TinybirdAgentContext(
                # context does not support the whole client, so we need to pass only the functions we need
                explore_data=client.explore_data,
                build_project=partial(build_project, project=project, config=config),
                deploy_project=partial(deploy_project, project=project, config=config),
                deploy_check_project=partial(deploy_check_project, project=project, config=config),
                mock_data=partial(mock_data, project=project, config=config),
                append_data=partial(append_data, config=config),
                analyze_fixture=partial(analyze_fixture, config=config),
                execute_cloud_query=partial(execute_cloud_query, config=config),
                execute_local_query=partial(execute_local_query, config=config),
                get_project_files=project.get_project_files,
                folder=folder,
                thinking_animation=thinking_animation,
                workspace_name=self.project.workspace_name,
                dangerously_skip_permissions=self.dangerously_skip_permissions,
                token=self.token,
                user_token=self.user_token,
                host=self.host,
            ),
            message_history=self.messages,
        )
        new_messages = result.new_messages()
        self.messages.extend(new_messages)
        thinking_animation.stop()
        usage = result.usage()
        request_tokens = usage.request_tokens or 0
        response_tokens = usage.response_tokens or 0
        total_tokens = usage.total_tokens or 0
        cost = (
            request_tokens * model_costs["input_cost_per_token"]
            + response_tokens * model_costs["output_cost_per_token"]
        )
        click.echo(result.output)
        click.echo("\n")

        if "@tinybird.co" in config.get("user_email", ""):
            click.echo(f"Input tokens: {request_tokens}")
            click.echo(f"Output tokens: {response_tokens}")
            click.echo(f"Total tokens: {total_tokens}")
            click.echo(f"Cost: ${cost:.6f}")
            click.echo("\n")


def run_agent(config: dict[str, Any], project: Project, dangerously_skip_permissions: bool):
    token = config.get("token", None)
    host = config.get("host", None)
    user_token = config.get("user_token", None)
    workspace_id = config.get("id", None)
    workspace_name = config.get("name", None)
    try:
        if not token or not host or not workspace_id or not user_token:
            yes = click.confirm(
                FeedbackManager.warning(
                    message="Tinybird Code requires authentication. Do you want to authenticate now? [Y/n]"
                ),
                prompt_suffix="",
                show_default=False,
                default=True,
            )
            if yes:
                click.echo()
                login(host, auth_host="https://cloud.tinybird.co", workspace=None, interactive=False, method="browser")
                click.echo()
                cli_config = CLIConfig.get_project_config()
                token = cli_config.get_token()
                user_token = cli_config.get_user_token()
                host = cli_config.get_host()

            if not token or not host or not user_token:
                click.echo(
                    FeedbackManager.error(message="Tinybird Code requires authentication. Run 'tb login' first.")
                )
                return

        display_banner()
        agent = TinybirdAgent(token, user_token, host, workspace_id, project, dangerously_skip_permissions)
        click.echo()
        click.echo(FeedbackManager.info(message="Describe what you want to create and I'll help you build it"))
        click.echo(FeedbackManager.info(message="Run /help for more commands"))

        click.echo()

    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Failed to initialize agent: {e}"))
        return

    # Interactive loop
    try:
        while True:
            try:
                user_input = show_input(workspace_name)
                if user_input.startswith("tb "):
                    cmd_parts = shlex.split(user_input)
                    subprocess.run(cmd_parts)
                    click.echo()
                    continue
                if user_input.lower() in ["/exit", "/quit"]:
                    click.echo(FeedbackManager.info(message="Goodbye!"))
                    break
                elif user_input.lower() == "/clear":
                    clear_history()
                    continue
                elif user_input.lower() == "/login":
                    click.echo()
                    subprocess.run(["tb", "login"], check=True)
                    click.echo()
                    continue
                elif user_input.lower() == "/help":
                    click.echo()
                    click.echo("• Describe what you want to create: 'Create a user analytics system'")
                    click.echo("• Ask for specific resources: 'Create a pipe to aggregate daily clicks'")
                    click.echo("• Connect to external services: 'Set up a Kafka connection for events'")
                    click.echo("• Type '/exit' or '/quit' to leave")
                    click.echo()
                    continue
                elif user_input.strip() == "":
                    continue
                else:
                    agent.run(user_input, config, project)

            except KeyboardInterrupt:
                click.echo(FeedbackManager.info(message="Goodbye!"))
                break
            except EOFError:
                click.echo(FeedbackManager.info(message="Goodbye!"))
                break

    except Exception as e:
        click.echo(FeedbackManager.error(message=f"Error: {e}"))
        sys.exit(1)


def build_project(config: dict[str, Any], project: Project, silent: bool = True, test: bool = True) -> None:
    local_client = get_tinybird_local_client(config, test=test, silent=silent)
    build_error = build_process(
        project=project, tb_client=local_client, watch=False, silent=silent, exit_on_error=False
    )
    if build_error:
        raise CLIBuildException(build_error)


def deploy_project(config: dict[str, Any], project: Project) -> None:
    client = _get_tb_client(config["token"], config["host"])
    create_deployment(
        project=project,
        client=client,
        config=config,
        wait=True,
        auto=True,
        allow_destructive_operations=False,
    )


def deploy_check_project(config: dict[str, Any], project: Project) -> None:
    client = _get_tb_client(config["token"], config["host"])
    create_deployment(
        project=project,
        client=client,
        config=config,
        check=True,
        wait=True,
        auto=True,
    )


def append_data(config: dict[str, Any], datasource_name: str, path: str) -> None:
    client = get_tinybird_local_client(config, test=False, silent=False)
    append_mock_data(client, datasource_name, path)


def mock_data(
    config: dict[str, Any],
    project: Project,
    datasource_name: str,
    data_format: str,
    rows: int,
    context: Optional[str] = None,
) -> list[dict[str, Any]]:
    client = get_tinybird_local_client(config, test=False, silent=False)
    cli_config = CLIConfig.get_project_config()
    datasource_path = project.get_resource_path(datasource_name, "datasource")

    if not datasource_path:
        raise CLIMockException(f"Datasource {datasource_name} not found")

    datasource_content = Path(datasource_path).read_text()
    return create_mock_data(
        datasource_name,
        datasource_content,
        rows,
        context or "",
        cli_config,
        config,
        cli_config.get_user_token() or "",
        client,
        data_format,
        project.folder,
    )


def analyze_fixture(config: dict[str, Any], fixture_path: str) -> dict[str, Any]:
    local_client = get_tinybird_local_client(config, test=False, silent=True)
    meta, _data = _analyze(fixture_path, local_client, Path(fixture_path).suffix.lstrip("."))
    return meta


def execute_cloud_query(config: dict[str, Any], query: str, pipe_name: Optional[str] = None) -> str:
    client = _get_tb_client(config["token"], config["host"])
    return client.query(sql=query, pipeline=pipe_name)


def execute_local_query(config: dict[str, Any], query: str, pipe_name: Optional[str] = None) -> str:
    local_client = get_tinybird_local_client(config, test=False, silent=True)
    return local_client.query(sql=query, pipeline=pipe_name)
