#!/usr/bin/env python3
"""
maxs - main application module.

a minimalist strands agent with ollama integration.
"""

import argparse
import os
import sys

from strands import Agent

from maxs.models.models import create_model
from maxs.tools import bash, file_ops, use_agent


def create_agent(model_provider="ollama"):
    """
    Create a Strands Agent with Ollama model.

    Args:
        model_provider: Model provider, default ollama (default: qwen3:4b)
        host: Ollama host URL (default: http://localhost:11434)

    Returns:
        Agent: Configured Strands agent
    """
    model = create_model(provider=os.getenv("MODEL_PROVIDER", model_provider))

    # Create the agent
    agent = Agent(model=model, tools=[bash, file_ops, use_agent])

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

    system_prompt = os.getenv(
        "SYSTEM_PROMPT", "i'm maxs. minimalist agent. welcome to chat."
    )

    # Create agent
    agent = create_agent(model_provider)
    agent.system_prompt = system_prompt

    # Check if query provided as arguments
    if args.query:
        # Single query mode - join all arguments as the query
        query = " ".join(args.query)
        print(f"\n> {query}")

        try:
            agent(query)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)

        # Exit after single query
        return

    print("💡 Type 'exit', 'quit', or 'bye' to quit, or Ctrl+C")

    while True:
        try:
            q = input("\n> ")

            if q.lower() in ["exit", "quit", "bye"]:
                print("\n👋 Goodbye!")
                break

            if not q.strip():
                continue

            agent(q)

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
