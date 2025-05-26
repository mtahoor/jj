from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from .models import Profile
from .forms import UserUpdateForm, ProfileUpdateForm


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                # Ensure user has a profile
                try:
                    profile = user.profile
                except Profile.DoesNotExist:
                    # Create profile if it doesn't exist
                    Profile.objects.create(user=user)

                login(request, user)
                messages.success(
                    request,
                    f"Welcome back, {user.first_name if user.first_name else username}!",
                )
                # Redirect to appropriate dashboard based on user role
                if user.is_staff:
                    return redirect("dashboard:admin")
                else:
                    return redirect("dashboard:home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def signup_view(request):
    if request.method == "POST":
        # Get form data
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Validate form data
        if password1 != password2:
            messages.error(request, "Passwords don't match.")
            return render(request, "accounts/signup.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return render(request, "accounts/signup.html")

        # Create user
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                )
                # Create profile for the user
                Profile.objects.create(user=user)

                login(request, user)
                messages.success(request, f"Welcome to EODB Portal, {first_name}!")
                return redirect("dashboard:home")
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")

    return render(request, "accounts/signup.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


@login_required
def profile_view(request):
    # Get or create profile for the user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("accounts:profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {"user_form": user_form, "profile_form": profile_form, "profile": profile}
    return render(request, "accounts/profile.html", context)


@login_required
def applications_view(request):
    # Redirect admin users to the admin dashboard
    if request.user.is_staff:
        return redirect("dashboard:admin")

    applications = request.user.applications.all().order_by("-last_updated")
    return render(request, "accounts/applications.html", {"applications": applications})
