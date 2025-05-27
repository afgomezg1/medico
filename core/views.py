from django.shortcuts import render
# core/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt # Para simplificar las pruebas, en producción se gestiona CSRF
def status_check(request):
    """
    Endpoint simple para simular un chequeo de estado.
    """
    if request.method == 'GET':
        return JsonResponse({"status": "ok", "message": "Django Service 1 is running healthy."})
    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)

# Opcional: una vista que simula un "spoofed" status
@csrf_exempt
def spoofed_status(request):
    """
    Endpoint que simula una respuesta "spoofed" (por ejemplo, con datos alterados).
    """
    if request.method == 'GET':
        # Simula una respuesta que podría ser interpretada como spoofed
        # (por ejemplo, un token JWT inválido, un hash incorrecto, etc.)
        return JsonResponse({
            "status": "compromised",
            "message": "Data integrity check failed.",
            "secret_key": "INVALID_KEY_123" # Dato que un detector podría buscar
        }, status=200) # O 403 Forbidden si prefieres
    return JsonResponse({"status": "error", "message": "Method not allowed."}, status=405)