from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class UsernameOrEmailBackend(ModelBackend):
    """Authenticate users by username or email."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        identifier = username or kwargs.get(UserModel.USERNAME_FIELD)
        if not identifier or not password:
            return None

        user = (
            UserModel.objects.filter(username__iexact=identifier).first()
            or UserModel.objects.filter(email__iexact=identifier).first()
        )
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
