from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_socketio import SocketIO, emit

server = Flask(__name__)
socketio = SocketIO(server)

@socketio.on("signin")
def sign_in(data):
    # 1. Validate credentials with user DB
    # 2. If valid, initialise user session
    # 3. Send success or error response
    # 4. Ask user for context updates
    pass

@socketio.on("signup")
def sign_up(data):
    # 1. Validate credentials with user DB (e.g., check if username already exists)
    # 2. If valid, create a new user and initialise user session
    # 3. Send success or error response
    # 4. Ask user for initial context
    pass

@socketio.on("update_context")
def update_context(data):
    # 1. Generate new user context based on provided text and current context (if any)
    # 2. Update user context in the database
    pass

@socketio.on("submit_feedback")
def submit_feedback(data):
    pass


if __name__ == '__main__':
    server.run(debug=True)