""" This file is designated as a place to keep functions that are for
 math calculations, data analysis, plot creation and streaming of the plot images"""
import matplotlib.pyplot as plt  # for matplotlib plots
import base64  # for matplotlib plots
from io import BytesIO  # for matplotlib plots
from .models import ActivityLookup, ActivityRecord, UserProfile, UnitsOfMeasure
import datetime as dt  # for date based querrys

def get_graph():
    """
    code here is taken almost directly from the following video
    https://www.youtube.com/watch?v=jrT6NiM46jk

    As is, this function will take the active figure and stuff it into a buffer for display.
    it is to be called after the figure is all set up. This will be called in a place
    similar to plt.show()"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(x, y, size=(6, 3), plot_title='Plot', x_label='Date', y_label='Value'):
    plt.switch_backend('AGG')
    plt.figure(figsize=size)
    plt.plot(x, y)
    plt.title(plot_title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.xticks(rotation=45)
    plt.tight_layout()
    graph = get_graph()
    return graph

def convert_to_percent(raw_values):
    """ this function takes a list of numbers and returns
    each value as a percent of the first value in the list."""
    first_value = raw_values[0]
    percentages = [(100 * v/first_value) for v in raw_values]
    return percentages

def get_differentials(raw_values):
    """This function takes a list of numbers and returns the
    difference of the numbers in order."""
    diffs = [0]
    for i in range(len(raw_values) - 1):
        dif = raw_values[i + 1] - raw_values[i]
        diffs.append(dif)
    return diffs

def get_points(userProf, start_date=None, end_date=None):
    """


    PARAMS
    ------
    userProf - userProfile
    """
    records = ActivityRecord.objects.filter(user_num=userProf.user_number)
    if start_date is not None:
        records = records.filter(record_date__gte=start_date)
    if end_date is not None:
        records = records.filter(record_date__lte=end_date)
    points = sum([r.points for r in records])
    return points

def get_point_leaders(group=None, limit=10, start_date=None, end_date=None):
    if group is not None:
        users = UserProfile.objects.filter(group_id=group)  # This needs to be fixed when groups are implemented
    else:
        users = UserProfile.objects.all()
    leader_list = []
    for user in users:
        points = get_points(user, start_date=start_date, end_date=end_date)
        tup = (user.user_name, points)
        leader_list.append(tup)
    leader_list.sort(key=lambda a: a[1], reverse=True)
    if limit >= len(leader_list):
        limit = len(leader_list)
    return leader_list[(-1 * limit):]


def get_weight_lost(userProf, start_date=None, end_date=None):
    """ returns the weight lost as a percent. if a time frame is specified,
    only the values in that time are considered."""
    weigh_in_activity = ActivityLookup.objects.get(activity_name="Weigh In")
    records = ActivityRecord.objects.filter(user_num=userProf.user_number).filter(activity_num=weigh_in_activity.activity_number)
    if start_date is not None:
        records = records.filter(record_date__gte=start_date)
    if end_date is not None:
        records = records.filter(record_date__lte=end_date)
    if len(records) < 2:
        return 0  # zero is returned when there aren't enough records
    first_weight = records[0].number_recorded
    last_weight = records[len(records) - 1].number_recorded
    points = 100 * (last_weight - first_weight) / first_weight
    return points


def get_weight_loss_leaders(group=None, limit=10, start_date=None, end_date=None):
    if group is not None:
        users = UserProfile.objects.filter(group_id=group)  # This needs to be fixed when groups are implemented
    else:
        users = UserProfile.objects.all()
    leader_list = []
    for user in users:
        weight_lost = get_weight_lost(user, start_date=start_date, end_date=end_date)
        if weight_lost >= 0:
            tup = (user.user_name, round(weight_lost, 3))
            leader_list.append(tup)
        else:
            continue  # don't show people that have gained weight
    leader_list.sort(key=lambda a: a[1], reverse=True)
    if limit >= len(leader_list):
        limit = len(leader_list)
    return leader_list[:limit]


def get_frequency_days(userProf, start_date=None, end_date=None):
    unique_dates = get_unique_dates_with_records(end_date, start_date, userProf)
    return len(unique_dates)


def get_unique_dates_with_records(end_date, start_date, userProf):
    records = ActivityRecord.objects.filter(user_num=userProf.user_number).order_by('record_date')
    if start_date is not None:
        records = records.filter(record_date__gte=start_date)
    if end_date is not None:
        records = records.filter(record_date__lte=end_date)
    unique_dates = []
    for r in records.iterator():
        if r.record_date.date() not in unique_dates:
            unique_dates.append(r.record_date.date())
    return unique_dates


def get_frequency_leaders(group=None, limit=10, start_date=None, end_date=None):
    if group is not None:
        users = UserProfile.objects.filter(group_id=group)  # This needs to be fixed when groups are implemented
    else:
        users = UserProfile.objects.all()
    leader_list = []
    for user in users:
        tup = (user.user_name, get_frequency_days(user, start_date=start_date, end_date=end_date))
        leader_list.append(tup)
    leader_list.sort(key=lambda a: a[1], reverse=True)
    if limit > len(leader_list):
        limit = len(leader_list)
    return leader_list[:limit]


def get_recording_streak(userProf, start_date=None, end_date=None, live_streak=False):
    unique_dates = get_unique_dates_with_records(end_date, start_date, userProf)
    if len(unique_dates) == 0:
        return 0
    highest_streak = 0
    streak = 0
    streak_end = unique_dates[-1]
    streak_beginning = streak_end
    if live_streak and (end_date is not None) and (end_date.date() != unique_dates[-1]):
        return 0  # the streak did not continue to the end of the time period, so return zero for current streak

    for i in range(1, len(unique_dates)):

        if unique_dates[-i] == streak_end:
            continue
        elif unique_dates[-i] == streak_beginning - dt.timedelta(days=1):
            streak_beginning = unique_dates[-i]
            if i == len(unique_dates):
                streak = (streak_end - streak_beginning).days
                if streak > highest_streak:
                    highest_streak = streak
        else:
            streak = (streak_end - streak_beginning).days
            streak_end = unique_dates[-i]
            streak_beginning = streak_end
            if live_streak:
                break
            if streak > highest_streak:
                highest_streak = streak
    return highest_streak + 1


def get_streak_leaders(group=None, limit=10, start_date=None, end_date=None,
                       only_live_streaks=False):
    if group is not None:
        users = UserProfile.objects.filter(group_id=group)  # This needs to be fixed when groups are implemented
    else:
        users = UserProfile.objects.all()
    leader_list = []
    for user in users:
        streak = get_recording_streak(user, start_date=start_date, end_date=end_date,
                                      live_streak=only_live_streaks)
        tup = (user.user_name, streak)
        leader_list.append(tup)
    leader_list.sort(key=lambda a: a[1], reverse=True)
    if limit > len(leader_list):
        limit = len(leader_list)
    return leader_list[:limit]

def cumsum(x_list):
    f_x_list = [x_list[0]]
    for i in range(1, len(x_list)):
        value = f_x_list[i - 1] + x_list[i]
        f_x_list.append(value)
    return f_x_list
