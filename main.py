from flask import Flask, request, g, render_template, send_from_directory, redirect, flash, url_for
from werkzeug.utils import secure_filename
import yaml
import os
import traceback

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

@app.before_request
def before_request():
    with open('/config.yaml') as config:
        data = yaml.safe_load(config)
        g.create_allowed = data['create_allowed']
        g.delete_allowed = data['delete_allowed']

def handle_delete_request():
    path = request.form['path']
    path.strip('/')
    
    if not g.delete_allowed:
        flash('Deleting files is currently disabled, please contact the server host for more information.')
        return redirect(url_for('main', path=os.path.dirname(path)))
    if os.path.isfile(os.path.join('/data', path)):
        try:
            os.unlink(os.path.join('/data', path))
        except OSError:
            flash('Deleting this file failed:\n<pre>' + traceback.format_exc()+'</pre>')    
    else:
        try:
            os.rmdir(os.path.join('/data', path))
        except OSError:
            flash('Deleting this directory failed:\n<pre>' + traceback.format_exc()+'</pre>')    
    return redirect(url_for('main', path=os.path.dirname(path)))


def handle_file_request(original_path):
    path = os.path.join('/data', original_path)
    if request.method == 'GET':
        return send_from_directory(os.path.dirname(path), os.path.basename(path), cache_timeout=0)

    elif request.method == 'POST':
        if request.form['action'] == 'delete':
            if g.delete_allowed:
                os.unlink(path)
            else:
                flash('Deleting files is currently disabled, please contact the server host for more information.')
        else:
            flash(f'A file with this name already exists.')
        return redirect(url_for('main', path=os.path.dirname(original_path)))

def handle_directory_request(original_path):
    path = os.path.join('/data', original_path)
    if request.method == 'GET':
        return render_template('files.html', path=original_path, truepath=path, os=os, can_add=g.create_allowed, can_del=g.delete_allowed)

    elif request.method == 'POST':
        if request.form['action'] == 'delete':
            return handle_delete_request()
        elif request.form['action'] == 'upload':
            if 'file' not in request.files or not request.files['file'].filename:
                flash('Your request did not contain a file to upload.')
                return redirect(url_for('main', path=os.path.dirname(original_path)))
            name = secure_filename(request.files['file'].filename)
            if os.path.exists(os.path.join(path, name)):
                flash("After normalization, this file's name matched another file's name. Please rename your file before uploading.")
                return redirect(url_for('main', path=os.path.dirname(original_path)))
            request.files['file'].save(os.path.join(path, name))
            return redirect(url_for('main', path=os.path.dirname(original_path)))
        elif request.form['action'] == 'mkdir':
            if g.create_allowed:
                dirname = request.form['dirname']
                try:
                    os.mkdir(os.path.join('/data', path, dirname))
                    return redirect(url_for('main', path=original_path))
                except OSError:
                    flash('An error occured while creating this directory, probably because the name matches an existing entry.')
            else:
                flash('Creating files is currently disabled, please contact the server host for more information.')
            return redirect(url_for('main', path=os.path.dirname(original_path)))

def handle_nonexisting_request(original_path):
    return 'This file or directory does not exist.', 404


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def main(path):
    original_path = path
    path = os.path.join('/data', original_path)
    if os.path.isfile(path):
        return handle_file_request(original_path)
    elif os.path.isdir(path):
        return handle_directory_request(original_path)
    else:
        return handle_nonexisting_request(original_path)


@app.route('/__stylesheet__.css')
def stylesheet():
    return send_from_directory('/', 'bootstrap.min.css')

