import logging
from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

import make_a_data_object.models
import make_a_data_object.routes
