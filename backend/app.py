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
        # Initialize OpenAI model through Agno
        agent_llm = OpenAIChat(id='gpt-4o', api_key=os.getenv('OPENAI_API_KEY'))
        
        
        # Initialize agent state
        self.previous_step = WorkflowStep.CONTEXT.value
        self.user_data = {**basic_info, "context": ""}
        self.companies = []
        self.contacts = []

        # More variables to track email being drafted
        self.current_email = {}
        self.num_approved_emails = 0

        # Tools
        self.contact_finder_tool = contact_finder_tool
        
        # Define instructions as multi-line strings
        overview_instructions = """
    OVERVIEW:
    You are an autonomous sales outreach assistant that helps find and contact potential leads.
    You can perform 2 types of tasks:
    1. Execute workflow steps as described in the workflow.
    2. Respond conversationally to the user's queries.

    You have access to 1 tool:
    1. contact_finder_tool: Searches the internet for companies and contacts based on user input

    Whenever you receive a user input, you will determine if the user input is requesting a workflow step to be executed, or if it is a conversational query.
    If the user input is a conversational query, generate a clear and concise answer, using information about the user state passed to you.
    If the user input pertains to a specific step, you will first decide which step of the workflow needs to be executed, and execute only that step.
    When executing a step, use the user input to generate the output data.
    """

        workflow_overview_instructions = """
    WORKFLOW OVERVIEW:
    The workflow consists of four sequential steps. You can only move on to the next step when the user approves your output for the previous step.
    You will only execute one step at a time.
    You can execute the same step more than once (if you deem that the user is not satisfied with your previous output)
    You should not execute earlier steps than the most recently executed one. That is, you cannot go backwards in the workflow.
    The four steps are: CONTEXT_GENERATION, COMPANY_SEARCH, CONTACT_SEARCH, or EMAIL_GENERATION. More details about each step will be provided below.
    """

        input_format_instructions = """
    INPUT FORMAT:
    You will receive a JSON object with:
    1. previous_step: The previous step executed
    2. state: The current state containing:
       - user_data: A dictionary containing user data from Step 1
       - companies: List of companies generated from Step 2
       - contacts: List of contacts generated from Step 3
       - current_email: The current email being drafted in Step 4
       - num_approved_emails: The number of contacts from the contacts list that the user has approved an email for in Step 4
    3. user_input: A string containing the user's most recent input
    """

        workflow_steps_instructions = """
    WORKFLOW STEPS:

    Step 1: Generate Context (CONTEXT_GENERATION)
    - Use the user_data in state
    - Look at the user_input field potentially contains additional context given by the user
    - Using user_input and user_data, generate a updated user_data object
    - Step-Specific Output Format: A JSON object with the following fields:
      - first_name: The first name of the user
      - last_name: The last name of the user
      - company: The company the user works in
      - role: The role of the user at the company
      - industry: The industry the user's company belongs to
      - city: The city the user is based in
      - country: The country the user is based in
      - context: Any additional information about the user that is useful for lead generation and sales outreach
    - Update the state object with the updated user data (state['user_data'])
    - On user approval, go to the next step

    Step 2: Generate List of Companies (COMPANY_SEARCH)
    - Use the user_data and companies list (if any) in state
    - Look at the user_input field which potentially contains the user's feedback regarding the current list of companies
    - Use contact_finder_tool to gather information on relevant companies
    - Using the structured data and state['companies'], return an updated list of companies to contact
    - Step-Specific Output Format: A JSON object with the following fields:
      - companies: A list of companies, each with the following fields:
        - name: The name of the company
        - reason: The reason why the company could be a potential lead
    - Update the state object with the updated companies list (state['companies'])
    - On user approval, go to the next step

    Step 3: Generate Contacts from Companies (CONTACT_SEARCH)
    - Use the user_data, the companies list, the contacts list (if any) in state
    - Look at the user_input field which potentially contains the user's feedback regarding the current list of contacts
    - Use contact_finder_tool to find contacts from the current list of companies
    - Using the structured data, and state['contacts'], return a list of contacts to reach out to
    - Step-Specific Output Format: A JSON object with ONLY the following fields:
      - contacts: A list of contacts, each with the following fields:
        - name: The name of the contact
        - email: The email of the contact
        - company: The company the contact works at
        - reason: The reason why the contact could be a potential lead
        - linkedin: The contact's LinkedIn profile URL
    - The state object should be updated with the updated contacts list (state['contacts']) separately
    - On user approval, go to the next step

    Step 4: Generate Emails (EMAIL_GENERATION)
    - This step aims to draft an email for only one contact at a time
    - Use the user_data, contacts, current_email and num_approved_emails fields in state.
    - The contacts and num_approved_emails is used for seeing which is the current contact
    - Look at the user_input field which potentially contains the user's feedback regarding the current email draft
    - Return an updated email to reach out to the specified contact
    - Step-Specific Output Format: A JSON object with the following fields:
      - name: The name of the contact
      - email: The email address of the contact
      - company: The company the contact works at
      - subject: The subject of the email
      - body: The body of the email
    - Update the state object with the latest email draft (state['current_email']) as well as the number of approved emails (state['num_approved_emails'])
    - On user approval, check if the number of approved emails is still less than the number of contacts. If yes, then move on to the next contact
    - If there are no more contacts, end the workflow and return an empty value for step executed
    """

        output_format_instructions = """
    OUTPUT FORMAT:
    Your *entire* response MUST be a single, valid JSON object string. This JSON object should contain the following fields:
    1. text: The agent's conversational response to the user. Make sure to provide details of the step you executed, if any.
    2. step: The step that was executed, if any (CONTEXT_GENERATION, COMPANY_SEARCH, CONTACT_SEARCH, or EMAIL_GENERATION). If no step was executed, this should be None.
    3. data: The output from the agent, if any. This should be a JSON object with the relevant data for the step executed
    4. state: The updated state object, such as user_data, companies, contacts, current_email, and num_approved_emails.
    """

        important_rules_instructions = """
    IMPORTANT RULES:
    1. Always decide which step to execute (if any) by inferring from the user's input.
    2. Never skip steps or execute multiple steps at once.
    3. Only use the provided state data from the current and previous steps.
    4. Follow the exact output format specified above. Ensure that the state variables are updated and returned correctly within the JSON structure.
    5. Your entire output *must* be a single JSON object string. Do not include ```json, ```, newlines outside the JSON string, or any other text before or after the JSON object. The `use_json_mode` is enabled, so adhere strictly to returning only the JSON structure.
    """

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
            overview_instructions,
            workflow_overview_instructions,
            input_format_instructions,
            workflow_steps_instructions,
            output_format_instructions,
            important_rules_instructions,
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
        # Prepare input data for the agent
        input_data = {
            "previous_step": self.previous_step,
            "state": {
                "user_data": self.user_data,
                "companies": self.companies,
                "contacts": self.contacts,
                "current_email": self.current_email,
                "num_approved_emails": self.num_approved_emails,
            },
            "user_input": user_input.get("text", ""),
        }
        
        # Run the agent with the input
        run_response = self.agent.run(json.dumps(input_data)).content
        print("Agent response:", run_response) # BOOKMARK
        result = json.loads(run_response)
        
        # Update state
        new_state = result.pop("state")
        self.previous_step = result.get("step", self.previous_step)
        self.user_data = new_state["user_data"]
        self.companies = new_state["companies"]
        self.contacts = new_state["contacts"]
        self.current_email = new_state["current_email"]
        self.num_approved_emails = new_state["num_approved_emails"]

        return result

# WebSocket event handlers
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