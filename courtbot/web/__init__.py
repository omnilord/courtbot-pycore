import os
from flask import Flask, render_template, request
from .. import CourtBotException, get_states, get_state

tpdir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
app = Flask('CourtBot', template_folder=tpdir)


# step 1, choice your state
@app.route('/')
def index():
    return render_template('index.html', states=get_states())

@app.route('/favicon.ico')
def favicon():
    return None

# step 2, look up your case
@app.route('/<string:state_code>', methods=['GET', 'POST'])
def state_index(state_code):
    statebot = get_state(state_code.upper())
    error = None
    if request.method == 'POST':
        try:
            case = statebot.fetch_valid_case(request.form)
            return statebot.render_case_info_page(app, case)
        except CourtBotException as err:
            error = err
    print(state_code, statebot)
    return statebot.render_lookup_page(app, error=error)


# step 4, receive confirmation that your phone has been added
@app.route('/<string:state_code>/optin', methods=['POST'])
def state_optin(state_code):
    # TODO: create a record in the 'reminders' table
    statebot = get_state(state_code.upper())
    error = None
    try:
        optin = statebot.register_optin(request.form)
        return statebot.render_optin_page(app, optin)
    except CourtBotException as err:
        error = err
    return statebot.render_confirmation_page(app, error=error)


# step 5, TODO: catch errors
# @app.errorhandler(???)
# def default_error_handler(error):
#     pass
