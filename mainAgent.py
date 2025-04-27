import asyncio
from agno.agent import Agent
from agno.models.google import Gemini
# Remove Toolkit import if SalesToolkit is removed
# from agno.tools.toolkit import Toolkit
from agno.tools.reasoning import ReasoningTools
import os
import json
from dotenv import load_dotenv
from linkedin_scraper import scrape_linkedin
from backend.model import User # Keep User model for context
from typing import List, Dict, Any

load_dotenv()

# --- Global list to store queries for testing ---
_test_queries_used = []

# --- Main Agent Definition ---

class MainAgent:
    def __init__(self):
        agent_llm = Gemini(id='gemini-2.0-flash-exp', api_key=os.getenv('GEMINI_API_KEY'))
        self.agent = Agent(
            model=agent_llm,
            # Pass the MainAgent instance itself as the tool provider
            tools=[
                self.linkedin_scraper_tool,
                self.organize_information_tool,
                self.generate_email_tool,
            ],
            instructions=[
                "You are an autonomous sales outreach assistant.",
                "Your goal is to find relevant contacts based on user criteria and draft personalized outreach emails using the tools available directly within this agent.",
                "Follow these steps:",
                "1. Use the linkedin_scraper_tool to find potential companies or people based on the user's request (industry, roles, location). You might need multiple searches.",
                "2. Use the organize_information_tool to process the raw scraped data and extract a structured list of contacts matching the user's target roles.",
                "3. For each contact found and organized, use the generate_email_tool to draft a personalized email based on the contact's details and the user's profile/purpose.",
                "4. Present the final drafted emails as your result. If multiple emails are generated, provide them as a list of JSON objects.",
                "Think step-by-step using the ReasoningTools to plan your actions.",
                "Ensure all necessary information (like user profile details) is passed correctly to the tools.",
            ],
            # debug_mode=True # Enable for detailed Agno logs
        )

    # --- Tool Definitions moved into MainAgent ---

    async def linkedin_scraper_tool(self, query: str) -> str:
        """
        Searches LinkedIn for profiles or companies based on the provided query.
        Returns the raw scraping results as a string.
        """
        print(f"--- Calling LinkedIn Scraper Tool with query: {query} ---")
        global _test_queries_used
        _test_queries_used.append(query) # Store query for test output
        try:
            result = await scrape_linkedin(query)
            return str(result)[:4000] # Return result as string, potentially truncated
        except Exception as e:
            print(f"Error in linkedin_scraper_tool: {e}")
            return f"Error scraping LinkedIn: {e}"

    async def organize_information_tool(self, scraped_data: str, target_roles: List[str], target_industry: str, location: str) -> List[Dict[str, Any]]:
        """
        Organizes raw scraped data (text) into a structured list of potential contacts.
        Filters based on target roles, industry, and location.
        Input 'scraped_data' is the raw text output from the linkedin_scraper_tool.
        Returns a JSON list of dictionaries, each representing a contact with keys like 'name', 'role', 'company', 'profile_url', 'justification'.
        Example Output: [ { "name": "Jane Doe", "role": "CEO", "company": "HealthAI", "profile_url": "...", "justification": "Matches target role CEO in Healthcare AI." } ]
        """
        print("--- Calling Organize Information Tool ---")
        organizer_llm = Gemini(id='gemini-2.0-flash-exp', api_key=os.getenv('GEMINI_API_KEY'))
        prompt = f"""
        Parse the following raw scraped data and extract relevant contacts based on the criteria.

        Criteria:
        - Target Roles: {target_roles}
        - Target Industry: {target_industry}
        - Location: {location}

        Raw Scraped Data:
        ---
        {scraped_data}
        ---

        Output ONLY a JSON list of contacts matching the criteria. Each contact should be an object with 'name', 'role', 'company', 'profile_url' (if available), and 'justification' keys.
        If no relevant contacts are found, return an empty list [].
        Example Output: [{{ "name": "Jane Doe", "role": "CEO", "company": "HealthAI", "profile_url": "...", "justification": "Matches target role CEO in Healthcare AI." }}]
        """
        try:
            response = await organizer_llm.acall(prompt)
            organized_list = json.loads(response)
            if isinstance(organized_list, list):
                print(f"Organized Data: {organized_list}")
                return organized_list
            else:
                print("Organize tool did not return a list.")
                return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from organize_information_tool response: {response}")
            return []
        except Exception as e:
            print(f"Error in organize_information_tool: {e}")
            return []

    async def generate_email_tool(self, contact: Dict[str, Any], user_profile: Dict[str, Any]) -> Dict[str, str]:
        """
        Generates a personalized sales outreach email for a given contact.
        'contact' is a dictionary with contact details (name, role, company, etc.).
        'user_profile' contains information about the sender and the email's purpose (target_industry, email_purpose, etc.).
        Returns a JSON object with 'subject' and 'body' keys for the email draft.
        Example Output: {{ "subject": "Introducting Our New Product", "body": "Hi Jane Doe, ..." }}
        """
        print(f"--- Calling Generate Email Tool for: {contact.get('name')} ---")
        email_llm = Gemini(id='gemini-2.0-flash-exp', api_key=os.getenv('GEMINI_API_KEY'))
        prompt = f"""
        Draft a concise and compelling personalized sales email based on the following information.

        Sender/User Profile:
        {user_profile}

        Recipient Contact Details:
        {contact}

        Email Purpose: {user_profile.get('email_purpose', 'Introduce our services')}

        Instructions:
        - Personalize the email using the recipient's name, role, and company.
        - Keep the email concise and focused on the purpose.
        - Output ONLY a JSON object with 'subject' and 'body' keys.
        Example Output: {{ "subject": "Regarding [Relevant Topic]", "body": "Hi {{contact['name']}},\n\nI saw your work at {{contact['company']}}..." }}
        """
        try:
            response = await email_llm.acall(prompt)
            email_draft = json.loads(response)
            if isinstance(email_draft, dict) and 'subject' in email_draft and 'body' in email_draft:
                print(f"Generated Email Draft: {email_draft}")
                return email_draft
            else:
                print("Generate email tool did not return expected format.")
                return {"subject": "Error", "body": "Failed to generate email draft."}
        except json.JSONDecodeError:
            print(f"Error decoding JSON from generate_email_tool response: {response}")
            return {"subject": "Error", "body": f"Failed to parse email draft response: {response}"}
        except Exception as e:
            print(f"Error in generate_email_tool: {e}")
            return {"subject": "Error", "body": f"Error generating email: {e}"}

    # --- Workflow Execution ---

    async def run_workflow(self, user_data: User) -> Any:
        """
        Runs the autonomous sales outreach workflow based on user data.
        """
        print(f"--- Starting Autonomous Workflow ---")
        # Convert User object to dict for the prompt, focusing on profile data
        user_profile_dict = user_data.profile if user_data.profile else {}
        # Add other relevant top-level fields if needed by tools/prompt
        user_profile_dict['uid'] = user_data.uid # Example if UID is needed

        initial_prompt = f"""
        Start the sales outreach workflow for the following user profile:
        - Target Industry: {user_profile_dict.get('target_industry', 'Not specified')}
        - Target Roles: {user_profile_dict.get('target_roles', [])}
        - Location: {user_profile_dict.get('location', 'Not specified')}
        - Email Purpose: {user_profile_dict.get('email_purpose', 'Not specified')}
        - User Profile Dict (for email tool): {user_profile_dict}

        Find relevant contacts matching these criteria and draft personalized outreach emails for them.
        """

        try:
            final_result = await self.agent.arun(initial_prompt)
            print(f"--- Workflow Completed ---")
            print(f"Final Result: {final_result}")
            return final_result
        except Exception as e:
            print(f"Error during autonomous workflow: {e}")
            # Consider logging the traceback for detailed debugging
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

# --- Test Function (Updated to use User.profile) ---

async def test_agent():
    global _test_queries_used
    _test_queries_used = []

    agent_instance = MainAgent()
    user = User(uid="test_user_healthcare_ai") # Changed UID for clarity
    # Store criteria in the user.profile dictionary
    # --- UPDATED TEST CRITERIA --- 
    user.profile["target_industry"] = "Healthcare"
    user.profile["target_roles"] = ["CEO", "CTO", "Head of Innovation", "Chief Medical Officer"]
    user.profile["location"] = "USA" # Broadened location
    user.profile["email_purpose"] = "Introduce our new AI platform designed to improve diagnostic accuracy and efficiency in healthcare settings. Seeking to schedule a brief demo."
    # --- END OF UPDATED CRITERIA ---

    output_file = "testresult_agno_autonomous_healthcare.md" # Changed output file name

    with open(output_file, "w") as f:
        f.write("# Agno Autonomous Agent Test Results (Healthcare AI Email)\n\n") # Updated title
        f.write("## Initial User Request\n")
        f.write(f"- **Target Industry:** {user.profile.get('target_industry')}\n")
        f.write(f"- **Target Roles:** {user.profile.get('target_roles')}\n")
        f.write(f"- **Location:** {user.profile.get('location')}\n")
        f.write(f"- **Email Purpose:** {user.profile.get('email_purpose')}\n\n")

        f.write("## Agent Execution Log\n")
        f.write("Running autonomous workflow...\n\n")

        final_output = await agent_instance.run_workflow(user)

        f.write("### LinkedIn Scraper Queries Used:\n")
        if _test_queries_used:
            for i, query in enumerate(_test_queries_used):
                f.write(f"{i+1}. `{query}`\n")
        else:
            f.write("No queries recorded.\n")
        f.write("\n")

        f.write("## Final Output\n")
        f.write("```json\n")
        try:
            # Attempt to pretty-print if it's JSON-like
            parsed_output = json.loads(final_output) if isinstance(final_output, str) else final_output
            f.write(json.dumps(parsed_output, indent=2))
        except (json.JSONDecodeError, TypeError):
            f.write(str(final_output)) # Write raw output if not JSON
        f.write("\n```\n")

    print(f"Autonomous test results written to {output_file}")


if __name__ == "__main__":
    asyncio.run(test_agent())
