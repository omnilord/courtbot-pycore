class StateCourtBot():
    def __init__(state):
        self.state = state
        self.get_case = None
        self.register_reminder = None
        self.required_fields = None


    def get_case_callback(self):
        """
        Decorator for attaching the method to get a case from the state's docket
        """

        def wrapper(fn):
            self.get_case = fn
            return fn
        return wrapper


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


    def render_page_callback(self):
        """
        Decorator for attaching an optional custom template/renderer for the opt-in page?

        This would allow states with multiple court jurisditions that do not have a unified
        record system to provide custom UI that may include JavaScript to dynamically adapt
        the form as court information is drilled down.
        """

        pass


    def validate_input_callback(self):
        """
        Decorator for attaching an optional custom validation?
        """

        pass


    def receive_registry(self, raw_params):
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

        case = self.register_reminder(**params)
