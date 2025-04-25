from flask import Flask, request
import requests

server = Flask(__name__)

@server.route('/')
def home():
    return "Hello, Flask!"

@server.route('/user_context', methods=['POST'])
def parse_user_context():
    """
    An endpoint to receive user context data.
    
    Expects a JSON body with a key 'user_context' containing the user input.
    """
    data = request.json
    res = None # Generate response
    return res

if __name__ == '__main__':
    server.run(debug=True)