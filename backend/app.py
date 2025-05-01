import os
import json
from enum import Enum
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
# from flask_cors import CORS
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from smolagents_implementation import contact_finder_tool

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*")

class WorkflowStep(Enum):
    START = "START"
    CONTEXT = "CONTEXT_GENERATION"
    COMPANIES = "COMPANY_SEARCH"
    CONTACTS = "CONTACT_SEARCH"
    EMAILS = "EMAIL_GENERATION"
    DONE = "DONE"

class MainAgent:
    def __init__(self, basic_info):
        # Initialize Gemini model through Agno
        # agent_llm = Gemini(id='gemini-2.0-flash-exp', api_key=os.getenv('GEMINI_API_KEY'))
        agent_llm = OpenAIChat(id='gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))
        
        
        # Initialize agent state
        self.current_step = WorkflowStep.CONTEXT
        self.user_data = {**basic_info, "context": ""}
        self.companies = []
        self.contacts = []

        # More variables to track email being drafted
        self.current_contact_index = None
        self.current_contact = {}
        self.current_email = {}
        self.processed_emails = []

        # Tools
        self.contact_finder_tool = contact_finder_tool
        
        self.agent = Agent(
            model=agent_llm,
            use_json_mode=True,
            tools=[
                self.contact_finder_tool,
                # self.linkedin_scraper_tool,
                # self.organize_information_tool,
                # self.send_email_tool,
            ],
            instructions=[
                # "You are a dummy agent. You have the full functionality of the agent I will describe below. However, the tools mentioned are not implemented yet.",
                # "At every step, make up dummy data but ensure the output format is as specified in the description below."

                "You are an autonomous sales outreach assistant that helps find and contact potential leads.",
                "You have access to one tool:",
                # "1. linkedin_scraper_tool: Searches LinkedIn for companies and people",
                # "2. organize_information_tool: Processes and structures the scraped data",
                # "3. send_email_tool: Sends personalized outreach emails",
                "1. contact_finder_tool: Searches the internet for companies and contacts based on user input",
                
                "WORKFLOW OVERVIEW:",
                "The overall workflow consists of four sequential steps. Each step must wait for user feedback before proceeding.",
                "You will only execute one step at a time.",
                
                "INPUT FORMAT:",
                "You will receive a JSON object with:",
                "1. current_step: The step to execute (CONTEXT_GENERATION, COMPANY_SEARCH, CONTACT_SEARCH, or EMAIL_GENERATION)",
                "2. state: The current state containing:",
                "   - user_data: A dictionary containing user data from Step 1"
                "   - companies: List of companies generated from Step 2",
                "   - contacts: List of contacts generated from Step 3",
                "   - current_contact: The contact of the current email being drafted in Step 4",
                "   - current_email: The current email being drafted in Step 4",
                "3. user_input: A string containing the user's most recent input",

                "INITIAL ACTION:",
                "Use the current_step value to determine which of the steps below to execute. Execute the step, using the relevant data."

                "STEPS:",
                
                "Step 1: Generate Context (CONTEXT_GENERATION)",
                "- Use the user_data in state",
                "- The user_input field contains additional context given by the user",
                "- Using user_input and user_data, generate a updated user_data object",
                "- Step-Specific Output Format: A JSON object with the following fields:",
                "  - first_name: The first name of the user",
                "  - last_name: The last name of the user",
                "  - company: The company the user works in",
                "  - role: The role of the user at the company",
                "  - industry: The industry the user's company belongs to",
                "  - city: The city the user is based in",
                "  - country: The country the user is based in",
                "  - context: Any additional information about the user that is useful for lead generation and sales outreach",
                
                "Step 2: Generate List of Companies (COMPANY_SEARCH)",
                "- Use the user_data and companies list (if any) in state"
                "- The user_input field, if present, contains the user's feedback regarding the current list of companies"
                "- Use contact_finder_tool to gather information on relevant companies",
                "- Using the structured data, return a list of companies to contact"
                "- Step-Specific Output Format: A JSON object with the following fields:",
                "  - companies: A list of companies, each with the following fields:",
                "    - name: The name of the company",
                "    - reason: The reason why the company could be a potential lead",
                
                "Step 3: Generate Contacts from Companies (CONTACT_SEARCH)",
                "- Use the user_data, the companies list, the contacts list (if any) in state",
                "- The user_input field, if present, contains the user's feedback regarding the current list of contacts",
                "- Use contact_finder_tool to find contacts from the list of companies",
                "- Using the structured data, return a list of companies to contact"
                "- Step-Specific Output Format: A JSON object with the following fields:",
                "  - contacts: A list of contacts, each with the following fields:",
                "    - name: The name of the contact",
                "    - email: The email of the contact",
                "    - company: The company the contact works at",
                "    - reason: The reason why the contact could be a potential lead",
                "    - linkedin: The contact's LinkedIn profile URL",
                
                "Step 4: Generate Emails (EMAIL_GENERATION)",
                "- Use the user_data, current_contact and current_email objects in state",
                "- The user_input field, if present, contains the user's feedback regarding the current email draft",
                "- Return an updated email to reach out to the specified contact",
                "- Step-Specific Output Format: A JSON object with the following fields:",
                "  - name: The name of the contact",
                "  - email: The email of the contact",
                "  - company: The company the contact works at",
                "  - subject: The subject of the email",
                "  - body: The body of the email",
                
                "OUTPUT FORMAT:",
                "After each step, return a JSON object with:",
                "1. step: The step that was executed (CONTEXT_GENERATION, COMPANY_SEARCH, CONTACT_SEARCH, or EMAIL_GENERATION)",
                "2. data: The step-specific output",
                
                "IMPORTANT RULES:",
                "1. Always check current_step to know which step to execute",
                "2. Never skip steps or execute multiple steps at once",
                "3. Only use the provided state data from the current and previous steps",
                "4. Follow the exact output format for each step",
                "5. Make sure your output is valid JSON. It should not have ``` or newline or any other formatting.",
            ]
        )
    
    def linkedin_scraper_tool(self, query):
        """Tool for searching LinkedIn"""
        # Implementation of LinkedIn scraping
        return {"status": "success", "data": "Scraped data"}
    
    def organize_information_tool(self, data):
        """Tool for organizing scraped data"""
        # Implementation of data organization
        return {"status": "success", "data": "Organized data"}
    
    def send_email_tool(self, contact_data):
        """Tool for sending emails"""
        # Implementation of email sending
        return {"status": "success", "data": "Email sent"}
    
    def handle_input(self, user_input):
        """Handle all user input for the workflow"""
        # Update step
        if self.current_step == WorkflowStep.START:
            self.current_step = WorkflowStep.CONTEXT
        elif self.current_step == WorkflowStep.CONTEXT:
            self.current_step = WorkflowStep.COMPANIES
        elif user_input.get("approved", True):
            if self.current_step == WorkflowStep.COMPANIES:
                self.current_step = WorkflowStep.CONTACTS
            elif self.current_step == WorkflowStep.CONTACTS:
                self.current_step = WorkflowStep.EMAILS
                self.current_contact_index = 0
            elif self.current_step == WorkflowStep.EMAILS:
                # Add to list of approved emails
                self.processed_emails.append(self.current_email)
                # Go to next contact, end if no more contacts
                self.current_contact_index += 1
                if self.current_contact_index >= len(self.contacts):
                    self.current_step = WorkflowStep.DONE

            # Refresh current contact and email draft
            if self.current_step == WorkflowStep.EMAILS:
                self.current_contact = self.contacts[self.current_contact_index]
                self.current_email = {
                    "name": "",
                    "email": "",
                    "company": "",
                    "subject": "",
                    "body": "",
                }

        if self.current_step == WorkflowStep.DONE:
            return {}
        
        # Prepare input data for the agent
        input_data = {
            "current_step": self.current_step.value,
            "state": {
                "user_data": self.user_data,
                "companies": self.companies,
                "contacts": self.contacts,
                "current_contact": self.current_contact,
                "current_email": self.current_email,
            },
            "user_input": user_input.get("text", ""),
        }
        
        # Run the agent with the input
        run_response = self.agent.run(json.dumps(input_data)).content
        print("Agent response:", run_response)
        result = json.loads(run_response)
        
        step_executed = result.get("step", {})
        if step_executed != self.current_step.value:
            print(f"Wrong step executed: expected {self.current_step.value}, executed {step_executed}")
        else:
            # Update state
            if self.current_step == WorkflowStep.CONTEXT:
                self.user_data = result["data"]
            if self.current_step == WorkflowStep.COMPANIES:
                self.companies = result["data"]["companies"]
            elif self.current_step == WorkflowStep.CONTACTS:
                self.contacts = result["data"]["contacts"]
            elif self.current_step == WorkflowStep.EMAILS:
                self.current_email = result["data"]

        return result

# WebSocket event handlers
# @socketio.on('connect')
# def handle_connect():
#     """Handle client connection"""
#     print('Client connected')
#     emit('connected', {'status': 'connected'})

# @socketio.on('disconnect')
# def handle_disconnect():
#     """Handle client disconnection"""
#     print('Client disconnected')


@socketio.on('initialize_agent')
def initialize_agent(data: dict):
    """
    Initialize the agent with basic user information.
    
    Expects a dictionary with the 'basic_info' key
    """
    try:
        basic_info = data.get('basic_info', {})
        global agent
        agent = MainAgent(basic_info)
        
        # Emit success message
        emit('agent_initialized', {'status': 'success'})
    except Exception as e:
        emit('error', {'message': str(e)})

@socketio.on('user_input')
def handle_user_input(data: dict):
    """
    Provide user input to the agent

    Expects a dictionary with the 'approved' (optional) and 'text' keys
    """
    try:
        result = agent.handle_input(data)
        emit('agent_output', result)
    except Exception as e:
        emit('error', {'message': str(e)})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000) 