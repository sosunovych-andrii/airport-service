from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from user.serializers import UserSerializer


User = get_user_model()


class CreateUserView(generics.CreateAPIView):
    """
    Create a new user account.
    Accessible without authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the authenticated user's profile.
    Only accessible to authenticated users.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return self.request.user
