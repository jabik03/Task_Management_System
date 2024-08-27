from django.contrib import admin

from tasksystem.models import Task

# Register your models here.

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass
