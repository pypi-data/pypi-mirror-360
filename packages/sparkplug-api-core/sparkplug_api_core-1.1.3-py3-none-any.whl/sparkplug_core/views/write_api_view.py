from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework.views import APIView


@method_decorator(csrf_protect, name="dispatch")
class WriteAPIView(APIView):
    """
    A base APIView that enforces CSRF protection for state-changing methods.

    Use this for views that handle write operations like POST, PATCH, PUT,
    and DELETE.
    """
