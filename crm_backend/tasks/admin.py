from django.contrib import admin
from .models import Task,SubTask
# Register your models here.


class TaskAdmin(admin.ModelAdmin):
  list_display = ['id','title','department','status','deadline','created_at']
admin.site.register(Task, TaskAdmin)


class SubTaskAdmin(admin.ModelAdmin):
  list_display = ['id','assigned_to','task','title','status','deadline','created_at']
  
admin.site.register(SubTask,SubTaskAdmin)