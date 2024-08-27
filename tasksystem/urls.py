from django.urls import path
from tasksystem import views


app_name = "tasksystem"

urlpatterns = [
    path("", views.content, name="content"),  # http://127.0.0.1:8000
    path("task_detail/<slug:tasks_slug>/", views.task_detail, name="task_detail"),
    path("required_tasks/", views.required_tasks, name="required_tasks"),
    path("completed_tasks/", views.completed_tasks, name="completed_tasks"),
    path("create_task/", views.create_task, name="create_task"),
    path("update_task/<slug:slug>/", views.TaskUpdateView.as_view(), name="update_task"),
    path("delete_task/<int:pk>/", views.delete_task, name="delete_task"),
    path("claim_task/<int:pk>/", views.claim_task, name="claim_task"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
