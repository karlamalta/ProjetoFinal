from django.contrib.auth.models import User
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.tokens import default_token_generator


class Backend( RemoteUserBackend ):
    def authenticate(username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # Create a new user. Note that we can set password
            # to anything, because it won't be checked; the password
            # from settings.py will.
            user = User(username=username, password=UNUSABLE_PASSWORD)
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user
