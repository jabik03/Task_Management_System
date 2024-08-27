from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_extensions.db.fields import AutoSlugField

from slugify import slugify


class Task(models.Model):
    class Status(models.TextChoices):
        PENDING = "PD", "Ожидает"
        WORKING = "WK", "В работе"
        COMPLETED = "CP", "Завершена"

    title = models.CharField(max_length=90, verbose_name="Заголовок")
    description = models.TextField("Описание")
    status = models.CharField("Статус", max_length=2, choices=Status.choices, default=Status.PENDING)
    slug = AutoSlugField("Слаг", max_length=200, unique=True, populate_from="title_slug", overwrite=True, db_index=True,)

    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="posts", verbose_name="Автор",)
    worker = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name="worker_tasks",
        verbose_name="Работник",
        blank=True,
        null=True,
        default=None,
    )

    time_create = models.DateTimeField("Время создания", auto_now_add=True)
    time_update = models.DateTimeField("Время изменения", auto_now=True)


    def get_absolute_url(self):
        return reverse("tasksystem:task_detail", kwargs={"tasks_slug": self.slug})
    
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Проверка, что задача создается впервые
            if self.worker:
                self.status = self.Status.WORKING

        if not self.slug:
            self.slug = slugify(f"{self.title}")
        return super().save(*args, **kwargs)


    @property
    def title_slug(self):
        return slugify(f"{self.title}")

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-time_update"]

