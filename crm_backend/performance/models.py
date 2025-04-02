from django.db import models
from tasks.models import Task, SubTask
from django.contrib.auth import get_user_model
from users.models import UserProfile
from departments.models import Departement
from django.db.models import Avg, Sum, F
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class TaskSubmission(models.Model):
    class STATUS(models.TextChoices):
        ON_TIME = 'On Time', 'On Time'
        LATE = 'Late', 'Late'
        
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    submission_time = models.DateTimeField(auto_now=True)
    progress = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS.choices, blank=True)
    system_score = models.IntegerField(default=0)


    def save(self, *args, **kwargs):
        submission_count = TaskSubmission.objects.filter(task=self.task, submitted_by=self.submitted_by).count()
        if submission_count >= 3:
            raise ValueError("You have already submitted this task 3 times.")

        if not self.pk:
            self.submission_time = timezone.now()

        if self.submission_time and self.task.deadline:
            total_time = (self.task.deadline - self.task.created_at).total_seconds()
            time_elapsed = (self.submission_time - self.task.created_at).total_seconds()
            time_remaining = (self.task.deadline - self.submission_time).total_seconds()

            if total_time > 0:
                time_used_percentage = time_elapsed / total_time
                time_remaining_percentage = time_remaining / total_time
            else:
                time_used_percentage = 1  
                time_remaining_percentage = 0  

            print(f"Total Time: {total_time} seconds")
            print(f"Time Used Percentage: {time_used_percentage}")
            print(f"Time Remaining Percentage: {time_remaining_percentage}")

            if self.submission_time <= self.task.deadline:
                self.status = TaskSubmission.STATUS.ON_TIME

                if time_used_percentage <= 0.1:  # Submitted in first 10% of time
                    self.system_score = 100
                elif time_used_percentage <= 0.5:  # Submitted between 10% - 50% of time
                    self.system_score = 90
                elif time_used_percentage <= 0.9:  # Submitted between 50% - 90% of time
                    self.system_score = 80
                else:  # Submitted close to the deadline
                    self.system_score = 70

            else:  # If submission is late
                self.status = TaskSubmission.STATUS.LATE
                time_late_percentage = abs(time_remaining_percentage)

                if time_late_percentage <= 0.1:  # Slightly late
                    self.system_score = 40
                elif time_late_percentage <= 0.2:
                    self.system_score = 30
                elif time_late_percentage <= 0.3:
                    self.system_score = 20
                else:
                    self.system_score = 10  # Very late submission

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Submission by {self.submitted_by.username} for {self.task.title}"


class SubTaskSubmission(models.Model):
    class STATUS(models.TextChoices):
        ON_TIME = 'On Time', 'On Time'
        LATE = 'Late', 'Late'

    subtask = models.ForeignKey(SubTask, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subtask_submissions')
    submission_time = models.DateTimeField(auto_now=True)
    progress = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS.choices, blank=True)
    system_score = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        submission_count = SubTaskSubmission.objects.filter(subtask=self.subtask, submitted_by=self.submitted_by).count()
        if submission_count >= 3:
            raise ValueError("You have already submitted this subtask 3 times.")

        if not self.pk:
            self.submission_time = timezone.now()

        if self.submission_time and self.subtask.deadline:
            total_time = (self.subtask.deadline - self.subtask.created_at).total_seconds()
            time_elapsed = (self.submission_time - self.subtask.created_at).total_seconds()
            time_remaining = (self.subtask.deadline - self.submission_time).total_seconds()

            if total_time > 0:
                time_used_percentage = time_elapsed / total_time
                time_remaining_percentage = time_remaining / total_time
            else:
                time_used_percentage = 1  # If total time is zero, assume full usage
                time_remaining_percentage = 0

            if self.submission_time <= self.subtask.deadline:
                self.status = SubTaskSubmission.STATUS.ON_TIME

                if time_used_percentage <= 0.1:  # First 10% of the time
                    self.system_score = 100
                elif time_used_percentage <= 0.5:  # 10% - 50% of the time
                    self.system_score = 90
                elif time_used_percentage <= 0.9:  # 50% - 90% of the time
                    self.system_score = 80
                else:  # Last 10% of the time
                    self.system_score = 70
            else:
                self.status = SubTaskSubmission.STATUS.LATE
                time_late_percentage = abs(time_remaining_percentage)

                if time_late_percentage <= 0.1:
                    self.system_score = 40
                elif time_late_percentage <= 0.2:
                    self.system_score = 30
                elif time_late_percentage <= 0.3:
                    self.system_score = 20
                else:
                    self.system_score = 10

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Submission by {self.submitted_by.username} for {self.subtask.title}"

      
class ManualReview(models.Model):
    class REVIEW_TYPE(models.TextChoices):
        COMPLAINT = 'Complaint', 'Complaint'
        SATISFACTION = 'Satisfaction', 'Satisfaction'

    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_reviews')
    review_employee = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_reviews')
    review_department = models.ForeignKey(to=Departement, on_delete=models.SET_NULL, null=True, blank=True, related_name='department_reviews')
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPE.choices)
    score = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    weight = models.IntegerField()


    def save(self, *args, **kwargs):
        if self.reviewer.userprofile.role == UserProfile.Role.DEPARTMENT_LEADER:
            self.weight = 3
        elif self.reviewer.userprofile.role == UserProfile.Role.DEPARTMENT_MEMBER:
            self.weight = 1
        else:
            self.weight = 2 
        
        if self.review_type == ManualReview.REVIEW_TYPE.COMPLAINT:
            self.score = max(0, self.score - 10)  
        elif self.review_type == ManualReview.REVIEW_TYPE.SATISFACTION:
            self.score = min(100, self.score + 10)  
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Review by {self.reviewer.username} - Score: {self.score}"


class DepartmentRank(models.Model):
    department = models.OneToOneField(to=Departement, on_delete=models.CASCADE, related_name='rank')
    system_score = models.FloatField(default=0)
    manual_score = models.FloatField(default=0)
    overall_score = models.FloatField(default=0)

    def calculate_scores(self):
        self.system_score = TaskSubmission.objects.filter(task__department=self.department).aggregate(
            avg_score=Avg('system_score')
        )['avg_score'] or 0

        review_data = ManualReview.objects.filter(review_department=self.department).aggregate(
            total_weighted_score=Sum(F('score') * F('weight')),
            total_weight=Sum('weight')
        )

        total_weighted_score = review_data['total_weighted_score'] or 0
        total_weight = review_data['total_weight'] or 1  
        self.manual_score = total_weighted_score / total_weight if total_weight > 0 else 0

        self.overall_score = (self.system_score * 0.5) + (self.manual_score * 0.5)
        self.save()

    def __str__(self):
        return f"Rank for {self.department.name} - Score: {self.overall_score:.2f}"

      
class EmployeeRank(models.Model):
  employee = models.OneToOneField(to=User,on_delete=models.CASCADE,related_name='employee_rank')
  system_score = models.FloatField(default=0)
  manual_score = models.FloatField(default=0)
  overall_score = models.FloatField(default=0)
  
  def calculate_scores(self):
    self.system_score = SubTaskSubmission.objects.filter(submitted_by=self.employee).aggregate(avg_score=Avg('system_score'))['avg_score'] or 0

    review_data = ManualReview.objects.filter(review_employee=self.employee).aggregate(
            total_weighted_score=Sum(F('score') * F('weight')),
            total_weight=Sum('weight')
        )

    total_weighted_score = review_data['total_weighted_score'] or 0
    total_weight = review_data['total_weight'] or 1  
    self.manual_score = total_weighted_score / total_weight
    self.overall_score = (self.system_score * 0.5) + (self.manual_score * 0.5)
    
    self.save()