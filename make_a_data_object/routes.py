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
    return render_template('index.html', do=do)

@app.route('/make', methods=['POST'])
def submit():
    a = request.form['abstract']
    p = request.form['precipitation'].split(',')
    l = int(request.form.get('limit', 5))
    do = DataObject(a, p, limit=l, size=100)
    return Response(str(do), mimetype='text/plain', headers={"content-disposition": "attachment;filename=make.dat"})

