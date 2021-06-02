import jinja2, functools, os, re
from flask import Blueprint, render_template
from wtforms import Form, StringField, SelectField, validators, ValidationError
from wtforms.widgets import HiddenInput


def validate_cellphone(form, field):
    try:
        text = re.sub('[^\d]', '', field.data)
        l = len(text)
        if l < 10 or l > 11 or (l == 11 and text[0] != '1'):
            raise ValidationError('Invalid Cell Phone Number Provided.')
    except TypeError:
        raise ValidationError('Invalid Cell Phone Number Provided.')


def build_optin_form(fields):
    class L(Form):
        def as_hidden(self):
            for field in self:
                field.widget = HiddenInput()
            return self

    for name, options in fields.items():
        title, validation = options
        vtype = type(validation)
        if vtype is list:
            setattr(L, name, SelectField(title, choices=validation))
        else:
            if vtype is tuple:
                regex, message = validation
                validator = validators.Regexp(regex, message=message)
            elif callable(validation) or str(vtype).startswith('wtforms.validators.', 8):
                validator = validation
            elif vtype in [re.Pattern, str]:
                validator = validators.Regexp(validation)
            setattr(L, name, StringField(title, [validators.InputRequired(), validator]))

    L.cellphone = StringField('Cell Phone Number <small>(ex: 302-555-0123)</small>', [validators.InputRequired(), validate_cellphone])
    return L


def setup_blueprint(state_code):
    name = f'courtbot.jurisdictions.{state_code}'
    return Blueprint(state_code, name, template_folder='templates', static_folder='static')


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
        self.cron = None
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
        self._optin_form = build_optin_form(fields)


    def optin_form(self, data):
        return self._optin_form(data)


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


    def cron_callback(self, fn):
        """
        Decorator for registering the cron callback for updating cases.
        """

        self.cron = fn
        return fn


    def register_optin(self, form):
        """
        This is the callback from the raw request sending in
        the ultimate opt-in for a text reminder for the court date.
        """

        pass


    def run_cron(self, case):
        """
        This runs every night for every incomplete case to perform an update on the case
        to ensure it does not text an invalid court date.  If the callback returns None,
        then there is nothing to be done.  If the callback returns a Case instance, the
        system will update the hearing date.

        TODO: figure out if we should send an immediate text to the subscriber to let them
        know their hearing date moved.  Perhaps there ought to be a "notify on updates"
        checkbox in the UI that is checked here?
        """

        if self.cron is None:
            return

        if _case := self.cron(case):
            # unless we get None back, the case was update, update the case information.
            pass


    def new_case(self, **kwargs):
        """
        Indirect for construction of a CourtBotCase instance
        """

        return courtbot.CourtBotCase(**kwargs)


    def get_valid_case(self, form):
        case_fields = {field.name: field.data for field in form if field.name in self.required_fields.keys()}
        return self.get_case(**case_fields)


    def render_lookup_page(self, form, lang='en', error=None):
        return render_template(f'{self.state_code}/state.{lang}.html', statebot=self,
                form=form, error=error)


    def render_case_info_page(self, case, form, lang='en', error=None):
        return render_template(f'{self.state_code}/case.{lang}.html', statebot=self,
                case=case, form=form, error=error)


    def render_confirmed_page(self, case, lang='en', error=None):
        return render_template(f'{self.state_code}/confirmed.{lang}.html', statebot=self,
                case=case, error=error)


    def render_failure_page(self, case, form, error, lang='en'):
        return render_template(f'{self.state_code}/failure.{lang}.html', statebot=self,
                case=case, form=form, error=error)
