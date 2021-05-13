import re
import courtbot
#import oscn

REQUIRED_FIELDS = {
    'case_id': ('Case Number', re.compile('^(?P<court>w{2})-(?P<year>\d{4})-(?P<case>\d+)$')),
    'year': ('Year', re.compile('^\d{4}$')),
    'county': ('County', re.compile('^.+$')),
    # cellphone is automatically included
}
REMINDER_MESSAGE = '''Hello!  You're arraignment is tomorrow at {when}.  Please remember to bring your id, and arrive early.'''

bot = courtbot.state('OK', REQUIRED_FIELDS)
