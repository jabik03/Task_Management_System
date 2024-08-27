from django.db.models import Q, Count
from django.template.defaultfilters import slugify as django_slugify

from authentication.models import User
from tasksystem.models import Task

alphabet = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "g",
    "д": "d",
    "е": "e",
    "ё": "yo",
    "ж": "zh",
    "з": "z",
    "и": "i",
    "й": "j",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ы": "i",
    "э": "e",
    "ю": "yu",
    "я": "ya",
}


def slugify(s):
    return django_slugify("".join(alphabet.get(w, w) for w in s.lower()))


def get_menu(user):
    # Функция get_menu возвращает список словарей с названием и url-адресом для каждого пункта меню
    if not user.is_anonymous:
        task_statistics = Task.objects.aggregate(
            all_tasks=Count("id", filter=~Q(status=Task.Status.COMPLETED)),
            required_tasks=Count(
                "id", filter=Q(status=Task.Status.WORKING, worker=user)
            ),
            completed_tasks=Count(
                "id",
                filter=Q(status=Task.Status.COMPLETED)
                & (
                    Q(author=user) | Q(status=Task.Status.COMPLETED) & Q(author=user)
                    if not user.is_superuser
                    else Q()
                ),
            ),
        )
    else:
        task_statistics = Task.objects.aggregate(
            all_tasks=Count("id", filter=~Q(status=Task.Status.COMPLETED))
        )

    menu = [
        {
            "title": "Все задачи",
            "url_name": "tasksystem:content",
            "icon": "all_tasks",
            "count": task_statistics["all_tasks"],
        },
    ]

    if user.is_authenticated:
        if user.role == user.Role.ADMIN or user.role == user.Role.MANAGER:
            menu.append(
                {
                    "title": "Готовые задачи",
                    "url_name": "tasksystem:completed_tasks",
                    "icon": "completed_tasks",
                    "count": task_statistics["completed_tasks"],
                }
            )
            menu.append(
                {
                    "title": "Создать задачу",
                    "url_name": "tasksystem:create_task",
                    "icon": "add_task",
                }
            )

        if user.role == user.Role.WORKER:
            menu.append(
                {
                    "title": "Мои задачи",
                    "url_name": "tasksystem:required_tasks",
                    "icon": "mandatory_tasks",
                    "count": task_statistics["required_tasks"],
                }
            )

        if user.role == user.Role.ADMIN:
            menu.append(
                {
                    "title": "Дэшборд",
                    "url_name": "tasksystem:dashboard",
                    "icon": "dashboard",
                }
            )
            menu.append(
                {
                    "title": "Пользователи",
                    "url_name": "authentication:user_list",
                    "icon": "user_control",
                    "count": User.objects.count(),
                }
            )

    return menu


def info_for_dashboard():
    # Считаем общее количество пользователей в системе
    total_users = User.objects.count()
    
    # Считаем общее количество задач в системе
    total_tasks = Task.objects.count()
    
    # Получаем количество пользователей для каждой роли
    role_counts = User.objects.values('role').annotate(count=Count('role'))
    
    # Преобразуем список словарей в словарь с ключами как роли и значениями как количество пользователей этой роли
    role_stats = {role['role']: role['count'] for role in role_counts}
    
    # Находим исполнителя (WORKER), который выполнил больше всего задач
    top_worker = User.objects.filter(role=User.Role.WORKER).annotate(
        completed_tasks=Count('worker_tasks', filter=Q(worker_tasks__status=Task.Status.COMPLETED))
    ).order_by('-completed_tasks').first()

    # Собираем все данные в один список словарей
    stats = [
        {"value": total_users, "label": "Всего пользователей", "icon": "users.png"},
        {"value": total_tasks, "label": "Всего задач", "icon": "tasks.png"},
        {"value": role_stats.get(User.Role.ADMIN, 0), "label": "Администраторы", "icon": "admins.png"},
        {"value": role_stats.get(User.Role.MANAGER, 0), "label": "Менеджеры", "icon": "managers.png"},
        {"value": role_stats.get(User.Role.WORKER, 0), "label": "Исполнители", "icon": "workers.png"},
        {"value": role_stats.get(User.Role.READER, 0), "label": "Читатели", "icon": "readers.png"},
        {
            "value": top_worker.get_full_name() if top_worker else "Нет данных",
            "label": "Лучший исполнитель",
            "icon": "top_worker.png",
            "extra": f"{top_worker.completed_tasks} выполненных задач" if top_worker else None
        },
    ]

    return stats
