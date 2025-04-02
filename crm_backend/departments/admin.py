from django.contrib import admin
from .models import Departement
# Register your models here.


class DepartmentAdminPage(admin.ModelAdmin):
  list_display = ('id','name','created_by','leader')
admin.site.register(Departement,DepartmentAdminPage)