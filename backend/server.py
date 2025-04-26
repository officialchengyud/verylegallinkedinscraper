from dotenv import load_dotenv
load_dotenv()

from database import FirestoreDatabase
from flask import Flask
from flask_socketio import SocketIO, emit
from model import User, UserStep

server = Flask(__name__)
socketio = SocketIO(server, cors_allowed_origins="*")

user_db = FirestoreDatabase()
user_steps: dict[str, UserStep] = {}
user_data: dict[str, User] = {}

@socketio.on("authenticate")
def initialise_user(data: dict):
    """
    Initialise user data.

    Expects a JSON object with the "uid" key.
    """
    uid = data.get("uid")
    if uid in user_steps:
        raise ValueError(f"User {uid} already exists.")
    increment_user_step(uid)

@socketio.on("update_context")
def update_context(data: dict):
    """
    Update user context.

    Expects a JSON object with the "uid" and "context" keys.
    Returns the updated user data.
    """
    uid = data.get("uid")
    new_context = data.get("context")
    user_data = user_db.get_user(uid)
    step_description = user_steps.get(uid).value
    if not (user_data and step_description and new_context):
        raise ValueError(f"Either user data, step description or new context not found for UID {uid}.")
    
    # ADD HERE: Feed existing user data, step description, and new context to the agent.
    # Agent should process these and generate updated user data.
    new_user_data = user_data.copy()

    user_db.update_document("users", uid, new_user_data)
    emit("context_updated", new_user_data)
    increment_user_step(uid)

@socketio.on("submit_feedback")
def submit_feedback(data: dict):
    """
    Updates user context with user feedback.

    Expects a JSON object with the "uid", "isApproved", and "feedback" keys.

    """
    uid = data.get("uid")
    is_approved = data.get("isApproved")
    feedback = data.get("feedback")
    user_data = user_db.get_user(uid)
    step_description = user_steps.get(uid).value
    if not (user_data and step_description and is_approved and feedback):
        raise ValueError(f"Either user data, step description or approval not found for UID {uid}.")
    if not is_approved and not feedback:
        raise ValueError(f"Feedback not found for UID {uid}.")
    
    if is_approved:
        

@socketio.on("cleaup")
def cleanup(data: dict):
    """
    Cleanup user data.

    Expects a JSON object with the "uid" key.
    """
    uid = data.get("uid")
    user_steps.pop(uid)

def increment_user_step(uid: str):
    """
    Increments the step of the user.
    """
    if uid not in user_steps:
        user_steps[uid] = UserStep.CONTEXT
    else:
        current_step = user_steps[uid]
        if current_step == UserStep.CONTEXT:
            user_steps[uid] = UserStep.COMPANIES
        elif current_step == UserStep.COMPANIES:
            user_steps[uid] = UserStep.CONTACTS
        elif current_step == UserStep.CONTACTS:
            user_steps[uid] = UserStep.EMAILS
        # TODO: Final step not handled yet


if __name__ == '__main__':
    socketio.run(server, debug=True)