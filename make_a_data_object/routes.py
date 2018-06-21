from flask import Flask, Response, render_template, request
from make_a_data_object import app
from make_a_data_object.models import Data, DataObject

@app.route('/hello')
def hello_world():
    """Just a test route."""
    return "Hello world."

@app.route('/')
def index():
    """Index route."""
    do = DataObject(Data.a, Data.p)
    return render_template('index.html')

@app.route('/make', methods=['POST'])
def submit():
    a = request.form['abstract']
    p = request.form['precipitation'].split(',')
    try:
        s = int(request.form.get('smoothing'))
    except ValueError:
        s = None

    try:
        l = int(request.form.get('limit'))
    except ValueError:
        l = None

    f = request.form.get('filename') or 'dataobject.dat'

    do = DataObject(a, p, size=250, limit=l, alpha=s)
    return Response(str(do), mimetype='text/plain', headers={"content-disposition": "attachment;filename={}".format(f)})

