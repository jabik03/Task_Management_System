from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Case, IntegerField, When
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from authentication.decorators import role_required
from authentication.forms import LoginUserForm, ProfileUserForm, RegisterUserForm, UserUpdateForm

from tasksystem.utils import get_menu

# Create your views here.


class LoginUserView(LoginView):
    template_name = "authentication/login.html"
    form_class = LoginUserForm
    success_url = reverse_lazy("content")


class RegisterUserView(CreateView):
    form_class = RegisterUserForm
    template_name = "authentication/register.html"
    success_url = reverse_lazy("authentication:login")


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = "authentication/profile.html"
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "TMS | Личный кабинет"
        context["page_name"] = "Личный кабинет"
        context["menu"] = get_menu(self.request.user)  # Добавляем меню в контекст
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        if 'photo' in form.cleaned_data and form.cleaned_data['photo']:
            user.photo.name = f'{user.username}_avatar.jpg'
        user.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("authentication:profile")

    def get_object(self, queryset=None):
        return self.request.user


@method_decorator([login_required, role_required(allowed_roles=["admin"])], name="dispatch")
class UserListView(ListView):
    model = get_user_model()
    template_name = "authentication/user_list.html"
    context_object_name = "users"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "TMS | Пользователи"
        context["menu"] = get_menu(self.request.user)  # Добавляем меню в контекст
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.annotate(
            role_priority=Case(
                When(role=get_user_model().Role.ADMIN, then=1),
                When(role=get_user_model().Role.MANAGER, then=2),
                When(role=get_user_model().Role.WORKER, then=3),
                When(role=get_user_model().Role.READER, then=4),
                output_field=IntegerField(),
            )
        ).order_by("role_priority")
        return queryset


# Представление для редактирования пользователя
@method_decorator([login_required, role_required(allowed_roles=["admin"])], name="dispatch")
class UserUpdateView(UpdateView):
    model = get_user_model()
    form_class = UserUpdateForm
    template_name = 'authentication/user_update.html'
    success_url = reverse_lazy('authentication:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "TMS | Личный кабинет"
        context["page_name"] = "Личный кабинет"
        context["menu"] = get_menu(self.request.user)  # Добавляем меню в контекст
        return context

    def form_valid(self, form):
        # Дополнительная логика при сохранении формы, если необходимо
        return super().form_valid(form)


@method_decorator([login_required, role_required(allowed_roles=['admin'])], name='dispatch')
class UserDeleteView(DeleteView):
    model = get_user_model()
    template_name = 'authentication/user_confirm_delete.html'
    success_url = reverse_lazy('authentication:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "TMS | Удаление пользователя"
        context["menu"] = get_menu(self.request.user)  # Добавляем меню в контекст
        return context
