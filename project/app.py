from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Project started from Flask on port 8080!'

    
@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'