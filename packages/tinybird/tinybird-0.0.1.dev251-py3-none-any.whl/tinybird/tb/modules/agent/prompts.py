from pathlib import Path

from tinybird.tb.modules.project import Project

plan_instructions = """
When asked to create a plan, you MUST respond with this EXACT format and NOTHING ELSE:

Plan description: [One sentence describing what will be built]

Steps:
1. Connection: [name] - [description]
2. Datasource: [name] - [description] - Depends on: [connection_name (optional)]
3. Endpoint: [name] - [description] - Depends on: [resources]
4. Materialized pipe: [name] - [description] - Depends on: [resources]
5. Materialized datasource: [name] - [description] - Depends on: [resources]
6. Sink: [name] - [description] - Depends on: [resources]
7. Copy: [name] - [description] - Depends on: [resources]
8. Build project
9. Generate mock data: [datasource_name]
10. Append existing fixture: [fixture_pathname] - Target: [datasource_name]

<dev_notes>
You can skip steps where resources will not be created or updated.
Always add 'Build project' step after generating resources.
Always add 'Generate mock data' step after building project if a landing datasource was created without providing a fixture file.
Always add 'Append existing fixture' step after building project if a landing datasource was created after providing a fixture file.
Solve the specific user request, do not add extra steps that are not related to the user request.
Reuse the existing resources if possible.
</dev_notes>

Resource dependencies:
[resource_name]: [resources]
"""


sql_instructions = """
<sql_instructions>
    - The SQL query must be a valid ClickHouse SQL query that mixes ClickHouse syntax and Tinybird templating syntax (Tornado templating language under the hood).
    - SQL queries with parameters must start with "%" character and a newline on top of every query to be able to use the parameters. Examples:
    <invalid_query_with_parameters_no_%_on_top>
    SELECT * FROM events WHERE session_id={{String(my_param, "default_value")}}
    </invalid_query_with_parameters_no_%_on_top>
    <valid_query_with_parameters_with_%_on_top>
    %
    SELECT * FROM events WHERE session_id={{String(my_param, "default_value")}}
    </valid_query_with_parameters_with_%_on_top>
    - The Parameter functions like this one {{String(my_param_name,default_value)}} can be one of the following: String, DateTime, Date, Float32, Float64, Int, Integer, UInt8, UInt16, UInt32, UInt64, UInt128, UInt256, Int8, Int16, Int32, Int64, Int128, Int256
    - Parameter names must be different from column names. Pass always the param name and a default value to the function.
    - Use ALWAYS hardcoded values for default values for parameters.
    - Code inside the template {{template_expression}} follows the rules of Tornado templating language so no module is allowed to be imported. So for example you can't use now() as default value for a DateTime parameter. You need an if else block like this:
    <invalid_condition_with_now>
    AND timestamp BETWEEN {{DateTime(start_date, now() - interval 30 day)}} AND {{DateTime(end_date, now())}}
    </invalid_condition_with_now>
    <valid_condition_without_now>
    {{%if not defined(start_date)%}}
    timestamp BETWEEN now() - interval 30 day
    {{%else%}}
    timestamp BETWEEN {{DateTime(start_date)}}
    {{%end%}}
    {{%if not defined(end_date)%}}
    AND now()
    {{%else%}}
    AND {{DateTime(end_date)}}
    {{%end%}}
    </valid_condition_without_now>
    - Parameters must not be quoted.
    - When you use defined function with a paremeter inside, do NOT add quotes around the parameter:
    <invalid_defined_function_with_parameter>{{% if defined('my_param') %}}</invalid_defined_function_with_parameter>
    <valid_defined_function_without_parameter>{{% if defined(my_param) %}}</valid_defined_function_without_parameter>
    - Use datasource names as table names when doing SELECT statements.
    - Do not use pipe names as table names.
    - The available datasource names to use in the SQL are the ones present in the existing_resources section or the ones you will create.
    - Use node names as table names only when nodes are present in the same file.
    - Do not reference the current node name in the SQL.
    - SQL queries only accept SELECT statements with conditions, aggregations, joins, etc.
    - Do NOT use CREATE TABLE, INSERT INTO, CREATE DATABASE, etc.
    - Use ONLY SELECT statements in the SQL section.
    - INSERT INTO is not supported in SQL section.
    - When using functions try always ClickHouse functions first, then SQL functions.
    - Parameters are never quoted in any case.
    - Use the following syntax in the SQL section for the iceberg table function: iceberg('s3://bucket/path/to/table', {{tb_secret('aws_access_key_id')}}, {{tb_secret('aws_secret_access_key')}})
    - Use the following syntax in the SQL section for the postgres table function: postgresql('host:port', 'database', 'table', {{tb_secret('db_username')}}, {{tb_secret('db_password')}}), 'schema')
</sql_instructions>
"""

datafile_instructions = """
<datafile_instructions>
- Endpoint files will be created under the `/endpoints` folder.
- Materialized pipe files will be created under the `/materialized` folder.
- Sink pipe files will be created under the `/sinks` folder.
- Copy pipe files will be created under the `/copies` folder.
- Connection files will be created under the `/connections` folder.
- Datasource files will be created under the `/datasources` folder.
</datafile_instructions>
"""


def resources_prompt(project: Project) -> str:
    files = project.get_project_files()
    fixture_files = project.get_fixture_files()

    resources_content = "# Existing resources in the project:\n"
    if files:
        paths = [Path(file_path) for file_path in files]

        resources_content += "\n".join(
            [
                f"""
    <resource>
        <path>{file_path.relative_to(project.folder)}</path>
        <type>{get_resource_type(file_path)}</type>
        <name>{file_path.stem}</name>
        <content>{file_path.read_text()}</content>
    </resource>
    """
                for file_path in paths
            ]
        )
    else:
        resources_content += "No resources found"

    fixture_content = "# Fixture files in the project:\n"
    if fixture_files:
        paths = [Path(file_path) for file_path in fixture_files]
        fixture_content += "\n".join(
            [
                f"""
    <fixture>
        <path>{file_path.relative_to(project.folder)}</path>
        <name>{file_path.stem}</name>
    </fixture>
    """
                for file_path in paths
            ]
        )
    else:
        fixture_content += "No fixture files found"

    return resources_content + "\n" + fixture_content


def get_resource_type(path: Path) -> str:
    if path.suffix.lower() == ".pipe":
        return Project.get_pipe_type(str(path))
    elif path.suffix.lower() == ".datasource":
        return "datasource"
    elif path.suffix.lower() == ".connection":
        return "connection"
    return "unknown"
