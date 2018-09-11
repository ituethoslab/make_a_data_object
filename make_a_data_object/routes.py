from flask import Flask, Response, render_template, request
from make_a_data_object import app
from make_a_data_object.models import AdditiveDataObject, DefaultParameters


@app.route('/hello')
def hello_world():
    """Just a test route."""
    return "Hello world."


@app.route('/')
def index():
    """Index route."""
    return render_template('index.html', default_smoothing=DefaultParameters.smoothing)


@app.route('/make', methods=['POST'])
def submit():
    a = request.form['abstract']
    p = [float(p) for p in request.form['precipitation'].split(',')]
    d = float(request.form['daylength'].replace(':', '.'))
    try:
        s = int(request.form.get('smoothing'))
    except ValueError:
        s = DefaultParameters.smoothing

    try:
        limit = int(request.form.get('limit'))
    except ValueError:
        limit = DefaultParameters.limit

    f = request.form.get('filename') or DefaultParameters.filename

    app.logger.debug("Parsed input a:{}, p:{}, d: {}, s:{}, l:{}, f:{}".format(a, p, d, s, limit, f))
    do = AdditiveDataObject(a, p, d, size=450, limit=limit, alpha=s)
    return Response(str(do), mimetype='text/plain', headers={"content-disposition": "attachment;filename={}".format(f)})
