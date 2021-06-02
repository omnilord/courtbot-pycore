import os
from flask import Flask, render_template, request
from .. import CourtBotException, CourtBotMisconfigured, CourtBotUnknownState, get_states, get_state

from flask import jsonify

tpdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
app = Flask('CourtBot', template_folder=tpdir)

# Config
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


# step 1, GET: choice your state
@app.route('/')
def index():
    return render_template('index.html', states=get_states())


@app.route('/favicon.ico')
def favicon():
    # TODO: get a favicon
    return 'data:,'


# step 2, GET: render case lookup
# step 3, POST: render case and confirm opt-in on case
@app.route('/<string:state_code>', methods=['GET', 'POST'])
def state_index(state_code):
    statebot = get_state(app, state_code.upper())
    form = statebot.optin_form(request.form)
    error = None
    try:
        if request.method == 'POST' and form.validate():
            case = statebot.get_valid_case(form)
            return statebot.render_case_info_page(case, form.as_hidden())
    except CourtBotException as err:
        error = err
    return statebot.render_lookup_page(form, error=error)


# step 4, POST: send confirmation that your phone has been added
@app.route('/<string:state_code>/optin', methods=['POST'])
def state_optin(state_code):
    statebot = get_state(app, state_code.upper())
    form = statebot.optin_form(request.form)
    error = None
    try:
        if request.method == 'POST' and form.validate():
            case = statebot.register_optin(form)
            return statebot.render_confirmed_page(case)
    except CourtBotException as err:
        error = err
    return statebot.render_failure_page(error=error)


@app.errorhandler(CourtBotMisconfigured)
def default_error_handler(error):
    return f"An error occurred. 😱<br/>{error.state_name} is misconfigured."


@app.errorhandler(CourtBotUnknownState)
def default_error_handler(error):
    return f"An error occurred. 😱<br/>{error.state_name} is not a configured state."
