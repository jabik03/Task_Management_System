from django import template

register = template.Library()


@register.filter
def can_delete_task(task, user):
    if not user.is_authenticated:
        return False
    if user.role == "admin":
        return True
    if user.role == "manager" and task.author == user:
        return True
    return False
