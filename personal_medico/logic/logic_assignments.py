from django.utils.dateparse import parse_datetime
from ..models import Assignment

def get_assignments(start=None, end=None):
    qs = Assignment.objects.select_related('doctor')
    if start:
        qs = qs.filter(assigned_at__gte=parse_datetime(start))
    if end:
        qs = qs.filter(assigned_at__lt =parse_datetime(end))
    return qs
