import jinja2, functools, os, re
from flask import Blueprint, render_template
from wtforms import Form, StringField, SelectField, validators, ValidationError


def validate_cellphone(form, text):
    _text = re.sub('[^\d]', '', text)
    l = len(_text)
    if l < 10 or l > 11 or (l == 11 and _text[0] != '1'):
        raise ValidationError('Invalid Cell Phone Number Provided.')
    return _text


def build_lookup_form(fields):
    class L(Form): pass
    for name, options in fields.items():
        title, validation = options
        if isinstance(validation, list):
            setattr(L, name, SelectField(title, choices=validation))
        # elif TODO: isinstance validation, any validators.* classes
        #    setattr(L, name, StringField(title, [validation]))
        else:
            setattr(L, name, StringField(title, [validators.InputRequired(), validators.Regexp(validation)]))
    return L


def build_optin_form(L):
    class O(L): pass
    O.cellphone = StringField('Cell Phone Number', [validate_cellphone])
    return O


def setup_blueprint(state_code):
    t_path = os.path.join(os.path.dirname(__file__), 'jurisdictions', state_code, 'templates')
    s_path = os.path.join(os.path.dirname(__file__), 'jurisdictions', state_code, 'static')
    return Blueprint(state_code, __name__, template_folder=t_path, static_folder=s_path)


class StateCourtBot():
    """
    StateCourtBot is the main workhorse interfacing functionality from each
    state's unique court case lookup to a normalized structure so one common
    tool can be used to provide text messages to case participants.
    """

    def __init__(self, state_code, state_name, fields):
        self.state_code = state_code
        self.state_name = state_name
        self.get_case = None
        self.register_reminder = None
        self.blueprint = setup_blueprint(state_code)
        self.set_required_fields(fields)


    def set_required_fields(self, fields):
        """
        Add the required fields and build the HTML WTForms used in the
        templating engine.

        fields should be a Dict, where the key is the field name and the value
        is a tuple consisting of ('title text', validation) where validation is
        either a singular regex or a list roif ('key', 'value') tuples used for a
        select tag's options.
        """

        if not fields or set(fields.keys()) == set(['cellphone']):  # if empty
            raise ArgumentError('A minimum of one field is a required to identify cases.  Cellphone is handled automatically.')

        self.required_fields = fields
        self.lookup_form = build_lookup_form(fields)
        self.optin_form = build_optin_form(self.lookup_form)


    def get_case_callback(self, fn):
        """
        Decorator for attaching the method to get a case from the state's docket
        """

        self.get_case = fn
        return fn


    def registration_callback(self, fn):
        """
        Decorator for registering a cell phone against a specific case.
        """

        self.register_reminder = fn
        return fn


    def register_optin(self, form):
        """
        This is the callback from the raw request sending in
        the ultimate opt-in for a text reminder for the court date.
        """

        pass


    def new_case(self, **kwargs):
        """
        Indirect for construction of a CourtBotCase instance
        """

        return courtbot.CourtBotCase(**kwargs)


    def render_lookup_page(self, form, lang='en', error=None):
        return render_template(f'{self.state_code}/state.{lang}.html', statebot=self,
                form=form, error=error)


    def render_case_info_page(self, case, form, lang='en', error=None):
        return render_template(f'{self.state_code}/case.{lang}.html', statebot=self,
                case=case, form=form, error=error)


    def render_optin_page(self, case, form, lang='en', error=None):
        return render_template(f'{self.state_code}/optin.{lang}.html', statebot=self,
                case=case, form=form, error=error)


    def render_confirmed_page(self, case, lang='en', error=None):
        return render_template(f'{self.state_code}/confirmed.{lang}.html', statebot=self,
                case=case, error=error)
