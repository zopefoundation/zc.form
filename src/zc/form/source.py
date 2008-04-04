import pytz
import zc.sourcefactory.basic

class USTimeZones(
    zc.sourcefactory.basic.BasicSourceFactory):

    """List of timezones taken from pytz"""

    tzs = [tz for tz in pytz.common_timezones if 'US/' in tz and
                                            'Pacific-New' not in tz]

    def getValues(self):
        return self.tzs

    def getTitle(self, value):
        return value

    def getToken(self, value):
        return value

