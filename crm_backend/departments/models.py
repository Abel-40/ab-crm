from django.db import models
class Departement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="departements_created"
    )
    leader = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="departements_led"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
