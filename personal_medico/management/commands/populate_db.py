# personal_medico/management/commands/populate_db.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from personal_medico.models import Doctor, Assignment
from django.conf import settings
import random, requests, json

# Parámetros ajustados para más realismo
NUM_CITIES           = 20
NUM_DOCTORS          = 200
ASSIGNMENTS_MIN      = 50
ASSIGNMENTS_MAX      = 300
MONTHS_SPAN          = 12
DIAGNOSED_PROBABILITY = 0.7  # 70% de las asignaciones se marcan como "diagnosed"

class Command(BaseCommand):
    help = 'Populate Postgres and Mongo with semi-realistic volumes'

    def handle(self, *args, **options):
        fake = Faker()
        now = timezone.now()

        # 1) Generar un pool de ciudades únicas
        Faker.seed(0)
        fake.unique.clear()
        cities = []
        while len(cities) < NUM_CITIES:
            cities.append(fake.unique.city())
        self.stdout.write(self.style.NOTICE(
            f'Using {NUM_CITIES} unique cities for doctor assignments.'
        ))

        # 2) Crear doctores y repartirlos entre esas ciudades
        doctors = []
        for _ in range(NUM_DOCTORS):
            name = fake.name()
            city = random.choice(cities)
            doctors.append(Doctor(name=name, city=city))
        Doctor.objects.bulk_create(doctors)
        doctors = list(Doctor.objects.all())
        self.stdout.write(self.style.SUCCESS(
            f'Postgres: created {NUM_DOCTORS} doctors.'
        ))

        # 3) Crear assignments y payload de diagnósticos
        assignments = []
        diag_payload = []
        for doc in doctors:
            num_asgs = random.randint(ASSIGNMENTS_MIN, ASSIGNMENTS_MAX)
            for _ in range(num_asgs):
                # a) Fecha aleatoria en últimos MONTHS_SPAN meses
                days_back = random.randint(0, MONTHS_SPAN * 30)
                assigned_at = now - timezone.timedelta(
                    days=days_back,
                    hours=random.randint(0,23),
                    minutes=random.randint(0,59),
                    seconds=random.randint(0,59)
                )
                pid = fake.uuid4()

                # b) Crear assignment en Postgres
                assignments.append(Assignment(
                    doctor=doc,
                    patient_id=pid,
                    assigned_at=assigned_at
                ))

                # c) Generar estado de diagnóstico con probabilidad
                if random.random() < DIAGNOSED_PROBABILITY:
                    status = "diagnosed"
                    diff = now - assigned_at
                    rnd_sec = random.randint(0, int(diff.total_seconds()))
                    diagnosed_at = assigned_at + timezone.timedelta(seconds=rnd_sec)
                    refractory = random.choice([True, False])
                else:
                    status = "pending"
                    diagnosed_at = None
                    refractory = None

                d = {"patient_id": pid, "status": status}
                if diagnosed_at:
                    d["diagnosed_at"] = diagnosed_at.isoformat()
                if refractory is not None:
                    d["refractory_epilepsy"] = refractory

                diag_payload.append(d)

        # 4) Bulk insert en Postgres
        Assignment.objects.bulk_create(assignments)
        total_asgs = len(assignments)
        self.stdout.write(self.style.SUCCESS(
            f'Postgres: created {total_asgs} assignments (avg {total_asgs/NUM_DOCTORS:.1f} per doctor).'
        ))

        # 5) Bulk insert en Mongo vía Kong
        url = settings.PATH_API_GATEWAY + "/historia-clinica/internal/diagnoses/bulk_create/"
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url,
                             data=json.dumps(diag_payload),
                             headers=headers,
                             timeout=300)
        resp.raise_for_status()
        inserted = resp.json().get("inserted", 0)
        self.stdout.write(self.style.SUCCESS(
            f'Mongo: inserted {inserted} diagnoses.'
        ))
