from django.shortcuts import render, redirect
from django.contrib import messages


def home(request):
    """
    Landing page view for the EODB portal
    """
    return render(request, "home/index_fixed.html")


def test_messages(request):
    """
    Test view to demonstrate different types of messages
    """
    messages.success(request, "Success message: Operation completed successfully!")
    messages.error(request, "Error message: Something went wrong.")
    messages.warning(request, "Warning message: Please check your input.")
    messages.info(request, "Info message: Your account has been updated.")

    # Redirect to home page to display the messages
    return redirect("home")


def test_toast(request):
    """
    Test page for toast notifications
    """
    return render(request, "test_toast.html")
