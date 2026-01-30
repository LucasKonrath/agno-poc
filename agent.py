from agno.agent import Agent
from agno.models.openai import OpenAIResponses

agent = Agent(model=OpenAIResponses(id="gpt-5.2"))

agent.print_response("Hi! I'm Alice. I work at Anthropic as a research scientist.", stream=True)
