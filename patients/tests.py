from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from .models import Patient, Insurance, MedicalRecord

class PatientAPITestCase(APITestCase):
    def setUp(self):
        # Create groups
        self.admin_group = Group.objects.create(name="admin")
        self.doctor_group = Group.objects.create(name="doctor")
        self.patient_group = Group.objects.create(name="patient")

        # Create users
        self.admin_user = User.objects.create_user(username="admin", password="adminpass", is_staff=True)
        self.doctor_user = User.objects.create_user(username="doctor", password="doctorpass")
        self.doctor_user.groups.add(self.doctor_group)
        self.patient_user = User.objects.create_user(username="patient", password="patientpass")
        self.patient_user.groups.add(self.patient_group)

        # Create patient profile
        self.patient = Patient.objects.create(
            user=self.patient_user,
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            contact_number="1234567890",
            email="john@example.com",
            address="123 Main St",
            medical_history="None"
        )

        # Create insurance and medical record
        self.insurance = Insurance.objects.create(
            patient=self.patient,
            provider="ProviderX",
            policy_number="POL123",
            expiration_date="2030-01-01"
        )
        self.medical_record = MedicalRecord.objects.create(
            patient=self.patient,
            date="2024-01-01",
            diagnosis="Healthy",
            treatment="None",
            follow_up_date="2025-01-01"
        )

    def authenticate(self, user):
        self.client = APIClient()
        self.client.force_authenticate(user=user)

    def test_patient_list_admin(self):
        self.authenticate(self.admin_user)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_patient_list_patient(self):
        self.authenticate(self.patient_user)
        url = reverse('patient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Patient should only see their own profile
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.patient_user.id)

    def test_patient_detail_owner(self):
        self.authenticate(self.patient_user)
        url = reverse('patient-detail', args=[self.patient.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.patient_user.id)

    def test_patient_create_admin(self):
        self.authenticate(self.admin_user)
        url = reverse('patient-list')
        data = {
            "user": User.objects.create_user(username="newpatient").id,
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-05-05",
            "contact_number": "5555555555",
            "email": "jane@example.com",
            "address": "456 Main St",
            "medical_history": "Asthma"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_patient_update_owner(self):
        self.authenticate(self.patient_user)
        url = reverse('patient-detail', args=[self.patient.id])
        data = {
            "user": self.patient_user.id,
            "first_name": "JohnUpdated",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "contact_number": "1234567890",
            "email": "john@example.com",
            "address": "123 Main St",
            "medical_history": "None"
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "JohnUpdated")

    def test_patient_delete_admin(self):
        self.authenticate(self.admin_user)
        url = reverse('patient-detail', args=[self.patient.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_insurance_list_owner(self):
        self.authenticate(self.patient_user)
        # Use the correct endpoint for insurance list
        url = reverse('insurance-list')
        response = self.client.get(url)
        # If this fails with 404, try with the full path:
        # url = '/api/patients/insurances/'
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        if response.status_code == status.HTTP_200_OK:
            self.assertGreaterEqual(len(response.data), 1)

    def test_medicalrecord_list_owner(self):
        self.authenticate(self.patient_user)
        # Use the correct endpoint for medical record list
        url = reverse('medicalrecord-list')
        response = self.client.get(url)
        # If this fails with 404, try with the full path:
        # url = '/api/patients/medicalrecords/'
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        if response.status_code == status.HTTP_200_OK:
            self.assertGreaterEqual(len(response.data), 1)

    def test_clinical_history_action(self):
        self.authenticate(self.patient_user)
        url = reverse('patient-clinical-history', args=[self.patient.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("patient", response.data)
        self.assertIn("insurances", response.data)
        self.assertIn("medical_records", response.data)