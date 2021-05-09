import jinja2, functools, os
from flask import render_template

def template_renderer(func):
    @functools.wraps(func)
    def renderer_wrapper(self, app, *args, **kwargs):
        # HACK: This is the only way I found that jinja won't cache
        #       the templates across jurisdictions
        app.jinja_env.cache = {}

        if self.template_loader:
            default_loader = app.jinja_loader

            app.jinja_loader = jinja2.ChoiceLoader([
                self.template_loader,
                app.jinja_loader,
            ])
            rendered = func(self, *args, **kwargs)

            app.jinja_loader = default_loader
            return rendered
        return func(self, *args, **kwargs)
    return renderer_wrapper


class StateCourtBot():
    def __init__(self, state_code):
        self.state_code = state_code
        self.get_case = None
        self.register_reminder = None
        self.required_fields = None
        self.template_loader = None
        path = os.path.join(os.path.dirname(__file__), 'jurisdictions', state_code, 'templates')
        if os.path.isdir(path):
            self.template_loader = jinja2.FileSystemLoader(path)


    def get_case_callback(self, fn):
        """
        Decorator for attaching the method to get a case from the state's docket
        """

        self.get_case = fn
        return fn


    def register_callback(self, **required_fields):
        """
        Decorator for registering a cell phone against a specific case.
        """

        def wrapper(fn):
            if not required_fields:  # if empty
                raise ArgumentError('A minimum of one field is a required to identify cases.')
            self.required_fields = required_fields
            self.register_reminder = fn
            return fn
        return wrapper


    def new_case(self, **kwargs):
        return courtbot.CourtBotCase(**kwargs)


    def validate_input_callback(self, fn):
        """
        Decorator for attaching an optional custom validation?
        """

        pass


    def register_optin(self, raw_params):
        """
        This is the callback from the raw request sending in
        the ultimate opt-in for a text reminder for the court date.
        """

        if self.register_reminder is None:
            raise CourtBotException('register_reminder attempted without registering a reminder callback.')

        params = {}
        if 'cellphone' in raw_params.keys():
            if not CELLPHONE_REGEX.match(raw_params['cellphone']):
                raise ArgumentError(f'Invalid cell phone number provided.')
            params['cellphone'] = raw_params['cellphone']
        else:
            raise ArgumentError(f'No cell phone number provided.')

        for k, v in self.required_fields.items():
            if k not in raw_params.keys():
                raise ArgumentError(f'{k} is a required field')
            if callable(v):
                if not v(raw_params[k]):
                    raise ArgumentError(f'Invalid value provided for {k}')
            elif not v.match(raw_params[k]):
                raise ArgumentError(f'Invalid value provided for {k}')
            params[k] = raw_params[k]

        return self.register_reminder(**params)


    @template_renderer
    def render_lookup_page(self, error=None):
        return render_template('state.html')


    @template_renderer
    def render_case_info_page(self, case, error=None):
        return render_template('case.html', case=case, error=error)


    @template_renderer
    def render_optin_page(self, case, error=None):
        return render_template('optin.html', case=case, error=error)
