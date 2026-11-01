from django import forms


class ADLoginForm(forms.Form):
    username = forms.CharField(
        label="Доменный логин",
        max_length=150,
    )

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput,
    )