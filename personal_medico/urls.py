from django.urls import path

from ANG_DiagnosticAPP.diagnosticapp import views

from.views import health_check

urlpatterns = [
    path('internal/assignments/',  views.assignment_list, name='assignment_list'),
    path('health/', health_check, name='health_check'),
]
