#/doctors/urls.py

from rest_framework.routers import DefaultRouter

from .views import (
    DoctorViewSet,
    DepartmentViewSet,
    DoctorAvailabilityViewSet,
    MedicalNoteViewSet,
)

router = DefaultRouter()

# Endpoints para doctores:
#   GET    /api/doctors/           → lista doctores
#   POST   /api/doctors/           → crear doctor (solo admin)
#   GET    /api/doctors/{pk}/      → detalle doctor
#   PUT    /api/doctors/{pk}/      → actualizar doctor (dueño/admin)
#   DELETE /api/doctors/{pk}/      → borrar doctor (dueño/admin)
router.register(r'', DoctorViewSet, basename='doctor')

# Endpoints para departamentos:
#   GET    /api/doctors/departments/
#   POST   /api/doctors/departments/        (solo admin)
#   GET    /api/doctors/departments/{pk}/
#   PUT    /api/doctors/departments/{pk}/    (solo admin)
#   DELETE /api/doctors/departments/{pk}/    (solo admin)
router.register(r'departments', DepartmentViewSet, basename='department')

# Endpoints para disponibilidades de doctores:
#   GET    /api/doctors/availabilities/
#   POST   /api/doctors/availabilities/      (dueño doctor/admin)
#   GET    /api/doctors/availabilities/{pk}/
#   PUT    /api/doctors/availabilities/{pk}/  (dueño doctor/admin)
#   DELETE /api/doctors/availabilities/{pk}/  (dueño doctor/admin)
router.register(r'availabilities', DoctorAvailabilityViewSet, basename='availability')

# Endpoints para notas médicas de doctor:
#   GET    /api/doctors/notes/
#   POST   /api/doctors/notes/               (dueño doctor/admin)
#   GET    /api/doctors/notes/{pk}/
#   PUT    /api/doctors/notes/{pk}/           (dueño doctor/admin)
#   DELETE /api/doctors/notes/{pk}/           (dueño doctor/admin)
router.register(r'notes', MedicalNoteViewSet, basename='doctornote')

urlpatterns = router.urls