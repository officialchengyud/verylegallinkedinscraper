import os
from smolagents import OpenAIServerModel, CodeAgent


def company_finder_tool(user_query):
    """Use this function to find companies from the internet.

    Args:
        user_query (str): The user's query to find companies.

    Returns:
        str: Array of companies
    """

    model = OpenAIServerModel(
        model_id="gpt-4.1-mini", # Optimizes performance and cost
        api_base="https://api.openai.com/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    with open("company_prompt.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    agent = CodeAgent(tools=[], model=model, add_base_tools=True)

    return agent.run(f'{instructions}\n\n{user_query}')

def contact_finder_tool(company_list):
    """Use this function to find contacts from the internet.

    Args:
        company_list (array): The list of companies from which to find contacts.

    Returns:
        str: Array of contacts as JSON objects.
    """

    model = OpenAIServerModel(
        model_id="gpt-4.1-mini", # Optimizes performance and cost
        api_base="https://api.openai.com/v1",
        api_key=os.environ["OPENAI_API_KEY"],
    )

    with open("contact_prompt.txt", "r", encoding="utf-8") as f:
        instructions = f.read()

    agent = CodeAgent(tools=[], model=model, add_base_tools=True)

    return agent.run(f'{instructions}\n\n{company_list}')
