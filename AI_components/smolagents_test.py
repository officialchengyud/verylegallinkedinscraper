import os
from smolagents import OpenAIServerModel, CodeAgent

model = OpenAIServerModel(
    model_id="gpt-4o",
    api_base="https://api.openai.com/v1",
    api_key=os.environ["OPENAI_API_KEY"],
)

agent = CodeAgent(tools=[], model=model, add_base_tools=True)

agent.run("Find the contact information or linkedin profile for a sales manager at 'Lunar Hard Seltzer', do not provide a generic email.")
