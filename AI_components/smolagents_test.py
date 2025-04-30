import os
from smolagents import OpenAIServerModel, CodeAgent

model = OpenAIServerModel(
    model_id="gpt-4.1-mini", # Optimizes performance and cost
    api_base="https://api.openai.com/v1",
    api_key=os.environ["OPENAI_API_KEY"],
)

with open("C:/Users/yashc/Desktop/verylegallinkedinscraper/AI_components/prompt.txt", "r", encoding="utf-8") as f:
    instructions = f.read()

agent = CodeAgent(tools=[], model=model, add_base_tools=True)

agent.run(f'{instructions}\n\nGo to market manager for pop mart based in United States')
