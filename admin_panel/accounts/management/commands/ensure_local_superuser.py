from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create local superuser if not exists (for emergency login)"

    def handle(self, *args, **options):
        User = get_user_model()
        username = "localadmin"
        password = "localadmin"
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username,
                                          email="",
                                          password=password)
            self.stdout.write(self.style.SUCCESS
                              ("Created local superuser localadmin/localadmin")
                              )
        else:
            self.stdout.write("Local superuser already exists")
