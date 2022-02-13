
# This is a group of custom made context processors
from FeelGreat_main.models import ActivityLookup, UserProfile
import datetime

def daily_renderer(request):
    tomorrow = datetime.date.today() + datetime.timedelta(days=1.0)
    todays_activity = ActivityLookup.get_daily_activity()
    tomorrows_activity = ActivityLookup.get_daily_activity(date_of_interest=tomorrow)
    return {'todays_activity': todays_activity,
            'tomorrows_activity': tomorrows_activity}
