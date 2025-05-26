from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import Assignment

def internal_assignments(request):
    start = parse_datetime(request.GET["start"])
    end   = parse_datetime(request.GET["end"])
    qs = Assignment.objects.filter(
        assigned_at__gte=start,
        assigned_at__lt=end
    ).select_related("doctor")
    data = [
        {
          "doctor_id": a.doctor.doctor_id,
          "doctor_name": a.doctor.name,
          "city": a.doctor.city,
          "patient_id": a.patient_id
        }
        for a in qs
    ]
    return JsonResponse(data, safe=False)
