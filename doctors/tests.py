from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from doctors.models import (
    Doctor,
    Department,
    DoctorAvailability,
    MedicalNote
)
from patients.models import Patient
from bookings.models import Appointment


class DoctorAPITestCase(APITestCase):
    def setUp(self):
        # Grupos
        self.admin_group = Group.objects.create(name="admin")
        self.doctor_group = Group.objects.create(name="doctor")

        # Usuarios
        self.admin_user = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )
        self.doctor_user = User.objects.create_user(
            username="doctor", password="doctorpass"
        )
        self.doctor_user.groups.add(self.doctor_group)

        self.other_doctor_user = User.objects.create_user(
            username="doctor2", password="doctor2pass"
        )
        self.other_doctor_user.groups.add(self.doctor_group)

        # Perfiles de doctor
        self.doctor = Doctor.objects.create(
            user=self.doctor_user,
            first_name="Gregory",
            last_name="House",
            qualification="MD",
            contact_number="1234567890",
            email="house@example.com",
            address="Princeton Plainsboro",
            biography="Diagnostic genius.",
            is_on_vacation=False
        )
        self.other_doctor = Doctor.objects.create(
            user=self.other_doctor_user,
            first_name="James",
            last_name="Wilson",
            qualification="Oncologist",
            contact_number="0987654321",
            email="wilson@example.com",
            address="Princeton Plainsboro",
            biography="Oncology expert.",
            is_on_vacation=False
        )

        # Departamento
        self.department = Department.objects.create(
            name="Diagnostics",
            description="Diagnostic Medicine"
        )

        # Disponibilidad de doctor
        self.availability = DoctorAvailability.objects.create(
            doctor=self.doctor,
            start_date="2025-01-01",
            end_date="2025-01-10",
            start_time="09:00",
            end_time="17:00"
        )

        # Nota médica
        self.note = MedicalNote.objects.create(
            doctor=self.doctor,
            note="Patient stable.",
            date="2025-01-02"
        )

        # Cliente sin autenticar
        self.client = APIClient()

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def create_and_authenticate_patient(self, username, first_name, last_name):
        user = User.objects.create_user(username=username, password="patientpass")
        patient = Patient.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            date_of_birth="1990-01-01",
            contact_number="3000000000",
            email=f"{username}@example.com",
            address="Dirección genérica",
            medical_history="Sin antecedentes"
        )
        self.authenticate(user)
        return patient

    # --- DoctorViewSet estándar ---

    def test_doctor_list_public(self):
        url = '/api/doctors/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

    def test_doctor_detail_public(self):
        url = f'/api/doctors/{self.doctor.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.doctor_user.id)

    def test_doctor_create_admin(self):
        self.authenticate(self.admin_user)
        url = '/api/doctors/'
        new_user_id = User.objects.create_user(username="newdoc").id
        data = {
            "user": new_user_id,
            "first_name": "Lisa",
            "last_name": "Cuddy",
            "qualification": "Hospital Director",
            "contact_number": "5555555555",
            "email": "cuddy@example.com",
            "address": "Princeton Plainsboro",
            "biography": "Hospital admin.",
            "is_on_vacation": False
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_doctor_update_owner(self):
        self.authenticate(self.doctor_user)
        url = f'/api/doctors/{self.doctor.id}/'
        data = {
            "user": self.doctor_user.id,
            "first_name": "GregoryUpdated",
            "last_name": "House",
            "qualification": "MD",
            "contact_number": "1234567890",
            "email": "house@example.com",
            "address": "Princeton Plainsboro",
            "biography": "Diagnostic genius.",
            "is_on_vacation": False
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "GregoryUpdated")

    def test_doctor_delete_admin(self):
        self.authenticate(self.admin_user)
        url = f'/api/doctors/{self.doctor.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # --- DepartmentViewSet ---

    def test_department_list_public(self):
        url = '/api/doctors/departments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_department_create_admin(self):
        self.authenticate(self.admin_user)
        url = '/api/doctors/departments/'
        data = {"name": "Cardiology", "description": "Heart medicine"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- DoctorAvailabilityViewSet ---

    def test_availability_list_public(self):
        url = '/api/doctors/availabilities/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_availability_create_owner(self):
        self.authenticate(self.doctor_user)
        url = '/api/doctors/availabilities/'
        data = {
            "doctor": self.doctor.id,
            "start_date": "2025-02-01",
            "end_date": "2025-02-10",
            "start_time": "08:00",
            "end_time": "16:00"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- MedicalNoteViewSet ---

    def test_note_list_owner(self):
        self.authenticate(self.doctor_user)
        url = '/api/doctors/notes/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_note_create_owner(self):
        self.authenticate(self.doctor_user)
        url = '/api/doctors/notes/'
        data = {
            "doctor": self.doctor.id,
            "note": "New note.",
            "date": "2025-01-03"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- Acciones personalizadas: appointments ---

    def test_appointments_get_by_patient(self):
        patient = self.create_and_authenticate_patient(
            "patient1", "Ana", "Gómez"
        )
        url = f'/api/doctors/{self.doctor.id}/appointments/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_appointments_post_success(self):
        patient = self.create_and_authenticate_patient(
            "patient2", "John", "Doe"
        )
        url = f'/api/doctors/{self.doctor.id}/appointments/'
        data = {
            "appointment_date": "2025-01-05",
            "appointment_time": "10:00",
            "notes": "Consulta general",
            "status": "pending"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['doctor'], self.doctor.id)
        self.assertEqual(response.data['patient'], patient.id)

    def test_appointments_post_denied_if_on_vacation(self):
        self.doctor.is_on_vacation = True
        self.doctor.save()

        patient = self.create_and_authenticate_patient(
            "patient3", "Laura", "Mendoza"
        )
        url = f'/api/doctors/{self.doctor.id}/appointments/'
        data = {
            "appointment_date": "2025-01-06",
            "appointment_time": "11:00",
            "notes": "Urgencia leve",
            "status": "pending"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            "vacaciones",
            response.data.get('detail', '').lower()
        )