from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template import loader
from django.views import generic

from .models import ActivityLookup, ActivityRecord, UserProfile, UnitsOfMeasure
from .utils import get_plot, convert_to_percent, get_differentials
from django.contrib.auth.models import User, auth
from django.contrib import messages


# Create your views here.
class IndexView(generic.ListView):
    template_name = "FeelGreat_main/index.html"
    context_object_name = 'high_scoring_activities'

    def get_queryset(self):
        """Return All activities"""
        return ActivityLookup.objects.exclude(value_type=UnitsOfMeasure.DAILY_SPECIAL).order_by('-point_value')


def index(request):
    high_scoring_activities = ActivityLookup.objects.exclude(value_type=UnitsOfMeasure.DAILY_SPECIAL).order_by('-point_value')
    weigh_in_activity = ActivityLookup.objects.get(activity_name="Weigh In")
    context = {'high_scoring_activities': high_scoring_activities,
               'weigh_in_activity': weigh_in_activity}
    return render(request, "FeelGreat_main/index.html", context)


def record_activity(request, activity_id):
    if request.method == "POST":
        act = ActivityLookup.objects.get(pk=activity_id)
        value = float(request.POST[act.activity_name])
        points, _ = ActivityRecord.verify_points_input(request, activity_id)
        user = request.user
        if not user.is_authenticated:
            messages.info(request, "Please sign-in or register in order to track activity.")
            return render(request, 'FeelGreat_main/register.html')
        user_prof = UserProfile.objects.filter(user_name=user.username)[0]
        record = ActivityRecord.create(new_points=points, number_recorded=value,
                                       user=user, act_num=activity_id,)
        record.save()
        return users_recent_records(request, user_prof.user_number)
    else:
        try:
            act = ActivityLookup.objects.get(pk=activity_id)
        except ActivityLookup.DoesNotExist:
            raise Http404("Activity does not exist")
        return render(request, 'FeelGreat_main/record_activity.html',
                      {'activity': act})


def users_recent_records(request, user_id):
    try:
        current_user = UserProfile.objects.get(pk=user_id)
    except UserProfile.DoesNotExist:
        raise Http404("That User does not exist. \
                       Contact administrator for more help.")
    users_records = ActivityRecord.objects.filter(user_num=user_id)
    users_records = users_records.order_by('-record_date')
    context = {'current_user': current_user, 'users_records': users_records}
    return render(request, "FeelGreat_main/users_recent_records.html", context)

def progress_summary(request):
    if request.user.is_authenticated:
        weigh_in_act = ActivityLookup.objects.get(activity_name="Weigh In")
        weigh_in_records = ActivityRecord.objects.filter(user_num=request.user.id).filter(activity_num=weigh_in_act.activity_number)
        if len(weigh_in_records) > 1:
            weigh_in_records = weigh_in_records.order_by('record_date')
            print(weigh_in_records)
            x = [x.record_date for x in weigh_in_records]
            y = [y.number_recorded for y in weigh_in_records]
            diffs = get_differentials(y)
            perc = convert_to_percent(y)
            diff_plot = get_plot(x, diffs, plot_title="Change in Weight",
                                 y_label="Weight Change (pounds)")
            percent_plot = get_plot(x, perc, plot_title="Percent Weight Change",
                                    y_label="Percent of original weight")
            context = {'percent_plot': percent_plot, 'diff_plot': diff_plot}
            return render(request, "FeelGreat_main/progress_page.html", context)
        else:
            print("not enough records")
            messages.info(request, "You do not have enough Weigh In activities recorded. \
                                    keep using the app and be sure to weigh in.")
            users_records = ActivityRecord.objects.filter(user_num=request.user.id)
            users_records = users_records.order_by('-record_date')
            context = {'current_user': request.user, 'users_records': users_records}
            return render(request, "FeelGreat_main/users_recent_records.html", context)
    else:
        print("user was not logged in")
        messages.info(request, "You need to log in before \
                                recording and tracking activity.")
        return render(request, "FeelGreat_main/login.html")



def record_daily_activity(request):
    activities = ActivityLookup.objects.exclude(value_type=UnitsOfMeasure.WEEKLY).exclude(value_type=UnitsOfMeasure.POUNDS).exclude(value_type=UnitsOfMeasure.DAILY_SPECIAL)
    daily_act = ActivityLookup.get_daily_activity()
    checklist_activities = activities.filter(value_type=UnitsOfMeasure.DAILY)
    quantity_activities = activities.exclude(value_type=UnitsOfMeasure.DAILY)

    checklist_strings = [a.activity_name for a in checklist_activities]
    quantity_strings = [a.activity_name for a in quantity_activities]

    checklist_stuff = zip(checklist_activities, checklist_strings)
    quantity_stuff = zip(quantity_activities, quantity_strings)

    if request.method == "POST":
        if request.user.is_authenticated:
            user_prof = UserProfile.objects.get(user_number=request.user.id)
            qs_4_dailyact = ActivityLookup.objects.filter(pk=daily_act.activity_number)
            activities = activities.union(qs_4_dailyact)  # append daily act queryset
            for act in activities:
                activity_id = ActivityLookup.objects.get(activity_name=act.activity_name).activity_number
                points, value = ActivityRecord.verify_points_input(request,
                                                                   activity_id)
                if points == 0 and value == 0:
                    continue  # Fields were blank so no record needs to be made
                record = ActivityRecord.create(new_points=points,
                                               number_recorded=value,
                                               user=request.user,
                                               act_num=activity_id,)
                record.save()
            return users_recent_records(request, user_prof.user_number)
        else:
            messages.info(request, "You need to log in before \
                                    recording activity.")
            return render(request, "FeelGreat_main/login.html")
    else:
        if daily_act.activity_name == "Weigh In":
            weigh_in_bool = True
        else:
            weigh_in_bool = False
        context = {'checklist_stuff': checklist_stuff,
                   'quantity_stuff': quantity_stuff,
                   'daily_activity': daily_act,
                   'daily_activity_string': daily_act.activity_name,
                   'weigh_in': weigh_in_bool
                   }
        return render(request, "FeelGreat_main/make_daily_record.html",
                      context)


def leader_board(request):
    if request.method == 'POST':
        pass
    else:
        return render(request, "FeelGreat_main/leader_board.html")

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return render(request, 'home.html')
        else:
            messages.info(request, "Invalid Username or Password")
            return render(request, "FeelGreat_main/login.html")
    else:
        return render(request, "FeelGreat_main/login.html")


def logout(request):
    auth.logout(request)
    return redirect("/FeelGreat_main/login/")


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password']
        password2 = request.POST['password2']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        birthdate = request.POST['birthdate']
        email = request.POST['email']
        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.info(request, "user name already taken.")
                return redirect('/FeelGreat_main/register/')
            else:
                user = User.objects.create_user(username=username,
                                                password=password1,
                                                email=email)
                user_prof = UserProfile.get_profile(user=user,
                                                    firstname=firstname,
                                                    lastname=lastname,
                                                    birthday=birthdate)
                user.save()
                user_prof.save()
                return redirect("/FeelGreat_main/login/")
        else:
            messages.info(request, "passwords do not match")
            return redirect('/FeelGreat_main/register/')
    else:
        return render(request, 'FeelGreat_main/register.html')
