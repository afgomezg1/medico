import requests
from django.conf import settings

# Define una función que tome start_window, period_end y devuelva la lista de asignaciones
def fetch_assignments(start_iso: str, end_iso: str):
    url = settings.PATH_API_GATEWAY + "/personal-medico/internal/assignments/"
    resp = requests.get(url, params={"start": start_iso, "end": end_iso})
    resp.raise_for_status()
    return resp.json()  # [{doctor_id, doctor_name, city, patient_id}, ...]
