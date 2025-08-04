# bookings/management/commands/populate_db.py

import random
import datetime

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from doctors.models import (
    Doctor, Department, DoctorAvailability,
    MedicalNote as DoctorNote
)
from patients.models import Patient, Insurance, MedicalRecord
from bookings.models import Appointment, MedicalNote as BookingNote


class Command(BaseCommand):
    help = "Puebla la base de datos con datos de prueba para doctors, patients y bookings."

    def handle(self, *args, **options):
        self.stdout.write("🔄 Iniciando población de datos…\n")

        self.create_groups()
        doctors = self.create_doctors()
        self.create_departments()
        self.create_availabilities(doctors)
        self.create_doctor_notes(doctors)

        patients = self.create_patients()
        self.create_insurances(patients)
        self.create_medical_records(patients)

        self.create_appointments(doctors, patients)
        self.create_booking_notes()

        self.stdout.write(self.style.SUCCESS("\n✅ ¡Datos de prueba insertados con éxito!"))

    def create_groups(self):
        for name in ("doctor", "patient"):
            grp, created = Group.objects.get_or_create(name=name)
            status = "creado" if created else "existía"
            self.stdout.write(f"  • Grupo `{name}`: {status}")

    def create_doctors(self):
        doctors = []
        for i in range(1, 4):
            uname = f"dr{i}"
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    "first_name": f"Doc{i}",
                    "last_name": "Demo",
                    "email": f"dr{i}@example.com"
                }
            )
            if created:
                user.set_password("Pass1234!")
                user.save()
            user.groups.add(Group.objects.get(name="doctor"))

            doc, doc_created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "qualification": "MD",
                    "contact_number": f"+57 30000000{i}",
                    "email": user.email,
                    "address": f"Calle Falsa {i}",
                    "biography": "Especialista en medicina general.",
                    "is_on_vacation": False
                }
            )
            status = "creado" if doc_created else "existía"
            self.stdout.write(f"  • Doctor `{uname}`: {status}")
            doctors.append(doc)
        return doctors

    def create_departments(self):
        specs = [
            ("Cardiology", "Corazón y sistema vascular"),
            ("Dermatology", "Piel y anexos"),
            ("Pediatrics", "Salud infantil")
        ]
        for name, desc in specs:
            dept, created = Department.objects.get_or_create(
                name=name, defaults={"description": desc}
            )
            status = "creado" if created else "existía"
            self.stdout.write(f"  • Departamento `{name}`: {status}")

    def create_availabilities(self, doctors):
        today = datetime.date.today()
        for doc in doctors:
            for slot in range(3):
                start_time = datetime.time(8 + slot*2, 0)
                end_time   = datetime.time(12 + slot*2, 0)
                avail, created = DoctorAvailability.objects.get_or_create(
                    doctor=doc,
                    start_date=today,
                    end_date=today + datetime.timedelta(days=30),
                    start_time=start_time,
                    end_time=end_time
                )
                status = "creada" if created else "existía"
                self.stdout.write(
                    f"     – Disponibilidad Dr.{doc.user.username}: "
                    f"{start_time}-{end_time} {status}"
                )

    def create_doctor_notes(self, doctors):
        for doc in doctors:
            for text in ("Revisar protocolos", "Reunión de equipo", "Actualizar docs"):
                note, created = DoctorNote.objects.get_or_create(
                    doctor=doc,
                    defaults={"note": text, "date": datetime.date.today()}
                )
                status = "creada" if created else "existía"
                self.stdout.write(
                    f"     – Nota Médico Dr.{doc.user.username}: {status}"
                )

    def create_patients(self):
        patients = []
        for i in range(1, 6):
            uname = f"pt{i}"
            user, created = User.objects.get_or_create(
                username=uname,
                defaults={
                    "first_name": f"Pac{i}",
                    "last_name": "Demo",
                    "email": f"pt{i}@example.com"
                }
            )
            if created:
                user.set_password("Pass1234!")
                user.save()
            user.groups.add(Group.objects.get(name="patient"))

            pat, pat_created = Patient.objects.get_or_create(
                user=user,
                defaults={
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "date_of_birth": datetime.date(1990, i, 1),
                    "contact_number": f"+57 31000000{i}",
                    "email": user.email,
                    "address": f"Avenida Demo {i}",
                    "medical_history": "Sin antecedentes."
                }
            )
            status = "creado" if pat_created else "existía"
            self.stdout.write(f"  • Paciente `{uname}`: {status}")
            patients.append(pat)
        return patients

    def create_insurances(self, patients):
        for pat in patients:
            ins, created = Insurance.objects.get_or_create(
                patient=pat,
                defaults={
                    "provider": random.choice(["Sura", "Colsanitas", "Sanitas"]),
                    "policy_number": f"POL{pat.id:04d}",
                    "expiration_date": datetime.date.today() + datetime.timedelta(days=365)
                }
            )
            status = "creado" if created else "existía"
            self.stdout.write(f"     – Seguro Pac.{pat.user.username}: {status}")

    def create_medical_records(self, patients):
        for pat in patients:
            rec, created = MedicalRecord.objects.get_or_create(
                patient=pat,
                defaults={
                    "date": datetime.date.today(),
                    "diagnosis": "Chequeo general",
                    "treatment": "Ninguno",
                    "follow_up_date": datetime.date.today() + datetime.timedelta(days=30)
                }
            )
            status = "creado" if created else "existía"
            self.stdout.write(f"     – Registro médico Pac.{pat.user.username}: {status}")

    def create_appointments(self, doctors, patients):
        for i in range(1, 11):
            date_ = datetime.date.today() + datetime.timedelta(days=i)
            time_ = datetime.time((9 + i) % 24, 0)
            appt, created = Appointment.objects.get_or_create(
                patient=random.choice(patients),
                doctor=random.choice(doctors),
                appointment_date=date_,
                appointment_time=time_,
                defaults={
                    "notes": f"Cita #{i}",
                    "status": random.choice(["scheduled", "completed", "canceled"])
                }
            )
            status = "creada" if created else "existía"
            self.stdout.write(f"  • Cita #{i}: {date_} {time_} {status}")

    def create_booking_notes(self):
        for appt in Appointment.objects.all():
            note, created = BookingNote.objects.get_or_create(
                appointment=appt,
                defaults={"note": f"Nota cita {appt.id}", "date": appt.appointment_date}
            )
            status = "creada" if created else "existía"
            self.stdout.write(f"     – Nota Booking cita#{appt.id}: {status}")