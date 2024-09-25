from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = 'Create admin user'

    def handle(self, *args, **kwargs):

        username = 'eunice'
        email = 'eunice@example.com'
        password = 'eunice'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f"admin '{username}' already exists."))
        else:
            User.objects.create_superuser(
                username=username, email=email, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"admin '{username}' created successfully.")
            )
