import os
from functools import cache
from importlib import import_module
from .. import StateCourtBot, CourtBotUnknownState


STATES = {
    'AL': 'Alabama',
    'AK': 'Alaska',
    'AS': 'American Samoa',
    'AZ': 'Arizona',
    'AR': 'Arkansas',
    'CA': 'California',
    'CO': 'Colorado',
    'CT': 'Connecticut',
    'DC': 'District of Columbia',
    'DE': 'Delaware',
    'FL': 'Florida',
    'GA': 'Georgia',
    'GU': 'Guam',
    'HI': 'Hawaii',
    'ID': 'Idaho',
    'IL': 'Illinois',
    'IN': 'Indiana',
    'IA': 'Iowa',
    'KS': 'Kansas',
    'KY': 'Kentucky',
    'LA': 'Louisiana',
    'ME': 'Maine',
    'MD': 'Maryland',
    'MA': 'Massachusetts',
    'MI': 'Michigan',
    'MN': 'Minnesota',
    'MS': 'Mississippi',
    'MO': 'Missouri',
    'MT': 'Montana',
    'NE': 'Nebraska',
    'NV': 'Nevada',
    'NH': 'New Hampshire',
    'NJ': 'New Jersey',
    'NM': 'New Mexico',
    'NY': 'New York',
    'NC': 'North Carolina',
    'ND': 'North Dakota',
    'MP': 'Northern Mariana Islands',
    'OH': 'Ohio',
    'OK': 'Oklahoma',
    'OR': 'Oregon',
    'PA': 'Pennsylvania',
    'PR': 'Puerto Rico',
    'RI': 'Rhode Island',
    'SC': 'South Carolina',
    'SD': 'South Dakota',
    'TN': 'Tennessee',
    'TX': 'Texas',
    'UT': 'Utah',
    'VT': 'Vermont',
    'VI': 'Virgin Islands',
    'VA': 'Virginia',
    'WA': 'Washington',
    'WV': 'West Virginia',
    'WI': 'Wisconsin',
    'WY': 'Wyoming'
}


def is_state_configured(state_code):
    """
    A Lazy utility function to determine if a state has been configured.
    It only check for the presents of the state's directory in 'jurisdictions'.
    """

    if state_code not in STATES.keys():
        return False
    dirname = os.path.dirname(__file__)
    target = os.path.join(dirname, state_code)
    return os.path.isdir(target)


def get_states():
    """
    A utility function that returns a list of states that have been configured
    in the 'jurisdictions' directory.
    """

    return {abbrv : state for abbrv, state in STATES.items() if is_state_configured(abbrv)}


@cache
def get_state(app, state_code):
    """
    A utility function that fetches a state's package from cache or the
    'jurisdictions' directory, assuming it exists.
    """

    if not is_state_configured(state_code):
        error = CourtBotUnknownState(f'{state_code} is an unknown state code.')
        error.state_code = state_code
        error.state_name = 'unknown'
        raise error

    bot = import_module(f'.{state_code}', package=__package__).bot
    app.register_blueprint(bot.blueprint, url_prefix=f'/{state_code}')
    return bot


def state(state_code, fields):
    return StateCourtBot(state_code, STATES[state_code], fields)
