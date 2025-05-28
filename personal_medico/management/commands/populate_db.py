from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from personal_medico.models import Doctor, Assignment
from django.conf import settings
import random, requests, json

NUM_DOCTORS = 20
ASSIGNMENTS_PER_DOCTOR = 150
MONTHS_SPAN = 12

class Command(BaseCommand):
    help = 'Populate Postgres and Mongo (Diagnoses) in one shot'

    def handle(self, *args, **options):
        fake = Faker()
        now = timezone.now()

        # 1) Create doctors
        doctors = [Doctor(name=fake.name(), city=fake.city())
                   for _ in range(NUM_DOCTORS)]
        Doctor.objects.bulk_create(doctors)
        doctors = list(Doctor.objects.all())

        # 2) Build assignments + a payload of Diagnosis dicts
        assignments = []
        diag_payload = []
        for doc in doctors:
            for _ in range(ASSIGNMENTS_PER_DOCTOR):
                # a) random assignment date
                days = random.randint(0, MONTHS_SPAN*30)
                assigned_at = now - timezone.timedelta(
                    days=days,
                    hours=random.randint(0,23),
                    minutes=random.randint(0,59),
                    seconds=random.randint(0,59)
                )
                pid = fake.uuid4()

                # b) schedule assignment in Postgres
                assignments.append(Assignment(
                    doctor=doc,
                    patient_id=pid,
                    assigned_at=assigned_at
                ))

                # c) prepare a full Diagnosis document
                status = random.choice(["pending", "diagnosed"])
                diagnosed_at = None
                refractory = None
                if status == "diagnosed":
                    diff = now - assigned_at
                    rnd = random.randint(0, int(diff.total_seconds()))
                    diagnosed_at = assigned_at + timezone.timedelta(seconds=rnd)
                    refractory = random.choice([True, False])

                d = {
                    "patient_id": pid,
                    "status": status,
                }
                if diagnosed_at:
                    d["diagnosed_at"] = diagnosed_at.isoformat()
                if refractory is not None:
                    d["refractory_epilepsy"] = refractory

                diag_payload.append(d)

        # 3) Bulk insert into Postgres
        Assignment.objects.bulk_create(assignments)
        self.stdout.write(self.style.SUCCESS(
            f'Postgres: {len(doctors)} doctors and {len(assignments)} assignments created.'
        ))

        # 4) Bulk insert into Mongo via Kong
        url = settings.PATH_API_GATEWAY + "/historia_clinica/internal/diagnoses/bulk_create/"
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, data=json.dumps(diag_payload), headers=headers, timeout=180)
        resp.raise_for_status()
        inserted = resp.json().get("inserted", 0)
        self.stdout.write(self.style.SUCCESS(
            f'Mongo: inserted {inserted} diagnoses.'
        ))
