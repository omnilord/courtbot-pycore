import os
from flask import Flask, render_template
from .. import get_states, get_state

tpdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
app = Flask('CourtBot', template_folder=tpdir)

@app.route('/')
def index():
    return render_template('index.html', states=get_states())

@app.route('/<string:state>')
def state_index(state):
    statebot = get_state(state.upper())
    template = statebot.template()
    return template.render()
