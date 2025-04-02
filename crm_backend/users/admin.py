from django.contrib import admin
from .models import User,UserProfile
# Register your models here.
class UserAdminPage(admin.ModelAdmin):
  list_display=('id','email','username')
admin.site.register(User,UserAdminPage)

class UserProfileAdminPage(admin.ModelAdmin):
  list_display = ('user','role','department')
admin.site.register(UserProfile,UserProfileAdminPage)