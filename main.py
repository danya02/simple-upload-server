from flask import Flask, request

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def main(path):
    return 'You have accessed path ' + path + ' with method ' + request.method

