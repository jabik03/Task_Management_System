from django import forms
from django.contrib.auth import get_user_model
from tasksystem.models import Task


User = get_user_model()

class TaskForm(forms.ModelForm):

    class Meta:
        model = Task
        fields = ["title", "description", "worker"]
        labels = {
            'title': 'Заголовок',
            'description': 'Описание',
            'worker': 'Исполнитель',
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'custom-input'}),
            'description': forms.Textarea(attrs={'class': 'custom-input', 'rows': 10, "style": "resize: none; overflow: auto;"}),
            'worker': forms.Select(attrs={'class': 'custom-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["worker"].queryset = User.objects.filter(role=User.Role.WORKER)
