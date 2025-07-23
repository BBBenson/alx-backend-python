from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication

class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication class.
    Extend this if you want to add extra logic.
    """
    pass

class CustomSessionAuthentication(SessionAuthentication):
   