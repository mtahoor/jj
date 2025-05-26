from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages

class DashboardAccessMiddleware:
    """
    Middleware to restrict access to dashboard URLs for unauthenticated users
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the current URL path
        path = request.path_info.lstrip('/')
        
        # Check if the URL is in the dashboard app
        if path.startswith('dashboard/'):
            # If user is not authenticated, redirect to login
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access the dashboard.")
                return redirect('accounts:login')
            
            # If URL is admin dashboard and user is not staff, redirect to user dashboard
            if path.startswith('dashboard/admin/') and not request.user.is_staff:
                messages.warning(request, "You don't have permission to access the admin dashboard.")
                return redirect('dashboard:home')
        
        response = self.get_response(request)
        return response
