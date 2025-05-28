from django.urls import path

from .views import health_check, assignment_list

urlpatterns = [
    path('internal/assignments/',  assignment_list, name='assignment_list'),
    path('health/', health_check, name='health_check'),
]
