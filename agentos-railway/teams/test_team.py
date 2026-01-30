from agno.team import Team
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.hackernews import HackerNewsTools
from agno.tools.yfinance import YFinanceTools

news_agent = Agent(
    name="News Agent",
    role="Get trending tech news from HackerNews",
    tools=[HackerNewsTools()]
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get stock prices and financial data",
    tools=[YFinanceTools()]
)

team = Team(
    name="Research Team",
    members=[news_agent, finance_agent],
    model=OpenAIResponses(id="gpt-4o"),
    instructions="Delegate to the appropriate agent based on the request."
)

team.print_response("What are the trending AI stories and how is NVDA stock doing?", stream=True)