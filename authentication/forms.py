from cProfile import label
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
)
from django.contrib.auth import get_user_model
from django.forms import widgets

from re import match as re__match


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
                "class": "custom-input",
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "Логин",
            }
        )
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "custom-input",
                "autocomplete": "current-password",
                "placeholder": "Минимум 8 символов",
            }
        ),
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "password"]


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(
            attrs={
                "class": "custom-input",
                "autocomplete": "username",
                "autofocus": True,
                "placeholder": "Логин",
            }
        ),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "custom-input",
                "autocomplete": "current-password",
                "placeholder": "Придумайте пароль",
            }
        ),
    )
    password2 = forms.CharField(
        label="Повтор пароля",
        widget=forms.PasswordInput(
            attrs={
                "class": "custom-input",
                "autocomplete": "current-password",
                "placeholder": "Повторите пароль",
            }
        ),
    )

    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]

        labels = {"email": "Email", "first_name": "Имя", "last_name": "Фамилия"}
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "class": "custom-input",
                    "placeholder": "E-mail",
                    "required": True,
                }
            ),
            "first_name": forms.TextInput(
                attrs={"class": "custom-input", "placeholder": "Имя", "required": True}
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "custom-input",
                    "placeholder": "Фамилия",
                    "required": True,
                }
            ),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError("Такой E-mail уже существует!")
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        if not re__match(r"^[A-Za-z][A-Za-z0-9._]*[A-Za-z]$", username):
            raise forms.ValidationError(
                "Имя пользователя должно начинаться и заканчиваться только буквой, и содержать только английские буквы, цифры, точки и подчеркивания."
            )
        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        # if not re__match(r"^[A-Za-z][A-Za-z0-9._!@#?]*[A-Za-z]$", password):
        if not re__match(r"^[A-Za-z0-9._!@#?+-]+$", password):
            raise forms.ValidationError(
                "Пароль должен состоять только из английских букв, цифр и специальных символов (+, -, _, !, @, #, ?, .)"
            )
        return password


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(
        disabled=True,
        label="Логин",
        widget=forms.TextInput(attrs={"class": "custom-input"}),
    )
    email = forms.CharField(
        disabled=True,
        label="E-mail",
        widget=forms.TextInput(attrs={"class": "custom-input"}),
    )

    class Meta:
        model = get_user_model()
        fields = ["photo", "username", "email", "first_name", "last_name"]
        labels = {"photo": "Фото", "first_name": "Имя", "last_name": "Фамилия"}
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "custom-input"}),
            "last_name": forms.TextInput(attrs={"class": "custom-input"}),
        }


class UserUpdateForm(forms.ModelForm):

    email = forms.EmailField(
        disabled=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "custom-input"}),
    )

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name", "role"]
        labels = {
            "username": "Логин",
            "email": "Email",
            "first_name": "Имя",
            "last_name": "Фамилия",
            "role": "Роль",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "custom-input"}),
            "first_name": forms.TextInput(attrs={"class": "custom-input"}),
            "last_name": forms.TextInput(attrs={"class": "custom-input"}),
            "role": forms.Select(attrs={"class": "custom-input"}),
        }
