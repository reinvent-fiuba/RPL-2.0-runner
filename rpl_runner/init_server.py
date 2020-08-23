import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import json

from init import process

UPLOAD_FOLDER = '/home/runner'
ALLOWED_EXTENSIONS = {'tar'}

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health')
def health():
    return "pong"

@app.route('/', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dir = os.path.join(UPLOAD_FOLDER, filename)
        file.save(dir)
        cflags = request.form['cflags']
        lang = request.form['lang']
        test_mode = request.form['test_mode']
        # Vamos a tener que poner los flags como argumento, no podemos dejarlo como CFLAGS env variable
        try:
            result = process(lang=lang, test_mode=test_mode, filename=dir, cflags=cflags)
        except Exception as e:
            result = {}
            result["test_run_result"] = "UNKNOWN_ERROR"
            result["test_run_stage"] = "unknown"
            result["test_run_exit_message"] = str(e)
        finally:
            os.system(f'rm -r -f {UPLOAD_FOLDER}/*')
        return json.dumps(result)






            