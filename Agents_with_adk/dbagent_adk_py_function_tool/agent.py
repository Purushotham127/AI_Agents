from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from google.adk.agents import Agent, SequentialAgent
from google.adk.tools.function_tool import FunctionTool

from .instructions import DB_AGENT_INSTRUCTION, FILE_CREATION_AGENT
from .db_util import (
    execute_read_query,
    find_column_across_databases,
    find_tables_by_column,
    get_table_schema,
    list_databases,
    list_tables,
    read_table_rows,
    search_column_values,
)
from .files_util import (
    write_csv_file,
    write_data_file,
    write_json_file,
    write_text_file,
    write_yaml_file,
)

MODEL_NAME = os.environ.get("GOOGLE_GENAI_MODEL", "gemini-2.0-flash")

# Database agent with read-only database utilities

db_agent = Agent(
    name="db_agent",
    instruction=DB_AGENT_INSTRUCTION,
    model=MODEL_NAME,
    tools=[
        FunctionTool(list_databases),
        FunctionTool(list_tables),
        FunctionTool(get_table_schema),
        FunctionTool(read_table_rows),
        FunctionTool(execute_read_query),
        FunctionTool(find_tables_by_column),
        FunctionTool(find_column_across_databases),
        FunctionTool(search_column_values),
    ],
    output_key="db_agent_output",
)

# File creation agent using file utility methods

files_agent = Agent(
    name="files_agent",
    instruction=FILE_CREATION_AGENT,
    model=MODEL_NAME,
    tools=[
        FunctionTool(write_text_file),
        FunctionTool(write_json_file),
        FunctionTool(write_csv_file),
        FunctionTool(write_yaml_file),
        FunctionTool(write_data_file),
    ],
)

root_agent = SequentialAgent(
    name="dbagent_adk_py_function_tool",
    sub_agents=[db_agent, files_agent],
)
