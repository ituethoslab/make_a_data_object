"""
Routes for MVC style traffic control in Flask.
"""
from flask import Response, render_template, request
from make_a_data_object import app
from make_a_data_object.models import AdditiveDataObject, DefaultParameters


@app.route('/hello')
def hello_world():
    """Just a test route."""
    return "Hello world."


@app.route('/')
def index():
    """Index route."""
    return render_template('index.html',
                           default_smoothing=DefaultParameters.smoothing)


@app.route('/make', methods=['POST'])
def submit():
    """Route for receiving the input form."""
    abstract = request.form['abstract']
    precip = [float(p) for p in request.form['precipitation'].split(',')]
    daylength = float(request.form['daylength'].replace(':', '.'))
    try:
        smoothing = int(request.form.get('smoothing'))
    except ValueError:
        smoothing = DefaultParameters.smoothing

    try:
        limit = int(request.form.get('limit'))
    except ValueError:
        limit = DefaultParameters.limit

    filename = request.form.get('filename') or DefaultParameters.filename

    app.logger.debug("Parsed input abstract:{}, precip:{}, daylength: {}, smoothing:{}, limit:{}, filename:{}".format(abstract, precip, daylength, smoothing, limit, filename))
    data_object = AdditiveDataObject(abstract, precip, daylength,
                                     size=450, limit=limit, alpha=smoothing)
    return Response(str(data_object), mimetype='text/plain', headers={"content-disposition": "attachment;filename={}".format(filename)})
