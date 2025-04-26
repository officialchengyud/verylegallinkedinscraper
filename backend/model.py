from enum import Enum

class UserStep(Enum):
    CONTEXT = "gathering user context"
    COMPANIES = "generating companies to contact"
    CONTACTS = "generating contacts to reach out to"
    EMAILS = "generating emails to send to contacts"

class User:
    def __init__(
        self,
        uid,
        step: UserStep,
        
    ):
        self.uid = uid
        self.step = step