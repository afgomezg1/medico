from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    """
    Representa un médico con su ciudad de trabajo.
    """
    doctor_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)

    class Meta:
        db_table = 'doctors'
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctores'

    def __str__(self):
        return f"{self.name} ({self.city})"


class Assignment(models.Model):
    """
    Registra la asignación de un paciente a un médico en un momento dado.
    """
    assignment_id = models.AutoField(primary_key=True)
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    patient_id = models.CharField(
        max_length=36,
        help_text='Identificador del paciente (puede ser UUID o cadena)'
    )
    assigned_at = models.DateTimeField(
        default=timezone.now,
        help_text='Fecha y hora en que se asignó el paciente al médico'
    )

    class Meta:
        db_table = 'patient_assignments'
        verbose_name = 'Asignación de paciente'
        verbose_name_plural = 'Asignaciones de pacientes'
        indexes = [
            models.Index(fields=['assigned_at']),
            models.Index(fields=['doctor', 'assigned_at']),
        ]

    def __str__(self):
        return f"Asignación {self.assignment_id}: paciente {self.patient_id} -> médico {self.doctor_id} en {self.assigned_at}"
