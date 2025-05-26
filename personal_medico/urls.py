from django.urls import path
from .views import internal_assignments

urlpatterns = [
    path("internal/assignments/", internal_assignments, name="internal_assignments")
]
