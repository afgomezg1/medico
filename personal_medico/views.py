from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from .models import Assignment

from django.http import JsonResponse
from .logic.logic_assignments import get_assignments

def health_check(request):
    return JsonResponse({"status": "ok"})

# El url para llegar acá es: /personal-medico/internal/assignments/?start=2023-10-01T00:00:00&end=2023-10-31T23:59:59
def assignment_list(request):
    start = request.GET.get('start')
    end   = request.GET.get('end')
    qs    = get_assignments(start, end)

    data = [
        {
          "doctor_id":    a.doctor.doctor_id,
          "doctor_name":  a.doctor.name,
          "city":         a.doctor.city,
          "patient_id":   a.patient_id,
          "assigned_at":  a.assigned_at.isoformat()
        }
        for a in qs
    ]
    return JsonResponse(data, safe=False)