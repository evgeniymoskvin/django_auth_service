from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm
from django.forms import ModelForm, TextInput, Textarea, CheckboxInput, Select, PasswordInput
from django.contrib.auth.models import User
from django import forms


class LoginForm(AuthenticationForm):
    username = UsernameField(
        label='Логин',
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": "form-control",
                'id': 'floatingInput',
                'placeholder': 'Логин',
                'autocomplete': "username"
            }
        )
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                'id': 'floatingPassword',
                'placeholder': 'Пароль'}),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        from identity.access import is_employee_allowed

        if not is_employee_allowed(user):
            raise forms.ValidationError(
                "Вход запрещён. Учетная запись не найдена в справочнике "
                "сотрудников или сотрудник больше не работает.",
                code="inactive_employee",
        )


class SignUpForm(UserCreationForm):
    username = UsernameField(
        widget=forms.TextInput(
            attrs={"autofocus": True, "class": "form-control", 'id': 'floatingInput', 'placeholder': 'Login'}))
    password1 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "class": "form-control", 'id': 'floatingPassword',
                   'placeholder': 'Password'}))
    password2 = forms.CharField(
        label=("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "class": "form-control", 'id': 'floatingPassword',
                   'placeholder': 'Password'})

    )
    # first_name = forms.py.CharField(max_length=30, required=False)
    # last_name = forms.py.CharField(max_length=30, required=False)
    #
    # class Vena:
    #     model = User
    #     fields = ['username', 'password']
    pass
