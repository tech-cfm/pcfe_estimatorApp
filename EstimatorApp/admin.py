from django.contrib import admin

# Register your models here.
from .models import Profile
# Adding profiles to the admin site
admin.site.register(Profile)
