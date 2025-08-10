# messaging_app/chats/auth.py

from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[settings.USER_ID_CLAIM]
        except KeyError:
            raise AuthenticationFailed(
                "Token contained no recognizable user identification"
            )

        try:
            user = self.user_model.objects.get(**{settings.USER_ID_FIELD: user_id})
        except self.user_model.DoesNotExist:
            raise AuthenticationFailed("User not found", code="user_not_found")

        if not user.is_active:
            raise AuthenticationFailed("User is inactive", code="user_inactive")

        return user
