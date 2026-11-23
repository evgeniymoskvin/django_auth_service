from django import forms


class ADLoginForm(forms.Form):
    username = forms.CharField(
        label="Доменный логин",
        max_length=150,
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
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
                "class": "form-control",
                'id': 'floatingPassword',
                'placeholder': 'Пароль'}),
    )

