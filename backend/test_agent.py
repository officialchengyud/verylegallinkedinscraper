import os
import json
import unittest
from dotenv import load_dotenv
from app import MainAgent, WorkflowStep

# Load environment variables
load_dotenv()

class TestMainAgent(unittest.TestCase):
    def setUp(self):
        """Set up the test environment"""
        basic_info = {
            "first_name": "John",
            "last_name": "Doe",
            "company": "Acme Inc",
            "role": "Sales Manager",
            "industry": "Technology",
            "city": "San Francisco",
            "country": "USA",
        }
        self.agent = MainAgent(basic_info)
        
    def test_workflow_flow(self):
        """Test the complete workflow flow"""
        # Step 1: CONTEXT_GENERATION
        self.assertEqual(self.agent.current_step, WorkflowStep.CONTEXT)
        
        # Simulate user input for context generation
        context_input = {"text": "I want only companies run by males"}
        
        # Process context input
        print("\nFeeding context input:", context_input)
        result = self.agent.handle_input(context_input)

        # print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.COMPANIES)
        self.assertEqual(result["step"], WorkflowStep.COMPANIES.value)
                
        # Simulate user input for company search
        companies_input = {
            "approved": False,
            "text": "Focus on companies with 50-200 employees",
        }
        
        # Process companies input
        print("\nFeeding companies input (reject):", companies_input)
        result = self.agent.handle_input(companies_input)
        # print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.COMPANIES)
        self.assertEqual(result["step"], WorkflowStep.COMPANIES.value)
        
        # Simulate user input for company search
        companies_input = {"approved": True}
        
        # Approve companies and move to CONTACTS step
        print("\nFeeding companies input (approve):", companies_input)
        result = self.agent.handle_input(companies_input)
        # print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.CONTACTS)
        self.assertEqual(result["step"], WorkflowStep.CONTACTS.value)
        
        # Simulate user input for contact search
        contacts_input = {
            "approved": False,
            "text": "Focus on males and only identify 2 contacts",
        }
        
        # Process contacts input
        print("\nFeeding contacts input (reject):", contacts_input)
        result = self.agent.handle_input(contacts_input)
        print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.CONTACTS)
        self.assertEqual(result["step"], WorkflowStep.CONTACTS.value)
        
        # Simulate user input for contact search
        contacts_input = {"approved": True}

        # Approve contacts and move to EMAILS step
        print("\nFeeding contacts input (approve):", contacts_input)
        result = self.agent.handle_input(contacts_input)
        print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.EMAILS)
        self.assertEqual(result["step"], WorkflowStep.EMAILS.value)
        self.assertEqual(self.agent.current_contact_index, 0)
        
        # Simulate user input for email generation
        email_input = {
            "approved": False,
            "feedback": "Make the email shorter"
        }
        
        # Process email input
        print("\nFeeding email input (reject):", email_input)
        result = self.agent.handle_input(email_input)
        # print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.EMAILS)
        self.assertEqual(result["step"], WorkflowStep.EMAILS.value)
        self.assertEqual(self.agent.current_contact_index, 0)
        self.assertEqual(self.agent.current_contact, self.agent.contacts[0])

        # Simulate user input for email generation
        email_input = {"approved": True}

        # Approve email and move to next contact
        print("\nFeeding email input (approve):", email_input)
        result = self.agent.handle_input({"approved": True})
        # print("Output:", result)
        self.assertIsNotNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.EMAILS)
        self.assertEqual(result["step"], WorkflowStep.EMAILS.value)
        self.assertEqual(self.agent.current_contact_index, 1)
        self.assertEqual(self.agent.current_contact, self.agent.contacts[1])
        
        # Test email generation for the next contact
        print("\nFeeding email input (approve):", email_input)
        result = self.agent.handle_input(email_input)
        # print("Output:", result)
        self.assertIsNone(result)
        self.assertEqual(self.agent.current_step, WorkflowStep.DONE)
        self.assertEqual(self.agent.current_contact_index, 2)
        
        
        # Verify workflow is complete
        self.assertEqual(self.agent.current_step, WorkflowStep.DONE)


if __name__ == "__main__":
    unittest.main() 