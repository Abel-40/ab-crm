from django.contrib import admin
from .models import TaskSubmission, SubTaskSubmission, ManualReview, DepartmentRank, EmployeeRank

@admin.register(TaskSubmission)
class TaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'submitted_by', 'submission_time', 'status', 'system_score')
    list_filter = ('status', 'task')
    search_fields = ('submitted_by__username', 'task__title')

@admin.register(SubTaskSubmission)
class SubTaskSubmissionAdmin(admin.ModelAdmin):
    list_display = ('subtask', 'submitted_by', 'submission_time', 'status', 'system_score')
    list_filter = ('status', 'subtask')
    search_fields = ('submitted_by__username', 'subtask__title')

@admin.register(ManualReview)
class ManualReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'review_employee', 'review_department', 'review_type', 'score', 'weight')
    list_filter = ('review_type', 'review_department')
    search_fields = ('reviewer__username', 'review_employee__username')

@admin.register(DepartmentRank)
class DepartmentRankAdmin(admin.ModelAdmin):
    list_display = ('department', 'system_score', 'manual_score', 'overall_score')
    search_fields = ('department__name',)

@admin.register(EmployeeRank)
class EmployeeRankAdmin(admin.ModelAdmin):
    list_display = ('employee', 'system_score', 'manual_score', 'overall_score')
    search_fields = ('employee__username',)
