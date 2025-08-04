#/patients/urls.py

from rest_framework.routers import DefaultRouter

from .views import (
    PatientViewSet,
    InsuranceViewSet,
    MedicalRecordViewSet,
)

router = DefaultRouter()

# Endpoints para seguros de paciente:
#   GET    /api/patients/insurances/
#   POST   /api/patients/insurances/      (dueño paciente/admin)
#   GET    /api/patients/insurances/{pk}/
#   PUT    /api/patients/insurances/{pk}/  (dueño paciente/admin)
#   DELETE /api/patients/insurances/{pk}/  (dueño paciente/admin)
router.register(r'insurances', InsuranceViewSet, basename='insurance')

# Endpoints para registros médicos de paciente:
#   GET    /api/patients/medicalrecords/
#   POST   /api/patients/medicalrecords/      (dueño paciente/admin)
#   GET    /api/patients/medicalrecords/{pk}/
#   PUT    /api/patients/medicalrecords/{pk}/  (dueño paciente/admin)
#   DELETE /api/patients/medicalrecords/{pk}/  (dueño paciente/admin)
router.register(r'medicalrecords', MedicalRecordViewSet, basename='medicalrecord')

# Endpoints para pacientes:
#   GET    /api/patients/           → lista pacientes
#   POST   /api/patients/           → crear paciente (solo staff/autorizado)
#   GET    /api/patients/{pk}/      → detalle paciente
#   PUT    /api/patients/{pk}/      → actualizar paciente (dueño/admin)
#   DELETE /api/patients/{pk}/      → borrar paciente (solo admin)
router.register(r'', PatientViewSet, basename='patient')

urlpatterns = router.urls