from flask import Flask

app = Flask(__name__, template_folder="templates")

# Import routes from surf.py
from flask_app.controllers import surf
