from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import os
import asyncio

# Read GOOGLE_API_KEY into env
load_dotenv()

# Initialize the model (consider initializing once in the main agent)
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=os.getenv('GEMINI_API_KEY'))

async def scrape_linkedin(query: str) -> str:
    """
    Uses browser_use.Agent to scrape LinkedIn based on the provided query.
    Returns the result as a string.
    """
    print(f"Starting LinkedIn scrape for query: {query}")
    # The task needs to be specific enough for the browser_use agent
    task = f"Find information on LinkedIn related to: {query}. Extract relevant details like names, roles, companies, and profile links if possible."
    agent = Agent(
        task=task,
        llm=llm
    )
    result = await agent.run()
    print(f"LinkedIn scrape completed. Result: {result}")
    return str(result) # Ensure result is string

# Example usage (optional, for testing)
async def main():
    result = await scrape_linkedin("sales managers in asian food tech in nyc")
    print("--- Scrape Result ---")
    print(result)
    print("---------------------")

if __name__ == "__main__":
    # Note: Running asyncio like this might cause issues if run from an already running event loop
    # Consider using asyncio.get_event_loop().run_until_complete(main()) if needed
    asyncio.run(main())


'''
Connect all the workflows through agno

User: I want to find out contacts for sales managers in asian food tech in nyc 

under the hood: go and find the lists of asian food tech and return this 

model: 'list of asian food tech companies in nyc - do you want me to find the contacts? - use tools to find companies, crunchbase, google search'

user: yes, please

under the hood: uses our tools to find contact information thru linkedin/apollo

model: 'here are the contacts for sales managers in asian food tech in nyc - would you like me to reach out?'

user: yes, please

under the hood: draft an email using context

model: 'email drafted - would you like me to send it?'

user: yes, please

under the hood: access the user email through api (set up at sign in) and then send email

model: 'email sent'

'''