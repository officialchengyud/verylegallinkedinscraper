from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
from dotenv import load_dotenv
import os
import asyncio

# Read GOOGLE_API_KEY into env
load_dotenv()

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp',api_key=os.getenv('GEMINI_API_KEY'))

# Create agent with the model
async def main():
    agent = Agent(
        task="Access twitter and search for people with the title 'Sales Manager' in the location 'New York', sign in with google using the email 'verylegaltest@gmail.com', and password '123terima!@#'",
        llm=llm
    )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())




