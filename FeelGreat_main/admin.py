from django.contrib import admin

# Register your models here.
from .models import UserProfile, ActivityLookup, ActivityRecord

admin.site.register(UserProfile)
admin.site.register(ActivityLookup)
admin.site.register(ActivityRecord)
