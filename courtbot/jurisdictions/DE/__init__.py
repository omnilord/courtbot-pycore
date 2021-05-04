import re
import courtbot
import dsccs  # Delaware State Court Connect Scraper / Pending


REQUIRED_FIELDS = {
    'case_id': re.compile('^(?P<court>w+)-(?P<year>\d{2})-(?P<case>\d+)$'),
}
REMINDER_MESSAGE = '''Hello!  You're hearing is tomorrow at {when} and will be held at {location}; {judge} presiding.  Please remember to bring your id, and arrive early.'''


state_courtbot = courtbot.get_state('DE')


@state_courtbot.get_case_callback
def delaware_get_case(case_id):
    try:
        return dsccs.fetch_case(case_id)
    except dsccs.CourtConnectParseException => ex:
        raise courtbot.ParseException(ex.get_message())


@state_courtbot.register_callback(**REQUIRED_FIELDS)
def delaware_register_reminder(*, case_id, cellnumber):
    case = delaware_get_case(case_id)
    when = case.schedule[0].datetime

    # return the data required for courtbot transmission
    return courtbot.CourtBotCase(
        case_id=case.id,
        when=when - datetimedelta(day=-1),
        what=REMINDER_MESSAGE.format(case_id=case.id, location=case.location, judge=case.judge),
        cellphone=cellphone,
        origination=case # Something for debugging / error tracing?
    )
