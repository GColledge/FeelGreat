from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta

from .models import ActivityLookup, ActivityRecord, UserProfile
from .utils import get_differentials, convert_to_percent, get_plot, get_point_leaders, get_weight_loss_leaders,\
    get_frequency_leaders, get_streak_leaders, get_points
# Create your tests here.


class UserTestCase(TestCase):

    def setUp(self):
        user_a = User(username="test", email="test@invalid.com")
        user_a.password = "somepassword"
        user_a.save()

        user_b = User(username="test2", email="test2@invalid.com")
        user_b.password = "somepassword2"
        user_b.save()



    def test_get_profile(self):
        # get user from db
        user_a = User.objects.filter(username="test")
        self.assertEqual(len(user_a), 1)
        user_a = user_a[0]
        # create profile for user
        prof_a = UserProfile.get_profile(user_a, "test", "A", date(1985, 9, 9))
        prof_a.save()
        # test that profile creation worked as expected
        self.assertEqual(prof_a.user_name, user_a.username)
        # duplicate the user in prof_a and call it prof_b
        prof_b = UserProfile.get_profile(user_a, "test", "A", date(1985, 9, 9))
        self.assertEqual(prof_b, prof_a)

    def test_get_age(self):
        # get user from db
        user_a = User.objects.filter(username="test")
        self.assertEqual(len(user_a), 1)
        user_a = user_a[0]
        # create profile for user_a
        prof_a = UserProfile.get_profile(user_a, "test", "A", date(1985, 9, 9))
        prof_a.save()
        # test the get age method
        year = timedelta(days=365)
        age = prof_a.get_age()
        age_in_years = round(age / year, 0)
        self.assertEqual(int(age_in_years), int(36))


class ActivityRecordTestCase(TestCase):
    def setUp(self):
        # create a user and profile
        user_a = User(username="test", email="test@invalid.com")
        user_a.password = "somepassword"
        user_a.save()
        prof_a = UserProfile.get_profile(user_a, "test", "A", date(1985, 9, 9))
        prof_a.save()

        act_lookup_1 = ActivityLookup()
        act_lookup_1.activity_name = "eat testing"
        act_lookup_1.value_type = 'each'
        act_lookup_1.point_value = 10.0
        act_lookup_1.daily_point_limit = 30
        act_lookup_1.save()

        act_lookup_2 = ActivityLookup()
        act_lookup_2.activity_name = "push testing"
        act_lookup_2.value_type = 'each'
        act_lookup_2.point_value = 1.0
        act_lookup_2.daily_point_limit = 0
        act_lookup_2.save()

    def test_create(self):
        # get the user and profile
        user_a = User.objects.filter(username="test")[0]
        prof_a = UserProfile.objects.filter(user_name="test")[0]
        act_lookup_1 = ActivityLookup.objects.filter(activity_name="eat testing")[0]
        act_rec_1 = ActivityRecord.create(new_points=10, number_recorded=1,
                                          user=user_a,
                                          act_num=act_lookup_1.activity_number)
        act_rec_1.save()
        self.assertEqual(act_rec_1.points, 10)


class ActivityLookUpTestCase(TestCase):
    def setUp(self):
        user_a = User(username="test", email="test@invalid.com")
        user_a.password = "somepassword"
        user_a.save()

        act_lookup_1 = ActivityLookup()
        act_lookup_1.activity_name = "eat testing"
        act_lookup_1.value_type = 'each'
        act_lookup_1.point_value = 10.0
        act_lookup_1.daily_point_limit = 30
        act_lookup_1.save()

        act_lookup_2 = ActivityLookup()
        act_lookup_2.activity_name = "push testing"
        act_lookup_2.value_type = 'each'
        act_lookup_2.point_value = 1.0
        act_lookup_2.daily_point_limit = 0
        act_lookup_2.save()

        act_lookup_3 = ActivityLookup()
        act_lookup_3.activity_name = "ounce testing"
        act_lookup_3.value_type = 'oz'
        act_lookup_3.point_value = 0.3
        act_lookup_3.daily_point_limit = 30
        act_lookup_3.save()

        act_lookup_4 = ActivityLookup()
        act_lookup_4.activity_name = "daily task testing"
        act_lookup_4.value_type = 'daily_calendar'
        act_lookup_4.point_value = 5.0
        act_lookup_4.daily_point_limit = 5
        act_lookup_4.save()

        act_lookup_5 = ActivityLookup()
        act_lookup_5.activity_name = "Weigh In"
        act_lookup_5.value_type = 'daily_calendar'
        act_lookup_5.point_value = 5.0
        act_lookup_5.daily_point_limit = 5
        act_lookup_5.save()

        act_lookup_6 = ActivityLookup()
        act_lookup_6.activity_name = "daily task testing 2"
        act_lookup_6.value_type = 'daily_calendar'
        act_lookup_6.point_value = 5.0
        act_lookup_6.daily_point_limit = 5
        act_lookup_6.save()



    def test_get_daily_activity_for_monday(self):
        date_of_a_monday = date(2022, 1, 24)  # this date is an actual monday
        monday_activity = ActivityLookup.get_daily_activity(date_of_interest=date_of_a_monday)
        self.assertEqual(monday_activity.activity_name, "Weigh In",
                         msg="activity number: {}\nvalue type: {}\npoint_value: {}".format(monday_activity.activity_number,
                                                                                           monday_activity.value_type,
                                                                                           monday_activity.point_value))

    def test_get_daily_activity(self):
        """this test is designed to ensure that the same activity wont show up two days in a row."""
        list_of_dates = [date(2022, 1, 29), date(2022, 1, 30) ,date(2022, 1, 31),  # A monday
                         date(2022, 2, 1), date(2022, 2, 2), date(2022, 2, 3)]
        list_of_activities = [ActivityLookup.get_daily_activity(date_of_interest=day) for day in list_of_dates]
        for i in range(len(list_of_activities) - 1):
            self.assertNotEqual(list_of_activities[i], list_of_activities[i + 1])


class UtilMethodsTestCase(TestCase):
    def setUp(self):
        user_a = User(username="test", email="test@invalid.com")
        user_a.password = "somepassword"
        user_a.save()

        user_b = User(username="test_b", email="test@invalid.com")
        user_b.password = "somepassword"
        user_b.save()

        act_lookup_1 = ActivityLookup()
        act_lookup_1.activity_name = "eat testing"
        act_lookup_1.value_type = 'each'
        act_lookup_1.point_value = 10.0
        act_lookup_1.daily_point_limit = 30
        act_lookup_1.save()

        act_lookup_2 = ActivityLookup()
        act_lookup_2.activity_name = "push testing"
        act_lookup_2.value_type = 'each'
        act_lookup_2.point_value = 1.0
        act_lookup_2.daily_point_limit = 0
        act_lookup_2.save()

        act_lookup_3 = ActivityLookup()
        act_lookup_3.activity_name = "ounce testing"
        act_lookup_3.value_type = 'oz'
        act_lookup_3.point_value = 0.3
        act_lookup_3.daily_point_limit = 30
        act_lookup_3.save()

        act_lookup_4 = ActivityLookup()
        act_lookup_4.activity_name = "daily task testing"
        act_lookup_4.value_type = 'daily_calendar'
        act_lookup_4.point_value = 5.0
        act_lookup_4.daily_point_limit = 5
        act_lookup_4.save()

        act_lookup_5 = ActivityLookup()
        act_lookup_5.activity_name = "Weigh In"
        act_lookup_5.value_type = 'lbs.'
        act_lookup_5.point_value = 5.0
        act_lookup_5.daily_point_limit = 5
        act_lookup_5.save()

        act_lookup_6 = ActivityLookup()
        act_lookup_6.activity_name = "daily task testing 2"
        act_lookup_6.value_type = 'daily_calendar'
        act_lookup_6.point_value = 5.0
        act_lookup_6.daily_point_limit = 5
        act_lookup_6.save()

        prof_a = UserProfile.get_profile(user_a, "test", "A", date(1985, 9, 9))
        prof_a.save()

        prof_b = UserProfile.get_profile(user_b, "test", "B", date(1980, 3, 6))
        prof_b.save()

        for i in range(1, 10):

            act_rec = ActivityRecord()
            act_rec.record_date = date(2022, 1, i)
            act_rec.activity_num = act_lookup_4
            act_rec.user_num = prof_a
            act_rec.number_recorded = i
            act_rec.points = i
            act_rec.save()

            if i%3 != 0:
                act_rec = ActivityRecord()
                act_rec.record_date = date(2022, 1, i)
                act_rec.activity_num = act_lookup_6
                act_rec.user_num = prof_b
                act_rec.number_recorded = i
                act_rec.points = i * 2
                act_rec.save()

    def test_get_points(self):
        prof_a = UserProfile.objects.get(last_name="A")
        points = get_points(prof_a)
        self.assertEqual(points, 55)


    def test_get_points_leaders(self):
        leader_list = get_point_leaders()
        self.assertEqual(len(leader_list), 2)





