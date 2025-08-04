import pytest
from django.contrib.auth.models import User
from patients.models import Patient, Insurance, MedicalRecord
from doctors.models import Doctor, Department, DoctorAvailability
from bookings.models import Appointment, MedicalNote
from datetime import date, time

# 🔧 Fixtures base
@pytest.fixture
def patient_user(db):
    return User.objects.create_user(username='patientuser', password='testpass')

@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(username='doctoruser', password='testpass')

@pytest.fixture
def patient(db, patient_user):
    return Patient.objects.create(
        user=patient_user,
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-01",
        contact_number="123456789",
        email="john@example.com",
        address="Calle 123",
        medical_history="Sin antecedentes relevantes"
    )

@pytest.fixture
def doctor(db, doctor_user):
    return Doctor.objects.create(
        user=doctor_user,
        first_name="Gregory",
        last_name="House",
        qualification="MD",
        contact_number="987654321",
        email="house@example.com",
        address="Hospital General",
        biography="Especialista en diagnóstico",
        is_on_vacation=False
    )

# 🧪 Pacientes
def test_patients_list(client, patient_user):
    client.force_login(patient_user)
    response = client.get('/api/patients/')
    assert response.status_code == 200

def test_patient_detail(client, patient_user, patient):
    client.force_login(patient_user)
    response = client.get(f'/api/patients/{patient.id}/')
    assert response.status_code == 200

def test_insurance_create(client, patient_user, patient):
    client.force_login(patient_user)
    response = client.post('/api/patients/insurances/', {
        "patient": patient.id,
        "provider": "SaludTotal",
        "policy_number": "ABC123",
        "expiration_date": "2026-01-01"
    })
    assert response.status_code in [200, 201]

def test_medical_record_create(client, patient_user, patient):
    client.force_login(patient_user)
    response = client.post('/api/patients/medicalrecords/', {
        "patient": patient.id,
        "date": "2025-08-01",
        "diagnosis": "Gripe",
        "treatment": "Reposo y líquidos",
        "follow_up_date": "2025-08-10"
    })
    assert response.status_code in [200, 201]

# 🧪 Doctores
def test_doctors_list(client, patient_user):
    client.force_login(patient_user)
    response = client.get('/api/doctors/')
    assert response.status_code == 200

def test_doctor_detail(client, patient_user, doctor):
    client.force_login(patient_user)
    response = client.get(f'/api/doctors/{doctor.id}/')
    assert response.status_code == 200

def test_department_create(client, doctor_user):
    client.force_login(doctor_user)
    response = client.post('/api/doctors/departments/', {
        "name": "Cardiología",
        "description": "Especialidad del corazón"
    })
    assert response.status_code in [200, 201]

def test_availability_create(client, doctor_user, doctor):
    client.force_login(doctor_user)
    response = client.post('/api/doctors/availabilities/', {
        "doctor": doctor.id,
        "start_date": "2025-08-05",
        "end_date": "2025-08-10",
        "start_time": "08:00",
        "end_time": "12:00"
    })
    assert response.status_code in [200, 201]

def test_doctor_note_create(client, doctor_user, doctor):
    client.force_login(doctor_user)
    response = client.post('/api/doctors/notes/', {
        "doctor": doctor.id,
        "note": "Paciente con hipertensión controlada.",
        "date": "2025-08-03"
    })
    assert response.status_code in [200, 201]

# 🧪 Citas
def test_appointment_create(client, patient_user, doctor):
    client.force_login(patient_user)
    response = client.post('/api/bookings/', {
        "doctor": doctor.id,
        "date": "2025-08-10",
        "time": "10:00"
    })
    assert response.status_code in [200, 201]

def test_appointment_list_as_doctor(client, doctor_user):
    client.force_login(doctor_user)
    response = client.get('/api/bookings/')
    assert response.status_code == 200

# 🧪 Notas médicas desde bookings
def test_medical_note_create_from_booking(client, doctor_user, doctor):
    client.force_login(doctor_user)
    response = client.post('/api/bookings/notes/', {
        "doctor": doctor.id,
        "note": "Seguimiento post consulta.",
        "date": "2025-08-03"
    })
    assert response.status_code in [200, 201]

def test_medical_notes_list_as_patient(client, patient_user):
    client.force_login(patient_user)
    response = client.get('/api/bookings/notes/')
    assert response.status_code == 200