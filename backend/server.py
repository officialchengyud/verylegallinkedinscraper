from flask import Flask
from flask_socketio import SocketIO, emit

server = Flask(__name__)
socketio = SocketIO(server)

@socketio.on("signin")
def sign_in(data):
    pass

@socketio.on("signup")
def sign_up(data):
    pass

@socketio.on("update_context")
def update_context(data):
    pass

@socketio.on("submit_feedback")
def submit_feedback(data):
    pass


if __name__ == '__main__':
    server.run(debug=True)