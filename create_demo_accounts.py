import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User

# Create admin demo account
try:
    admin_user = User.objects.create_user(
        username='admin@eodb.sc',
        email='admin@eodb.sc',
        password='admin123',
        first_name='Admin',
        last_name='User',
        is_staff=True
    )
    print("Admin demo account created successfully!")
except Exception as e:
    print(f"Error creating admin account: {e}")

# Create regular user demo account
try:
    user = User.objects.create_user(
        username='user@eodb.sc',
        email='user@eodb.sc',
        password='user123',
        first_name='Regular',
        last_name='User'
    )
    print("User demo account created successfully!")
except Exception as e:
    print(f"Error creating user account: {e}")
