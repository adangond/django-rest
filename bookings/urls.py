#/bookings/urls.py

from rest_framework.routers import DefaultRouter

from .views import AppointmentViewSet, MedicalNoteViewSet

router = DefaultRouter()

# Notas médicas de cita:
#   GET    /api/bookings/notes/
#   POST   /api/bookings/notes/
#   GET    /api/bookings/notes/{pk}/
#   PUT    /api/bookings/notes/{pk}/
#   DELETE /api/bookings/notes/{pk}/
router.register(r'notes', MedicalNoteViewSet, basename='appointmentnote')


# Raíz:  GET /api/bookings/          → lista y crea citas
#         GET /api/bookings/{pk}/    → detalle, update, destroy
router.register(r'', AppointmentViewSet, basename='appointment')


urlpatterns = router.urls