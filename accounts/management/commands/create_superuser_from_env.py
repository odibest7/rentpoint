import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

User = get_user_model()


class Command(BaseCommand):
    help = "Create or update a Django superuser from environment variables."

    def handle(self, *args, **options):
        username = (os.getenv("DJANGO_SUPERUSER_USERNAME") or "admin").strip() or "admin"
        email = (os.getenv("DJANGO_SUPERUSER_EMAIL") or "admin@example.com").strip() or "admin@example.com"
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD") or "Admin@1234"

        if not password:
            raise CommandError("DJANGO_SUPERUSER_PASSWORD is required.")

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created superuser: username={user.username}, email={user.email}"
                )
            )
            return

        updated = False
        if user.email != email:
            user.email = email
            updated = True
        if not user.is_staff:
            user.is_staff = True
            updated = True
        if not user.is_superuser:
            user.is_superuser = True
            updated = True
        if not user.check_password(password):
            user.set_password(password)
            updated = True

        if updated:
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated superuser: username={user.username}, email={user.email}"
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser already exists and matches the configured environment values: username={user.username}, email={user.email}"
            )
        )
