import os
import django
from decouple import config

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = config("DJANGO_SUPERUSER_USERNAME")
EMAIL = config("DJANGO_SUPERUSER_EMAIL")
PASSWORD = config("DJANGO_SUPERUSER_PASSWORD")

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(email=EMAIL, password=PASSWORD, first_name=USERNAME)
    print("✅ Superuser '{}' created.".format(USERNAME))
else:
    print("ℹ️ Superuser '{}' already exists. Skipping.".format(USERNAME))
