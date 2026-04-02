from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib import messages
from ..forms import RegisterForm, UserInfoForm, UserProfileForm
from ..models import UserProfile
from ..services.email_service import send_password_changed_email


class PasswordResetConfirmWithEmail(PasswordResetConfirmView):
    template_name = 'flights/password_reset_confirm.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.user
        if user.email:
            send_password_changed_email(user.email, user.username)
        return response


def register(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_staff = False
        user.save()
        login(request, user)
        return redirect("home")
    return render(request, "flights/register.html", {"form": form})


def custom_logout(request):
    logout(request)
    return redirect("home")


@login_required
def profile(request):
    user = request.user
    profile_obj, _ = UserProfile.objects.get_or_create(user=user)

    user_form    = UserInfoForm(instance=user)
    profile_form = UserProfileForm(instance=profile_obj)
    password_form = PasswordChangeForm(user)
    for field in password_form.fields.values():
        field.widget.attrs["class"] = "form-control"

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "info":
            user_form    = UserInfoForm(request.POST, instance=user)
            profile_form = UserProfileForm(request.POST, instance=profile_obj)
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, "Profile updated successfully.")
                return redirect("profile")

        elif action == "password":
            password_form = PasswordChangeForm(user, request.POST)
            for field in password_form.fields.values():
                field.widget.attrs["class"] = "form-control"
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                send_password_changed_email(user.email, user.username)
                messages.success(request, "Password changed successfully.")
                return redirect("profile")

    return render(request, "flights/profile.html", {
        "user_form":     user_form,
        "profile_form":  profile_form,
        "password_form": password_form,
    })
