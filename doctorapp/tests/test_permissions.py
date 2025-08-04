import pytest
from django.contrib.auth.models import User, Group
from rest_framework.test import APIRequestFactory
from doctorapp.permissions import IsAdminUser, IsDoctorUser, IsPatientUser, IsOwnerOrAdmin

@pytest.fixture
def factory():
    return APIRequestFactory()

@pytest.fixture
def doctor_group():
    return Group.objects.get_or_create(name="doctor")[0]

@pytest.fixture
def patient_group():
    return Group.objects.get_or_create(name="patient")[0]

@pytest.fixture
def admin_user():
    return User.objects.create_user(username="admin", is_staff=True)

@pytest.fixture
def doctor_user(doctor_group):
    user = User.objects.create_user(username="doctor")
    user.groups.add(doctor_group)
    return user

@pytest.fixture
def patient_user(patient_group):
    user = User.objects.create_user(username="patient")
    user.groups.add(patient_group)
    return user

@pytest.fixture
def dummy_obj(patient_user):
    class Dummy:
        user = patient_user
    return Dummy()

@pytest.mark.django_db
def test_admin_permission(admin_user, factory):
    request = factory.get("/")
    request.user = admin_user
    assert IsAdminUser().has_permission(request, None)

@pytest.mark.django_db
def test_doctor_permission(doctor_user, factory):
    request = factory.get("/")
    request.user = doctor_user
    assert IsDoctorUser().has_permission(request, None)

@pytest.mark.django_db
def test_patient_permission(patient_user, factory):
    request = factory.get("/")
    request.user = patient_user
    assert IsPatientUser().has_permission(request, None)

@pytest.mark.django_db
def test_owner_or_admin_as_owner(patient_user, factory, dummy_obj):
    request = factory.get("/")
    request.user = patient_user
    assert IsOwnerOrAdmin().has_object_permission(request, None, dummy_obj)

@pytest.mark.django_db
def test_owner_or_admin_as_admin(admin_user, factory, dummy_obj):
    request = factory.get("/")
    request.user = admin_user
    assert IsOwnerOrAdmin().has_object_permission(request, None, dummy_obj)

@pytest.mark.django_db
def test_owner_or_admin_denied(factory, doctor_user, dummy_obj):
    request = factory.get("/")
    request.user = doctor_user
    assert not IsOwnerOrAdmin().has_object_permission(request, None, dummy_obj)