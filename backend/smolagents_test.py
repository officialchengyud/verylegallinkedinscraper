import os
from smolagents import OpenAIServerModel, CodeAgent


def contact_finder_tool(user_query):
    """Use this function to find companies or contacts from the internet.

    Args:
        user_query (str): The user's query to find companies or contacts.

    Returns:
        str: Array of companies or contacts as JSON objects.
    """

    model = OpenAIServerModel(
        model_id="gpt-4.1-mini", # Optimizes performance and cost
        api_base="https://api.openai.com/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    with open("prompt.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    agent = CodeAgent(tools=[], model=model, add_base_tools=True)

    agent.run(f'{instructions}\n\n{user_query}')

# if __name__ == "__main__":
#     user_query = "Find me a list of contacts for the company 'OpenAI' in the USA."
#     contact_finder_tool(user_query)