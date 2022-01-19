from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta

from .models import ActivityLookup, ActivityRecord, UserProfile

# Create your tests here.


class UserTestCase(TestCase):

    def setUp(self):
        user_a = User(username="test", email="test@invalid.com")
        user_a.password = "somepassword"
        user_a.save()

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
