import re
import courtbot
import dsccs  # Delaware State Court Connect Scraper / Pending


REQUIRED_FIELDS = {
    'case_id': ('Case Number', re.compile('^(?P<court>w+)-(?P<year>\d{2})-(?P<case>\d+)$')),
    # cellphone is automatically included
}
REMINDER_MESSAGE = '''Hello!  You're hearing is tomorrow at {when} and will be held at {location}; {judge} presiding.  Please remember to bring your id, and arrive early.'''


bot = courtbot.state('DE', REQUIRED_FIELDS)

@bot.get_case_callback
def delaware_get_case(self, case_id):
    try:
        return dsccs.fetch_case(case_id)
    except dsccs.CourtConnectParseException as ex:
        raise courtbot.CourtBotException(ex.get_message())


@bot.registration_callback
def delaware_registration_reminder(self, *, case_id, cellnumber):
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
