import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
import json

from init import process

UPLOAD_FOLDER = '/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tar'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# @app.route('/')
# def hello_world():
    # return 'Hello, World!'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        print(request.files)
        print(request.form)
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            dir = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(dir)

            cflags = request.form['cflags']
            lang = request.form['lang']
            test_mode = request.form['test_mode']
            # Vamos a tener que poner los flags como argumento, no podemos dejarlo como CFLAGS env variable

            result = process(lang=lang, test_mode=test_mode, filename=dir)

            return json.dumps(result)






            