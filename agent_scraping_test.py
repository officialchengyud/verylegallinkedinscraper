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
        task="Can you find out where Edric Khiew studied from his linkedin profile?",
        llm=llm
    )
    await agent.run()

if __name__ == "__main__":
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

