import pytz
import zc.sourcefactory.contextual

class USTimeZones(
    zc.sourcefactory.contextual.BasicContextualSourceFactory):

    """List of timezones taken from pytz"""

    tzs = [tz for tz in pytz.common_timezones if 'US/' in tz]

    def getValues(self, context):
        return self.tzs

    def getTitle(self, value):
        return value

    def getToken(self, value):
        return value

