#!/usr/bin/env python3
"""
maxs - main application module.

a minimalist strands agent.
"""

import argparse
import base64
import os
import sys
import datetime
import json
from typing import Any
import uuid
from pathlib import Path

from strands import Agent
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from maxs.models.models import create_model
from maxs.handlers.callback_handler import callback_handler


def get_shell_history_file():
    """Get the maxs-specific history file path."""
    # Use /tmp/.maxs_history as requested
    maxs_history = Path("/tmp/.maxs_history")
    return str(maxs_history)


def get_messages_dir():
    """Get the maxs messages directory path."""
    messages_dir = Path("/tmp/.maxs")
    messages_dir.mkdir(exist_ok=True)
    return messages_dir


def get_session_file():
    """Get or create session file path."""
    messages_dir = get_messages_dir()

    # Generate session ID based on date and UUID
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    session_id = str(uuid.uuid4())[:8]  # Short UUID

    session_file = messages_dir / f"{today}-{session_id}.json"
    return str(session_file)


def save_agent_messages(agent, session_file):
    """Save agent.messages to JSON file."""
    try:
        # Convert messages to serializable format
        messages_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "messages": [],
        }

        # Handle different message formats
        for msg in agent.messages:
            if hasattr(msg, "to_dict"):
                # If message has to_dict method
                messages_data["messages"].append(msg.to_dict())
            elif hasattr(msg, "__dict__"):
                # If message is an object with attributes
                msg_dict = {}
                for key, value in msg.__dict__.items():
                    try:
                        # Try to serialize the value
                        json.dumps(value)
                        msg_dict[key] = value
                    except (TypeError, ValueError):
                        # If not serializable, convert to string
                        msg_dict[key] = str(value)
                messages_data["messages"].append(msg_dict)
            else:
                # Fallback: convert to string
                messages_data["messages"].append(str(msg))

        # Write to file
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(messages_data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        # Silently fail if we can't save messages
        print(f"⚠️  Warning: Could not save messages: {e}")


def get_last_messages():
    """Get the last N messages from maxs history for context."""
    try:
        history_file = get_shell_history_file()
        if not os.path.exists(history_file):
            return ""

        # Get message count from environment variable, default to 10
        message_count = int(os.getenv("MAXS_LAST_MESSAGE_COUNT", "10"))

        with open(history_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Filter for maxs queries and results, get last N
        maxs_lines = [
            line.strip()
            for line in lines
            if "# maxs:" in line or "# maxs_result:" in line
        ]
        recent_lines = (
            maxs_lines[-message_count:]
            if len(maxs_lines) >= message_count
            else maxs_lines
        )

        if not recent_lines:
            return ""

        # Format for context with timestamps
        context = (
            f"\n\nRecent conversation context (last {len(recent_lines)} messages):\n"
        )
        for line in recent_lines:
            # Extract timestamp from shell history format: ": timestamp:0;# content"
            if line.startswith(": ") and ":0;# " in line:
                try:
                    timestamp_str = line.split(":")[1]
                    timestamp = int(timestamp_str)
                    readable_time = datetime.datetime.fromtimestamp(timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                except (ValueError, IndexError):
                    readable_time = "????-??-?? ??:??:??"
            else:
                readable_time = "????-??-?? ??:??:??"

            if "# maxs:" in line:
                query = line.split("# maxs:")[-1].strip()
                context += f"[{readable_time}] you: {query}\n"
            elif "# maxs_result:" in line:
                result = line.split("# maxs_result:")[-1].strip()
                context += f"[{readable_time}] me: {result}\n"

        return context
    except Exception:
        return ""


def append_to_shell_history(query, response):
    """Append the interaction to shell history."""
    try:
        history_file = get_shell_history_file()

        # Format the entry for shell history
        # Use a comment format that's shell-compatible
        timestamp = os.popen("date +%s").read().strip()

        with open(history_file, "a", encoding="utf-8") as f:
            # Add the query
            f.write(f": {timestamp}:0;# maxs: {query}\n")
            # Add a compressed version of the response
            response_summary = (
                str(response).replace("\n", " ")[
                    : int(os.getenv("MAXS_RESPONSE_SUMMARY_LENGTH", "200"))
                ]
                + "..."
            )
            f.write(f": {timestamp}:0;# maxs_result: {response_summary}\n")

    except Exception as e:
        # Silently fail if we can't write to history
        pass


def setup_otel() -> None:
    """Setup OpenTelemetry if configured."""
    otel_host = os.environ.get("LANGFUSE_HOST")

    if otel_host:
        public_key = os.environ.get("LANGFUSE_PUBLIC_KEY", "")
        secret_key = os.environ.get("LANGFUSE_SECRET_KEY", "")

        if public_key and secret_key:
            auth_token = base64.b64encode(
                f"{public_key}:{secret_key}".encode()
            ).decode()
            otel_endpoint = f"{otel_host}/api/public/otel/v1/traces"

            os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = otel_endpoint
            os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = (
                f"Authorization=Basic {auth_token}"
            )


def get_tools() -> dict[str, Any]:
    """Returns the filtered collection of available agent tools for strands.

    This function first gets all available tools, then filters them based on
    the STRANDS_TOOLS environment variable if it exists.

    Returns:
        Dict[str, Any]: Dictionary mapping tool names to tool functions
    """
    # First get all tools
    tools = _get_all_tools()

    # Then apply filtering based on environment variable
    return _filter_tools(tools)


def _get_all_tools() -> dict[str, Any]:
    """Returns all available tools without filtering.

    Returns:
        Dict[str, Any]: Dictionary mapping tool names to tool functions
    """
    tools = {}

    try:
        # Strands tools
        from maxs.tools import (
            bash,
            tcp,
            use_agent,
            scraper,
            tasks,
            use_computer,
            environment,
            dialog,
        )

        tools = {
            "bash": bash,
            "tcp": tcp,
            "use_agent": use_agent,
            "scraper": scraper,
            "tasks": tasks,
            "use_computer": use_computer,
            "environment": environment,
            "dialog": dialog,
        }

    except ImportError as e:
        print(f"Warning: Could not import all tools: {e!s}")

    return tools


def _filter_tools(all_tools: dict[str, Any]) -> dict[str, Any]:
    """Filter tools based on STRANDS_TOOLS environment variable.

    Supports both comma-separated strings and JSON arrays for flexibility.

    Args:
        all_tools: Dictionary of all available tools

    Returns:
        Dict[str, Any]: Filtered dictionary of tools
    """
    # Get tool filter from environment variable
    tool_filter_str = os.getenv("STRANDS_TOOLS")

    # If env var not set or set to 'ALL', return all tools
    if not tool_filter_str or tool_filter_str == "ALL":
        return all_tools

    tool_filter = None

    # First try to parse as JSON array
    try:
        tool_filter = json.loads(tool_filter_str)
        if not isinstance(tool_filter, list):
            tool_filter = None
    except json.JSONDecodeError:
        # If JSON parsing fails, try comma-separated string
        pass

    # If JSON parsing failed or didn't produce a list, try comma-separated
    if tool_filter is None:
        # Handle comma-separated string format
        tool_filter = [
            tool.strip() for tool in tool_filter_str.split(",") if tool.strip()
        ]

        # If we still don't have a valid list, return all tools
        if not tool_filter:
            print(
                "Warning: STRANDS_TOOLS env var is not a valid JSON array or comma-separated string. Using all tools."
            )
            return all_tools

    # Filter the tools
    filtered_tools = {}
    for tool_name in tool_filter:
        if tool_name in all_tools:
            filtered_tools[tool_name] = all_tools[tool_name]
        else:
            print(
                f"Warning: Tool '{tool_name}' specified in STRANDS_TOOLS env var not found."
            )

    return filtered_tools


def create_agent(model_provider="ollama"):
    """
    Create a Strands Agent with Ollama model.

    Args:
        model_provider: Model provider, default ollama (default: qwen3:4b)
        host: Ollama host URL (default: http://localhost:11434)

    Returns:
        Agent: Configured Strands agent
    """
    setup_otel()

    model = create_model(provider=os.getenv("MODEL_PROVIDER", model_provider))

    tools = get_tools()

    # Create the agent
    agent = Agent(
        model=model, tools=list(tools.values()), callback_handler=callback_handler
    )

    return agent


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="maxs",
        description="minimalist strands agent with ollama integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  maxs                    # Interactive mode
  maxs hello world        # Single query mode
  maxs "what can you do"  # Single query with quotes
        """,
    )

    parser.add_argument(
        "query",
        nargs="*",
        help="Query to ask the agent (if provided, runs once and exits)",
    )

    return parser.parse_args()


def main():
    """Main entry point for the maxs agent."""
    # Parse command line arguments
    args = parse_args()

    # Show configuration
    model_provider = os.getenv("MODEL_PROVIDER", "ollama")

    # Get recent conversation context
    recent_context = get_last_messages()

    # Enhanced system prompt with history context and self-modification instructions
    base_prompt = "i'm maxs. minimalist agent. welcome to chat."
    self_modify_note = "\n\nNote: You can modify your system prompt using the environment tool: environment(action='set', name='SYSTEM_PROMPT', value='new prompt'). This allows self-modification of behavior and personality."

    default_system_prompt = base_prompt + recent_context + self_modify_note

    system_prompt = os.getenv("SYSTEM_PROMPT", default_system_prompt)

    # Create agent
    agent = create_agent(model_provider)
    agent.system_prompt = system_prompt

    # Get session file for storing messages
    session_file = get_session_file()
    print(f"📝 Session messages will be saved to: {session_file}")

    # Check if query provided as arguments
    if args.query:
        # Single query mode - join all arguments as the query
        query = " ".join(args.query)
        print(f"\n# {query}")

        try:
            result = agent(query)
            append_to_shell_history(query, result)
            save_agent_messages(agent, session_file)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

        # Exit after single query
        return

    print("💡 Type 'exit', 'quit', or 'bye' to quit, or Ctrl+C")

    # Set up prompt_toolkit with history
    history_file = get_shell_history_file()
    history = FileHistory(history_file)

    # Create completions from common commands and shell history
    common_commands = ["exit", "quit", "bye", "help", "clear", "ls", "pwd", "cd"]
    completer = WordCompleter(common_commands, ignore_case=True)

    while True:
        try:
            # Use prompt_toolkit for enhanced input
            q = prompt(
                "\n# ",
                history=history,
                auto_suggest=AutoSuggestFromHistory(),
                completer=completer,
                complete_while_typing=True,
            )

            if q.startswith("!"):
                shell_command = q[1:]  # Remove the ! prefix
                print(f"$ {shell_command}")

                try:
                    # Execute shell command directly using the shell tool
                    result = agent.tool.bash(
                        command=shell_command, timeout=900, shell=True
                    )
                    print(result["content"][0]["text"])
                    append_to_shell_history(q, result["content"][0]["text"])
                    save_agent_messages(agent, session_file)
                except Exception as e:
                    print(f"Shell command execution error: {str(e)}")
                continue

            if q.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye!")
                break

            if not q.strip():
                continue

            result = agent(q)
            append_to_shell_history(q, result)
            save_agent_messages(agent, session_file)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
