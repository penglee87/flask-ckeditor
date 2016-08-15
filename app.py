# -*- coding: utf-8 -*-

import os
import re
import json
import random
import urllib
import datetime
from flask_script import Manager, Shell
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from flask import Flask, request, render_template, url_for, make_response

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

class PostForm(Form):
    title = StringField("The title", validators=[Required()])
    summary = StringField("The summary", validators=[Required()])
    submit = SubmitField('Submit')
    cancel = SubmitField('Cancel')


def gen_rnd_filename():
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))


@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        content = request.form.get('content')
        print('content',content)
        return '''
    <!doctype html>
    <h1>Upload new File</h1>
    '''

    return render_template('index.html')


@app.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)

        filepath = os.path.join(app.static_folder, 'upload', rnd_name)

        # 检查路径是否存在，不存在则创建
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'

        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response


if __name__ == '__main__':
    app.run(debug=True)
