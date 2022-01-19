from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.contrib.auth.models import User
from django.utils.datastructures import MultiValueDictKeyError


# Create your models here.
class UserProfile(models.Model):
    user_number = models.IntegerField(primary_key=True)
    user_auth_obj = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    user_name = models.CharField(max_length=150)
    birth_date = models.DateField(null=False)
    prof_image = models.ImageField(upload_to='prof_pics/', null=True, default=None)
    # pword_hash = models.?

    def __str__(self):
        return "User: {}".format(self.user_name)

    def get_age(self):
        return date.today() - self.birth_date

    def get_profile(user, firstname, lastname, birthday):
        tester = UserProfile.objects.filter(user_name=user.username)
        if tester.exists():
            return tester[0]
        else:  # create a profile for the given user
            userprof = UserProfile(user_auth_obj=user, first_name=firstname,
                                   last_name=lastname, birth_date=birthday,
                                   user_name=user.username, user_number=user.id)
            return userprof


class UnitsOfMeasure(models.TextChoices):
    EACH = 'each', _('Each')
    POUNDS = 'lbs.', _('Pounds')
    OUNCES = 'oz', _('Ounces')
    SERVINGS = 'Serving', _('Servings')
    MINUTES = 'min', _('Minutes')
    DAILY = 'day', _('Per Day')
    WEEKLY = 'weekly', _('Per Week')
    DAILY_SPECIAL = 'daily_calendar', _('Daily Special')


class ActivityLookup(models.Model):
    activity_number = models.AutoField(primary_key=True)
    # activity_name is what the activity is called
    activity_name = models.CharField(max_length=100, unique=True)

    # value_type records what units the activity uses for measurement
    value_type = models.CharField('Unit Type',
                                  max_length=20,
                                  choices=UnitsOfMeasure.choices,
                                  default=UnitsOfMeasure.EACH,)
    # point_vaue is the number of points for a single unit of activity
    point_value = models.FloatField('Points Per Unit')
    # maximum number fo points earnable for this activity per day.
    # A zero indicates no limit.
    daily_point_limit = models.IntegerField(default=0)
    act_description = models.TextField(default="Description pending.")

    def __str__(self):
        return self.activity_name

    def get_daily_activity():
        act_list = ActivityLookup.objects.exclude(value_type=UnitsOfMeasure.DAILY_SPECIAL).exclude(activity_name="Weigh In")
        daily_seed = (date.today() - date(year=2022, month=1, day=2)).days
        daily_seed = daily_seed % len(act_list)
        if daily_seed == 1:  # 1 in monday
            return ActivityLookup.objects.get(activity_name == "Weigh In")
        else:
            return act_list[daily_seed]


class ActivityRecord(models.Model):
    record_number = models.AutoField(primary_key=True)
    record_date = models.DateTimeField()  # date the activity happened
    # user_name indicates who did the activity
    user_num = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    # activity_num indicates the type of activity done
    activity_num = models.ForeignKey('ActivityLookup',
                                     on_delete=models.PROTECT)
    # This is the number of things done
    number_recorded = models.IntegerField()
    # This is the number of points earned for the activity
    points = models.IntegerField()

    def create(new_points, number_recorded, user, act_num):
        act = ActivityLookup.objects.get(activity_number=act_num)
        userProf = UserProfile.objects.get(user_auth_obj=user)
        record = ActivityRecord(record_date=date.today(),
                                user_num=userProf,
                                activity_num=act,
                                number_recorded=number_recorded,
                                points=new_points)
        return record

    def verify_points_input(request, activity_id):
        """ this method is designed to take a POST request and an activity and
        determine how many points to assign for the given activity and the given user.
        """
        activity = ActivityLookup.objects.get(pk=activity_id)
        # get initial points and activity value
        if activity.value_type == UnitsOfMeasure.DAILY:  # check box activities
            try:
                is_checked = request.POST[activity.activity_name]
            except MultiValueDictKeyError as mvdke:
                return 0, 0
            if is_checked:
                points = float(activity.point_value)
                value = 1  # DAILY means only one per day
        else:  # number entry type activities
            if request.POST[activity.activity_name] == '':
                value = 0
            else:
                value = float(request.POST[activity.activity_name])
            points = float(activity.point_value) * value
        if points > activity.daily_point_limit and activity.daily_point_limit != 0:
            points = activity.daily_point_limit
        records = ActivityRecord.objects.filter(user_num=request.user.id).filter(record_date=date.today()).filter(activity_num=activity_id)
        points_so_far_today = sum([r.points for r in records])
        if points_so_far_today >= activity.daily_point_limit:
            points = 0
        elif (points_so_far_today + points) > activity.daily_point_limit:
            points = activity.daily_point_limit - points_so_far_today
        return points, value

    def __str__(self):
        return "user number {} recorded activity \
        number {} on {}".format(self.user_num,
                                self.activity_num,
                                self.record_date)
