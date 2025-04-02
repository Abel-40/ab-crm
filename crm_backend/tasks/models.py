from django.db import models, transaction
from django.contrib.auth import get_user_model

User = get_user_model()

class Task(models.Model):
    class STATUS(models.TextChoices):
        PENDING = 'PN', 'Pending'
        IN_PROGRESS = 'IN_P', 'In Progress'
        COMPLETED = 'CM', 'Completed'

    title = models.CharField(unique=True,max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.PENDING)
    department = models.ForeignKey('departments.Departement', on_delete=models.CASCADE, related_name='tasks')
    assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.department.name}"


class SubTask(models.Model):
    class STATUS(models.TextChoices):
        PENDING = 'PN', 'Pending'
        IN_PROGRESS = 'IN_P', 'In Progress'
        COMPLETED = 'CM', 'Completed'
    class TYPE(models.TextChoices):
        MANDATORY = 'Mandatory', 'Mandatory'
        OPTIONAL = 'Optional', 'Optional'
        
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='subtasks',null=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.PENDING)
    subtask_type = models.CharField(max_length=20, choices=TYPE.choices, default=TYPE.MANDATORY)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} - {self.task.title} - {self.assigned_to.email}"
