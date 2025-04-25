from flask import Flask
from flask_socketio import SocketIO, emit

server = Flask(__name__)
socketio = SocketIO(server)

@server.route('/')
def home():
    return "Hello, Flask!"

@socketio.on('connect')
def emit_data():
    data = {'message': 'Hello, World!'}
    while True:
        emit('message', data)
        print("Emitting data")
        socketio.sleep(5)

if __name__ == '__main__':
    server.run(debug=True)