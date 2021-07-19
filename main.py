from flask import Flask, request, g
import yaml

app = Flask(__name__)

@app.before_request
def before_request():
    with open('/config.yaml') as config:
        data = yaml.load(config)
        print(data)
        g.create_allowed = data['create_allowed']
        g.delete_allowed = data['delete_allowed']

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST'])
def main(path):
    return f'{g.create_allowed} {g.delete_allowed}'
