import os
import json
from enum import Enum
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
# from flask_cors import CORS
from agno.agent import Agent
from agno.models.google import Gemini
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
        agent_llm = OpenAIChat(id='o4-mini', api_key=os.getenv('OPENAI_API_KEY'))
        
        
        # Initialize agent state
        self.previous_step = WorkflowStep.CONTEXT.value
        self.user_data = {**basic_info, "context": ""}
        self.companies = []
        self.contacts = []

        # More variables to track email being drafted
        self.current_email = {}
        self.num_processed_emails = 0

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
    When executing a step, use the user input to generate the output data and incorporate it naturally into your conversational response in the 'text' field.
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
       - current_email: The most recently drafted email in Step 4. If this value is updated, this MUST contain the subject and content fields
       - num_processed_emails: The index of the contact in the 'contacts' list for whom an email draft has just been generated (or is about to be generated). This effectively counts how many contacts have had an email drafted for them so far. Starts at 0.
    3. user_input: A string containing the user's most recent input (e.g., approval, rejection, modification request for the current email, or a request to proceed).
    """

        workflow_steps_instructions = """
    WORKFLOW STEPS:

    Step 1: Generate Context (CONTEXT_GENERATION)
    - Use the user_data in state
    - Look at the user_input field potentially contains additional context given by the user
    - Using user_input and user_data, generate a updated user_data object
    - Step-Specific Output Format (to be included in the 'text' field): Describe the updated user profile information clearly. For example: "Okay, I've updated your profile. Here's the current information: First Name: [first_name], Last Name: [last_name], Company: [company], Role: [role], Industry: [industry], City: [city], Country: [country], Context: [context]. Let me know if this looks correct."
    - Update the state object with the updated user data (state['user_data'])
    - On user approval, go to the next step

    Step 2: Generate List of Companies (COMPANY_SEARCH)
    - Use the user_data and companies list (if any) in state
    - Look at the user_input field which potentially contains the user's feedback regarding the current list of companies
    - Use contact_finder_tool to gather information on relevant companies
    - Using the structured data and state['companies'], generate an updated list of companies to contact
    - Step-Specific Output Format (to be included in the 'text' field): Present the list of companies clearly, including their names and the reason for suggesting them. For example: "Based on your profile and request, I found these companies:\n- [Company Name 1]: [Reason 1]\n- [Company Name 2]: [Reason 2]\nLet me know if you'd like to proceed with these or refine the search."
    - Update the state object with the updated companies list (state['companies'])
    - On user approval, go to the next step

    Step 3: Generate Contacts from Companies (CONTACT_SEARCH)
    - Use the user_data, the companies list, the contacts list (if any) in state
    - Look at the user_input field which potentially contains the user's feedback regarding the current list of contacts
    - Use contact_finder_tool to find contacts from the current list of companies
    - Using the structured data, and state['contacts'], generate a list of contacts to reach out to
    - Step-Specific Output Format (to be included in the 'text' field): Present the list of contacts clearly, including name, email, company, reason, and LinkedIn URL. For example: "I found the following contacts at the selected companies:\n- Name: [Name 1], Email: [Email 1], Company: [Company 1], Reason: [Reason 1], LinkedIn: [URL 1]\n- Name: [Name 2], Email: [Email 2], Company: [Company 2], Reason: [Reason 2], LinkedIn: [URL 2]\nShould I start drafting emails for them?"
    - The state object should be updated with the updated contacts list (state['contacts']) separately. Ensure that each contact in this list has an email field.
    - On user approval, go to the next step

    Step 4: Generate Emails (EMAIL_GENERATION)
    - This step aims to draft an email for only one contact at a time, sequentially from the 'contacts' list.
    - Use the 'user_data', 'contacts', 'current_email', and 'num_processed_emails' fields in state.
    - Determine the current contact to process using the 'num_processed_emails' as the index for the 'contacts' list (i.e., `contact_to_process = contacts[num_processed_emails]`).
    - Check if `num_processed_emails` is less than the total number of contacts. If not, the email generation phase is complete; inform the user and set 'step' to None in the output.
    - If within bounds, use the 'user_input' (which might contain feedback on the *previous* draft or a request to proceed) and the details of `contact_to_process` to generate or refine an email draft.
    - Step-Specific Output Format (to be included in the 'text' field): Present the drafted email clearly for the current contact (`contact_to_process`), including recipient details, subject, and body. For example: "Here's draft #{index + 1} for {contact_name} at {company_name} ({contact_email}):\nSubject: {subject}\n\nBody:\n{body}\n\nPlease review it. Let me know if you approve, want changes, or want to skip this contact."
    - **Crucially**: After generating the draft for the current contact, update the state for the response:
        - Set `state['current_email']` to the newly generated draft.
        - Increment `state['num_processed_emails']` by 1. This signifies that this contact has now been processed (i.e., an email has been drafted and shown).
    - The workflow proceeds based on the *next* user input. When the user responds (approve/reject/modify/next), you will again check the (already incremented) `num_processed_emails` against the total number of contacts to decide whether to draft for the *next* contact or end the process.
    - DO NOT REPEAT ANY CONTACTS. The sequential processing using `num_processed_emails` ensures this.
    """

        output_format_instructions = """
    OUTPUT FORMAT:
    Your *entire* response MUST be a single, valid JSON object string. This JSON object should contain the following fields:
    1. text: The agent's conversational response to the user. If a step was executed, this field MUST include a clear, human-readable presentation of the results or data generated for that step (as described in the Step-Specific Output Format for each step).
    2. step: The step that was executed, if any (CONTEXT_GENERATION, COMPANY_SEARCH, CONTACT_SEARCH, or EMAIL_GENERATION). If no step was executed (e.g., email process finished), this should be None.
    3. state: The updated state object, including user_data, companies, contacts, current_email, and the potentially incremented num_processed_emails.
    """

        important_rules_instructions = """
    IMPORTANT RULES:
    1. Always decide which step to execute (if any) by inferring from the user's input.
    2. Never skip steps or execute multiple steps at once.
    3. Only use the provided state data from the current and previous steps.
    4. Follow the exact output format specified above (text, step, state). Ensure the 'text' field contains both the conversational part and a description of any generated data if a step was run. Ensure that the state variables are updated and returned correctly within the JSON structure.
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
                "num_processed_emails": self.num_processed_emails, # Pass the current count
            },
            "user_input": user_input.get("text", ""),
        }
        
        # Run the agent with the input
        run_response = self.agent.run(json.dumps(input_data)).content
        print("Raw Agent response:", run_response) # BOOKMARK

        # Clean the response string: remove potential markdown fences
        cleaned_response = run_response.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[len("```json"):].strip()
        if cleaned_response.startswith("```"):
             cleaned_response = cleaned_response[len("```"):].strip()
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-len("```")].strip()

        print("Cleaned Agent response:", cleaned_response)
        
        # Attempt to parse the cleaned JSON response
        try:
            # Use the cleaned response string for parsing
            result = json.loads(cleaned_response) 
        except json.JSONDecodeError as e:
             print(f"JSONDecodeError: {e}")
             print("Could not parse the agent response string.")
             # Return error with the original raw response for debugging
             return {"error": "Failed to parse agent response", "raw_response": run_response}

        # Update state (ensure 'state' key exists)
        if "state" in result:
            new_state = result.pop("state")
            self.previous_step = result.get("step", self.previous_step)
            # Safely get values from new_state
            self.user_data = new_state.get("user_data", self.user_data)
            self.companies = new_state.get("companies", self.companies)
            self.contacts = new_state.get("contacts", self.contacts)
            self.current_email = new_state.get("current_email", self.current_email)
            # Update num_processed_emails from the agent's returned state
            self.num_processed_emails = new_state.get("num_processed_emails", self.num_processed_emails) 
        else:
            print("Warning: 'state' key not found in the parsed agent result.")

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

    Expects a dictionary with the 'text' key
    """
    try:
        # Check if the user input contains "/sendemail"
        user_text = data.get("text", "")
        if "/sendemail" in user_text:
            print("Detected '/sendemail' command in user input.")
            emit('send_email', {
                "email": agent.contacts[agent.num_processed_emails]["email"],
                "subject": agent.current_email["subject"],
                "content": agent.current_email["content"],
            })
        result = agent.handle_input(data)
        # Check if the result indicates an error from handle_input
        if isinstance(result, dict) and "error" in result:
             emit('error', {'message': result["error"], 'details': result.get("raw_response")})
        else:
            emit('agent_output', result["text"]) # Emits JSON with 'text', 'step'
    except Exception as e:
        # Catch any other unexpected errors during handling or emission
        print(f"Error in handle_user_input: {e}")
        emit('error', {'message': f"An unexpected error occurred: {str(e)}"})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=5000)