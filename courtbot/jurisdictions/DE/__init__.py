import re, os
import courtbot
import dsccs  # Delaware State Court Connect Scraper / Pending
from wtforms import ValidationError


CASE_ID_REGEX = re.compile('^\s*((?P<court>\w{4})-(?P<year>\d{2})-(?P<case>\d{6}))\s*$')


def validate_court_case(form, field):
    m = CASE_ID_REGEX.match(field.data.upper())
    if not m:
        raise ValidationError('Invalid format for case id.  Case ids will look like: <em>JP13-21-012345</em>')
    if not m.group('court') == 'JP13':
        raise ValidationError('We are only registering court case that begin with JP13 at this time.')


REQUIRED_FIELDS = {
    'case_id': ('Case Number <small>(ex: JP13-20-567890)</small>', validate_court_case),
    # cellphone is automatically included
}
REMINDER_MESSAGE = '''Hello!  You're hearing is tomorrow at {when} and will be held at {location}; {judge} presiding.  Please remember to bring your id, and arrive early.'''


bot = courtbot.state('DE', REQUIRED_FIELDS)

#TODO: only cache in development
dsccs.cache.directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', '..', '.cache')


@bot.get_case_callback
def delaware_get_case(*, case_id):
    try:
        return dsccs.fetch_case(case_id)
    except dsccs.CourtConnectParseException as ex:
        raise courtbot.CourtBotException(ex.get_message())


@bot.registration_callback
def delaware_registration_reminder(*, case_id, cellnumber):
    case = delaware_get_case(case_id)
    when = case.schedule[0].datetime

    # return the data required for courtbot transmission
    return self.new_case(
        case_id=case.id,
        when=when - datetimedelta(day=-1),
        what=REMINDER_MESSAGE.format(case_id=case.id, location=case.location, judge=case.judge),
        cellphone=cellphone,
        origination=case # Something for debugging / error tracing?
    )
