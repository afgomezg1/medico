# personal_medico/management/commands/populate_db.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from personal_medico.models import Doctor, Assignment
from django.conf import settings
import random, requests, json

NUM_CITIES            = 20
NUM_DOCTORS           = 200
ASSIGNMENTS_MIN       = 50
ASSIGNMENTS_MAX       = 300
MONTHS_SPAN           = 12
DIAGNOSED_PROBABILITY = 0.7
BATCH_SIZE            = 1000  # <=  API’s comfortable limit

class Command(BaseCommand):
    help = 'Populate Postgres and Mongo with semi-realistic volumes, in batches'

    def handle(self, *args, **options):
        fake = Faker()
        now = timezone.now()

        # 1) Generate unique cities
        Faker.seed(0)
        fake.unique.clear()
        cities = []
        while len(cities) < NUM_CITIES:
            cities.append(fake.unique.city())
        self.stdout.write(self.style.NOTICE(f'Using {NUM_CITIES} unique cities.'))

        # 2) Create doctors
        doctors = [
            Doctor(name=fake.name(), city=random.choice(cities))
            for _ in range(NUM_DOCTORS)
        ]
        Doctor.objects.bulk_create(doctors)
        doctors = list(Doctor.objects.all())
        self.stdout.write(self.style.SUCCESS(f'Created {NUM_DOCTORS} doctors.'))

        # 3) Build assignments + diagnosis payload
        assignments = []
        diag_payload = []
        for doc in doctors:
            for _ in range(random.randint(ASSIGNMENTS_MIN, ASSIGNMENTS_MAX)):
                days_back = random.randint(0, MONTHS_SPAN * 30)
                assigned_at = now - timezone.timedelta(
                    days=days_back,
                    hours=random.randint(0,23),
                    minutes=random.randint(0,59),
                    seconds=random.randint(0,59)
                )
                pid = fake.uuid4()
                assignments.append(Assignment(
                    doctor=doc, patient_id=pid, assigned_at=assigned_at
                ))

                # Decide status
                if random.random() < DIAGNOSED_PROBABILITY:
                    status = "diagnosed"
                    diff = now - assigned_at
                    sec = random.randint(0, int(diff.total_seconds()))
                    diagnosed_at = assigned_at + timezone.timedelta(seconds=sec)
                    refractory = random.choice([True, False])
                else:
                    status = "pending"
                    diagnosed_at = None
                    refractory = None

                entry = {"patient_id": pid, "status": status}
                if diagnosed_at:
                    entry["diagnosed_at"] = diagnosed_at.isoformat()
                if refractory is not None:
                    entry["refractory_epilepsy"] = refractory

                diag_payload.append(entry)

        # 4) Bulk insert assignments in Postgres
        Assignment.objects.bulk_create(assignments)
        total_asgs = len(assignments)
        self.stdout.write(self.style.SUCCESS(
            f'Postgres: created {total_asgs} assignments.'
        ))

        # 5) Chunked POST to Mongo via Kong
        url = settings.PATH_API_GATEWAY + "/historia-clinica/internal/diagnoses/bulk_create/"
        headers = {'Content-Type': 'application/json'}
        inserted_total = 0

        for i in range(0, len(diag_payload), BATCH_SIZE):
            batch = diag_payload[i:i+BATCH_SIZE]
            resp = requests.post(url,
                                 data=json.dumps(batch),
                                 headers=headers,
                                 timeout=300)
            try:
                resp.raise_for_status()
            except requests.HTTPError as e:
                self.stderr.write(f'Batch {i//BATCH_SIZE +1} failed: {resp.status_code} {resp.text}')
                raise
            inserted = resp.json().get("inserted", 0)
            inserted_total += inserted
            self.stdout.write(self.style.SUCCESS(
                f'Batch {i//BATCH_SIZE +1}: inserted {inserted} diagnoses.'
            ))

        self.stdout.write(self.style.SUCCESS(
            f'Total Mongo inserts: {inserted_total} diagnoses.'
        ))
