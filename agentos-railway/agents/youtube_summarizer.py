"""
YouTube Summarizer Agent
=========

An agent that uses YouTube Tools to summarize videos.

Test:
    python -m agents.youtube_summarizer
"""

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.youtube import YouTubeTools

from db import get_postgres_db

# ============================================================================
# Setup
# ============================================================================
agent_db = get_postgres_db()

# ============================================================================
# Agent Instructions
# ============================================================================
instructions = """\
You are a helpful assistant with access to external tools via YouTube Tools.
## How You Work
1. Understand what the user needs
2. Use your tools to find information or take action
3. Provide clear answers based on tool results
4. If a tool can't help, say so and suggest alternatives
## Guidelines
- Be direct and concise
- Explain what you're doing when using tools
"""

# ============================================================================
# Create Agent
# ============================================================================
youtube_summarizer_agent = Agent(
    id="youtube-summarizer-agent",
    name="YouTube Summarizer Agent",
    model=OpenAIResponses(id="gpt-5.2"),
    db=agent_db,
    tools=[YouTubeTools()],
    instructions=instructions,
    enable_agentic_memory=True,
    add_datetime_to_context=True,
    add_history_to_context=True,
    read_chat_history=True,
    num_history_runs=5,
    markdown=True,
)

if __name__ == "__main__":
    youtube_summarizer_agent.print_response("What tools do you have access to?", stream=True)
