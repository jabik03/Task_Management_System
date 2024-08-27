from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.db.models import Case, When, IntegerField, Value
from django.db.models.functions import Concat


from authentication.decorators import role_required
from tasksystem.forms import TaskForm
from tasksystem.models import Task
from tasksystem.utils import get_menu, info_for_dashboard


# Функция для отображения всех задач
@login_required
@role_required(allowed_roles=["admin", "manager", "worker", "reader"])
def content(request):
    tasks = Task.objects.exclude(status=Task.Status.COMPLETED).annotate(
    status_order=Case(
        When(status=Task.Status.PENDING, then=0),
        When(status=Task.Status.WORKING, then=1),
        default=2,
        output_field=IntegerField(),
    )
).order_by('status_order', '-time_update',)
    data = {
        "title": "TMS | Все задачи",
        "page_name": "Все задачи",
        "menu": get_menu(request.user),
        "tasks": tasks,
    }
    return render(request, "tasksystem/content.html", context=data)


@login_required
@role_required(allowed_roles=["admin", "manager"])
def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.user.role == "admin" or (
        request.user.role == "manager" and task.author == request.user
    ):
        task.delete()
        messages.success(request, "Задача успешно удалена.")
    else:
        messages.error(request, "У вас нет прав для удаления этой задачи.")

    previous_url = request.META.get('HTTP_REFERER', 'tasksystem:content')
    return redirect(previous_url)


def claim_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.worker is None and request.user.role == request.user.Role.WORKER and task.status == Task.Status.PENDING:
        task.worker = request.user
        task.status = Task.Status.WORKING
        task.save()
        messages.success(request, "Задача успешно взята.")
    else:
        messages.error(request, "Задача уже взята.")

    previous_url = request.META.get('HTTP_REFERER', 'tasksystem:content')
    return redirect(previous_url)


# Функция для отображения деталей задачи
@login_required
def task_detail(request, tasks_slug):
    task = get_object_or_404(Task, slug=tasks_slug)
    data = {
        "title": "TMS | Подробнее о задаче",
        "page_name": "Подробнее о задаче",
        "menu": get_menu(request.user),
        "task": task,
    }
    return render(request, "tasksystem/task_detail.html", context=data)


# Функция для отображения обязательных задач
@login_required
@role_required(allowed_roles=["admin", "manager", "worker"])
def required_tasks(request):
    if request.method == "POST":
        task_id = request.POST.get("task_id")
        task = get_object_or_404(Task, id=task_id, worker=request.user)
        if task.status == Task.Status.WORKING:
            task.status = Task.Status.COMPLETED
            task.save()
            messages.success(
                request, f"Задача '{task.title}' отмечена как завершенная."
            )
            return redirect("tasksystem:required_tasks")

    tasks = Task.objects.filter(worker=request.user, status=Task.Status.WORKING).order_by(
        'author__first_name', 'author__last_name', '-time_update',
    )
    data = {
        "title": "TMS | Обязательные задачи",
        "page_name": "Обязательные задачи",
        "menu": get_menu(request.user),
        "tasks": tasks,
    }
    return render(request, "tasksystem/required_tasks.html", context=data)


@login_required
@role_required(allowed_roles=["admin", "manager"])
def completed_tasks(request):
    # Фильтруем задачи, которые выполнены и созданы текущим пользователем
    if request.user.role == "admin":
        tasks = Task.objects.filter(
            status=Task.Status.COMPLETED
        ).order_by(
            'author__first_name', 'author__last_name', 'worker__first_name', 'worker__last_name',  '-time_update',
        )
    else:
        tasks = Task.objects.filter(
            author=request.user,
            status=Task.Status.COMPLETED
        ).order_by(
            'author__first_name', 'author__last_name', 'worker__first_name', 'worker__last_name',  '-time_update',
        )
         
    data = {
        "title": "TMS | Готовые задачи",
        "page_name": "Готовые задачи",
        "menu": get_menu(request.user),
        "tasks": tasks,
    }
    return render(request, "tasksystem/completed_tasks.html", context=data)


# Функция для создания задачи, доступная только администраторам и менеджерам
@login_required
@role_required(allowed_roles=["admin", "manager"])
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.author = request.user  # Установка автора задачи
            task.save()
            messages.success(request, "Задача успешно создана.")
            return redirect("tasksystem:content")
    else:
        form = TaskForm()
    return render(
        request,
        "tasksystem/create_task.html",
        {"title" : "TMS | Создание задачи", 
         "form": form, 
         "menu": get_menu(request.user)}
        )


# Представление для редактирования задачи, доступное только администраторам и менеджерам
@method_decorator(
    [login_required, role_required(allowed_roles=["admin", "manager", "executor"])],
    name="dispatch",
)
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "tasksystem/update_task.html"
    context_object_name = "task"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Редактирование задачи"
        context["page_name"] = "Редактирование задачи"
        context["menu"] = get_menu(self.request.user)
        return context

    def form_valid(self, form):
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("tasksystem:task_detail", kwargs={"tasks_slug": self.object.slug})

    def dispatch(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == Task.Status.COMPLETED:
            raise Http404()
        if not request.user.has_perm('tasksystem.change_task'):
            raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)


@login_required
@role_required(allowed_roles=["admin"])
def dashboard(request):
    stats = info_for_dashboard()
    data = {
        "title": "TMS | Дэшборд",
        "page_name": "Дэшборд",
        "menu": get_menu(request.user),
        "stats": stats,
    }
    return render(request, "tasksystem/dashboard.html", context=data)


def page_404(request, exception):
    return render(request, "404.html", status=404)

def page_403(request, exception):
    return render(request, "403.html", status=403)
    