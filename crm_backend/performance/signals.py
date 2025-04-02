from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TaskSubmission, ManualReview, DepartmentRank,SubTaskSubmission,EmployeeRank

@receiver(post_save, sender=TaskSubmission)
def create_or_update_department_rank(sender, instance, **kwargs):
    """Create or update DepartmentRank automatically when a TaskSubmission is created or updated."""
    if instance.task and instance.task.department:
        department, _ = DepartmentRank.objects.get_or_create(department=instance.task.department)
        department.calculate_scores()

@receiver(post_save, sender=ManualReview)
def update_department_rank_on_review(sender, instance, **kwargs):
    """Update DepartmentRank when a ManualReview is created or updated."""
    if instance.review_department:
        department, _ = DepartmentRank.objects.get_or_create(department=instance.review_department)
        department.calculate_scores()

@receiver(post_delete, sender=TaskSubmission)
def update_department_rank_on_task_deletion(sender, instance, **kwargs):
    """Update DepartmentRank when a TaskSubmission is deleted."""
    if instance.task and instance.task.department:
        department_rank = DepartmentRank.objects.filter(department=instance.task.department).first()
        if department_rank:
            remaining_submissions = TaskSubmission.objects.filter(task__department=instance.task.department).exists()
            if remaining_submissions:
                department_rank.calculate_scores()
            else:
                department_rank.system_score = 0
                department_rank.overall_score = department_rank.manual_score * 0.5
                department_rank.save()

@receiver(post_delete, sender=ManualReview)
def update_department_rank_on_review_deletion(sender, instance, **kwargs):
    """Update DepartmentRank when a ManualReview is deleted."""
    if instance.review_department:
        department_rank = DepartmentRank.objects.filter(department=instance.review_department).first()
        if department_rank:
            remaining_reviews = ManualReview.objects.filter(review_department=instance.review_department).exists()
            if remaining_reviews:
                department_rank.calculate_scores()
            else:
                department_rank.manual_score = 0
                department_rank.overall_score = department_rank.system_score * 0.5
                department_rank.save()

@receiver(post_save, sender=SubTaskSubmission)
def create_or_update_employee_rank(sender, instance, **kwargs):
    """Create or update EmployeeRank automatically when a SubTaskSubmission is created or updated."""
    if instance.submitted_by:
        employee, _ = EmployeeRank.objects.get_or_create(employee=instance.submitted_by)
        employee.calculate_scores()

@receiver(post_save, sender=ManualReview)
def update_employee_rank_on_review(sender, instance, **kwargs):
    """Update EmployeeRank when a ManualReview related to an employee is created or updated."""
    if instance.review_employee:
        employee, _ = EmployeeRank.objects.get_or_create(employee=instance.review_employee)
        employee.calculate_scores()

@receiver(post_delete, sender=SubTaskSubmission)
def update_employee_rank_on_submission_deletion(sender, instance, **kwargs):
    """Update EmployeeRank when a SubTaskSubmission is deleted."""
    if instance.submitted_by:
        employee_rank = EmployeeRank.objects.filter(employee=instance.submitted_by).first()
        if employee_rank:
            remaining_submissions = SubTaskSubmission.objects.filter(submitted_by=instance.submitted_by).exists()
            if remaining_submissions:
                employee_rank.calculate_scores()
            else:
                employee_rank.system_score = 0
                employee_rank.overall_score = employee_rank.manual_score * 0.5
                employee_rank.save()

@receiver(post_delete, sender=ManualReview)
def update_employee_rank_on_review_deletion(sender, instance, **kwargs):
    """Update EmployeeRank when a ManualReview related to an employee is deleted."""
    if instance.review_employee:
        employee_rank = EmployeeRank.objects.filter(employee=instance.review_employee).first()
        if employee_rank:
            remaining_reviews = ManualReview.objects.filter(review_employee=instance.review_employee).exists()
            if remaining_reviews:
                employee_rank.calculate_scores()
            else:
                employee_rank.manual_score = 0
                employee_rank.overall_score = employee_rank.system_score * 0.5
                employee_rank.save()
