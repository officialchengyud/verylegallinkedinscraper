from flask import Flask

server = Flask(__name__)

@server.route('/')
def home():
    return "Hello, Flask!"

if __name__ == '__main__':
    server.run(debug=True)