from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import ADLoginForm
from identity.ad_auth import authenticate_ad_user
from django.utils.http import url_has_allowed_host_and_scheme

def ad_login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "GET":
        request.session["ad_login_next"] = request.GET.get("next", "/")

    if request.method == "POST":
        form = ADLoginForm(request.POST)

        if form.is_valid():
            user = authenticate_ad_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )

            if user is not None:
                login(request, user)

                next_url = request.session.pop("ad_login_next", "/")

                if not url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    next_url = "/"

                return redirect(next_url)

            form.add_error(
                None,
                "Не удалось выполнить вход. Проверьте логин и пароль или обратитесь к администратору.",
            )
    else:
        form = ADLoginForm()

    return render(
        request,
        "accounts/ad_login.html",
        {"form": form},
    )