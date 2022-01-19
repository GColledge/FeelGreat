from django.urls import path, include
from django.views.generic.base import TemplateView

from . import views


app_name = 'FeelGreat_main'
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('index/', views.IndexView.as_view(), name='index'),
    path('userrecords/<int:user_id>/', views.users_recent_records, name='users_recent_records'),
    path('makerecord/<int:activity_id>/', views.record_activity, name='record_activity'),
    path('record_daily_activity/', views.record_daily_activity, name='record_daily_activity'),
    # path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
]
