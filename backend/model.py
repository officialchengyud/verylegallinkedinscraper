from enum import Enum
from typing import List, Dict, Any, Optional

class UserStep(Enum):
    CONTEXT = "gathering user context"
    COMPANIES = "generating companies to contact"
    CONTACTS = "generating contacts to reach out to"
    EMAILS = "generating emails to send to contacts"
    DONE = "workflow finished" # Added a final state

class User:
    # Store data as simple dict for easy Firestore serialization
    def __init__(self, uid: str):
        self.uid: str = uid
        self.step: str = UserStep.CONTEXT.name # Store enum name as string
        self.profile: Dict[str, Any] = { # Store context here
            "target_industry": None,
            "target_roles": [],
            "location": None,
            "email_purpose": None,
            "other_notes": None,
        }
        self.company_feedback: Optional[str] = None
        self.found_companies: List[Dict[str, Any]] = []
        self.contact_feedback: Optional[str] = None
        self.found_contacts: List[Dict[str, Any]] = []
        self.current_email_contact_index: int = 0
        self.drafted_emails: Dict[int, Dict[str, str]] = {} # { contact_index: { subject: ..., body: ... } }
        self.email_feedback: Optional[str] = None

    # Helper to convert to dict for Firestore
    def to_dict(self) -> dict:
        return self.__dict__

    # Helper to load from dict from Firestore
    @staticmethod
    def from_dict(uid: str, data: dict) -> 'User':
        user = User(uid)
        user.step = data.get("step", UserStep.CONTEXT.name)
        user.profile = data.get("profile", {
            "target_industry": None, "target_roles": [], "location": None,
            "email_purpose": None, "other_notes": None
        })
        user.company_feedback = data.get("company_feedback")
        user.found_companies = data.get("found_companies", [])
        user.contact_feedback = data.get("contact_feedback")
        user.found_contacts = data.get("found_contacts", [])
        user.current_email_contact_index = data.get("current_email_contact_index", 0)
        # Ensure keys are integers after loading from JSON/Firestore if needed
        drafted_emails_raw = data.get("drafted_emails", {})
        user.drafted_emails = {int(k): v for k, v in drafted_emails_raw.items()}
        user.email_feedback = data.get("email_feedback")
        return user