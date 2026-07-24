import sys
import json
import asyncio
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import ToolMessage
import uuid

SYSTEM_PROMPT = """You are a precise file management assistant and web/app automation agent.
You have access to tools to read, write, list, delete files, and interact with applications.

CRITICAL RULES:
1. To delete a file, follow a two-step process:
   - Step 1: Call request_delete_confirmation(filename).
   - Step 2: Only call confirm_delete_file(token) after the user says "yes" or "confirm".
2. If a user asks for current information, recent facts, or anything that may require live web data, use the web search tool before answering. If you do not already have enough context to answer from memory or the workspace, call the search tool and use the returned results. Prefer the Bing News fallback path for live news/current-events questions.
3. If a user asks to open an application, use the application automation tool to launch it.
4. Always verify the JSON response status from tools before answering.
5. Prefer the tool result over stale model memory when the question is time-sensitive or fact-dependent.
6. Do not output raw JSON blocks in your text response — use the tool interface."""

MEMORY_LIMIT = 5


def remember_interaction(memory: list[dict[str, str]], user_query: str, assistant_reply: str) -> None:
    """Store a user/assistant exchange while keeping only the latest five."""
    memory.append({"user": user_query, "assistant": assistant_reply})
    if len(memory) > MEMORY_LIMIT:
        memory.pop(0)


def build_memory_context(memory: list[dict[str, str]], current_user_input: str) -> str:
    """Compose a concise prompt that includes recent conversation history."""
    if not memory:
        return current_user_input

    history_lines = []
    for index, item in enumerate(memory, start=1):
        history_lines.append(
            f"{index}. User: {item['user']}\n   Assistant: {item['assistant']}"
        )

    return (
        "Recent conversation memory:\n"
        + "\n".join(history_lines)
        + f"\n\nCurrent user request: {current_user_input}"
    )


def try_parse_tool_call(content: str) -> dict | None:
    """Detect if model output is a raw JSON tool call instead of a real tool_calls array."""
    try:
        content = content.strip()
        if not content.startswith("{"):
            return None
        parsed = json.loads(content)
        if "name" in parsed and "arguments" in parsed:
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass
    return None

async def run_agent():
    llm = ChatOllama(
        model="qwen3:4b", #"gemma4:e4b", #llama3.1:8b
        temperature=0.0
    )

    client_config = {
        "FileIO_Server": {
            "command": sys.executable,
            "args": ["MCP_file_server.py"],
            "transport": "stdio",
        }
    }

    print("Connecting to local MCP Server...")
    client = MultiServerMCPClient(client_config)

    try:
        tools = await client.get_tools()

        # Build a lookup map for manual dispatch
        tool_map = {tool.name: tool for tool in tools}

        agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt=SYSTEM_PROMPT
        )

        print("\nAgent initialized! Managing files in './workspace'.")
        print("Type 'exit' or 'quit' to close.\n")

        interaction_memory: list[dict[str, str]] = []

        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['exit', 'quit']:
                    break

                prompt_with_memory = build_memory_context(interaction_memory, user_input)
                assistant_reply = ""

                async for event in agent.astream(
                    {"messages": [("user", prompt_with_memory)]},
                    stream_mode="updates"
                ):
                    if "model" in event:
                        message = event["model"]["messages"][-1]

                        # ✅ Case 1: Proper structured tool call (model works correctly)
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            calls = ", ".join([tc['name'] for tc in message.tool_calls])
                            print(f"\n⚙️  [Calling tool: '{calls}']")

                        # ✅ Case 2: Model output raw JSON in content instead of tool_calls
                        elif message.content:
                            raw_call = try_parse_tool_call(message.content)
                            if raw_call:
                                tool_name = raw_call["name"]
                                tool_args = raw_call["arguments"]
                                print(f"\n⚙️  [Fallback: detected raw tool call for '{tool_name}']")

                                if tool_name in tool_map:
                                    try:
                                        result = await tool_map[tool_name].ainvoke(tool_args)
                                        print(f"📄 [Tool Response: {result}]\n")
                                    except Exception as e:
                                        print(f"❌ [Tool Error: {e}]\n")
                                else:
                                    print(f"❌ [Unknown tool '{tool_name}']\n")
                            else:
                                assistant_reply = message.content
                                print(f"\nAgent: {message.content}")

                    elif "tools" in event:
                        message = event["tools"]["messages"][-1]
                        print(f"📄 [Tool Response: {message.content}]\n")

                    else:
                        for key in event:
                            if key not in ("__end__",):
                                print(f"[DEBUG] Unhandled event key: '{key}'")

                if assistant_reply:
                    remember_interaction(interaction_memory, user_input, assistant_reply)

            except (EOFError, KeyboardInterrupt):
                break
    finally:
        pass

if __name__ == "__main__":
    asyncio.run(run_agent())