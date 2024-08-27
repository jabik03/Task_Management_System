import os
from django.contrib.auth.models import AbstractUser
from django.db import models

from core import settings

# Модель пользователя
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер'
        WORKER = 'worker', 'Исполнитель'
        READER = 'reader', 'Читатель'
    
    role = models.CharField("Роль", 
                            max_length=15, 
                            choices=Role.choices, 
                            default=Role.READER)

    first_name = models.CharField("Имя", max_length=150, blank=True)
    last_name = models.CharField("Фамилия", max_length=150, blank=True)
    
    email = models.EmailField(unique=True)
    photo = models.ImageField("Фото", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def photo_exists(self):
        if self.photo:
            return os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.photo.name))
        return False

    def delete_old_photo(self):
        if self.photo:
            old_photo_path = os.path.join(settings.MEDIA_ROOT, self.photo.name)
            if os.path.isfile(old_photo_path):
                os.remove(old_photo_path)

    def save(self, *args, **kwargs):
        # Проверка, существует ли объект в базе данных (т.е. это обновление)
        if self.pk:
            try:
                old_user = User.objects.get(pk=self.pk)
                if old_user.photo and old_user.photo != self.photo:
                    old_photo_path = os.path.join(
                        settings.MEDIA_ROOT, old_user.photo.name
                    )
                    if os.path.isfile(old_photo_path):
                        os.remove(old_photo_path)
            except User.DoesNotExist:
                pass

        # Устанавливаем новое имя файла
        if self.photo and not self.photo.name.startswith("users/"):
            self.photo.name = f"users/{self.username}_avatar.jpg"

        super(User, self).save(*args, **kwargs)
