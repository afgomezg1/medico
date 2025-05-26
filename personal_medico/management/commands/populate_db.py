from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from personal_medico.models import Doctor, Assignment
import random

# Parámetros configurables manualmente
NUM_DOCTORS = 100                 # Número de doctores a crear
ASSIGNMENTS_PER_DOCTOR = 150     # Número de asignaciones por médico
MONTHS_SPAN = 12                 # Rango en meses para las fechas de assigned_at

class Command(BaseCommand):
    help = 'Popula la base de datos con datos de prueba usando Faker'

    def handle(self, *args, **options):
        fake = Faker()

        self.stdout.write(self.style.NOTICE(f'Creando {NUM_DOCTORS} doctores...'))
        doctors = [
            Doctor(name=fake.name(), city=fake.city())
            for _ in range(NUM_DOCTORS)
        ]
        Doctor.objects.bulk_create(doctors)
        created_doctors = list(Doctor.objects.all())

        total_assignments = NUM_DOCTORS * ASSIGNMENTS_PER_DOCTOR
        self.stdout.write(self.style.NOTICE(
            f'Creando {total_assignments} asignaciones...' +
            f'({ASSIGNMENTS_PER_DOCTOR} por médico)'
        ))

        assignments = []
        now = timezone.now()
        for doctor in created_doctors:
            for _ in range(ASSIGNMENTS_PER_DOCTOR):
                # Fecha aleatoria dentro de MONTHS_SPAN
                days_offset = random.randint(0, MONTHS_SPAN * 30)
                assigned_at = now - timezone.timedelta(
                    days=days_offset,
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59)
                )
                assignments.append(
                    Assignment(
                        doctor=doctor,
                        patient_id=fake.uuid4(),
                        assigned_at=assigned_at
                    )
                )
        Assignment.objects.bulk_create(assignments)

        self.stdout.write(self.style.SUCCESS(
            f'Insertados {NUM_DOCTORS} doctores y {len(assignments)} asignaciones.'
        ))
