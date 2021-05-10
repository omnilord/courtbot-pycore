class CourtBotException(Exception):
    pass


def valid_cellphone(text):
    _text = re.sub('[^\d]', '', text)
    l = len(_text)
    if l < 10 or l > 11 or (l == 11 and _text[0] != '1'):
        raise ArgumentError('Invalid Cell Phone Number Provided.')
    return _text


from .StateCourtBot import StateCourtBot
from .Case import Case
from .jurisdictions import get_states, get_state
from .web import app
