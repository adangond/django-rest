django-rest

Table of Contents
- Overview
- Features
- Architecture
- Permission Levels
- Getting Started
- Prerequisites
- Installation
- Configuration
- Database Setup
- Running the Application
- API Documentation
- Usage
- Authentication
- Common Endpoints
- Requirements
- Contributing
- License
- Contact

Overview
django-rest is a modular Django REST Framework project managing a clinical scheduling system across three core apps:
- doctors: professional profiles, departments, availability, and medical notes
- patients: demographic data, insurance details, and medical history
- bookings: appointment scheduling and related notes

It relies on Django’s session-based authentication and group-based permissions (admin, doctor, patient) to enforce access control. Interactive API docs are provided via drf-spectacular.

Features
- Separate apps for doctors, patients, and bookings
- Session authentication (no JWT)
- Group-based permissions for admin, doctor, and patient roles
- SQLite3 as the development and testing database
- Management command to populate test data (`populate_db.py`)
- Swagger/OpenAPI schema and interactive UI

Architecture
Project root (`django-rest/`):
django-rest/
├── doctorapp/            # Project settings, root URLs, global permissions
├── doctors/              # Doctor profiles, departments, availability, medical notes
├── patients/             # Patient data, insurance, medical history
├── bookings/             # Appointment scheduling and related notes
│   └── management/
│       └── commands/
│           └── populate_db.py   # Management command to seed test data
├── docs/                 # drf-spectacular schema & Swagger UI
├── requirements.txt      # Project dependencies
└── manage.py             # Django CLI entry point

Each app follows Django conventions and includes:
- models.py           # Database models
- serializers.py      # DRF serializers
- views.py            # ModelViewSets for API endpoints
- permissions.py      # Custom permission classes
- urls.py             # Router registrations

Permission Levels
Access is determined by Django groups and enforced in viewsets:

| Role    | List/Retrieve | Create                | Update Own         | Delete Own         |
|---------|---------------|----------------------|--------------------|--------------------|
| admin   | Yes           | Yes                  | Any                | Any                |
| doctor  | Yes           | Appointments & Notes | Own records only   | Own records only   |
| patient | Yes           | Appointments         | Own records only   | Own records only   |

Getting Started

Prerequisites
- Python 3.10 or higher
- Git 2.30 or higher
- Virtual environment tool (venv or virtualenv)

Installation
```bash
git clone https://github.com/adangond/django-rest.git
cd django-rest
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configuration
- Open `doctorapp/settings.py` and set your `SECRET_KEY` and `DEBUG` mode.
- Ensure `INSTALLED_APPS` includes:
  - rest_framework
  - django_filters
  - drf_spectacular
  - doctors
  - patients
  - bookings
  - docs
- Confirm `REST_FRAMEWORK` settings use session authentication and drf-spectacular:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
}
```

Database Setup
```bash
python manage.py migrate
python manage.py populate_db
```
The `populate_db` command lives in `bookings/management/commands/` and seeds users, groups, and sample data.

Running the Application
```bash
python manage.py runserver
```
Browse to [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to explore.

API Documentation
- Schema JSON: `GET /api/schema/`
- Swagger UI: `GET /api/docs/`

Usage

Authentication
- Log in via Django’s browsable API at `/api-auth/login/`.
- Log out via `/api-auth/logout/`.
- Use session cookies for subsequent requests.

Common Endpoints

| Endpoint                                   | Method | Description                              |
|---------------------------------------------|--------|------------------------------------------|
| /api/doctors/                              | GET    | List all doctors                         |
| /api/doctors/                              | POST   | Create a new doctor                      |
| /api/doctors/{id}/                         | GET    | Retrieve a doctor profile                |
| /api/doctors/{id}/                         | PUT    | Update a doctor profile                  |
| /api/doctors/{id}/                         | PATCH  | Partial update of a doctor profile       |
| /api/doctors/{id}/                         | DELETE | Delete a doctor profile                  |
| /api/patients/                             | GET    | List all patients                        |
| /api/patients/                             | POST   | Create a new patient                     |
| /api/patients/{id}/                        | GET    | Retrieve a patient profile               |
| /api/patients/{id}/                        | PUT    | Update a patient profile                 |
| /api/patients/{id}/                        | PATCH  | Partial update of a patient profile      |
| /api/patients/{id}/                        | DELETE | Delete a patient profile                 |
| /api/bookings/                             | GET    | List all appointments                    |
| /api/bookings/                             | POST   | Create a new appointment                 |
| /api/bookings/{id}/                        | GET    | Retrieve an appointment                  |
| /api/bookings/{id}/                        | PUT    | Update an appointment                    |
| /api/bookings/{id}/                        | PATCH  | Partial update of an appointment         |
| /api/bookings/{id}/                        | DELETE | Delete an appointment                    |
| /api/bookings/{id}/medical-notes/          | GET    | List notes for a specific appointment    |
| /api/bookings/{id}/medical-notes/          | POST   | Add a note to a specific appointment     |

Requirements
```
asgiref==3.9.1
Django==5.2.4
django-filter==25.1
djangorestframework==3.16.0
Markdown==3.8.2
sqlparse==0.5.3
```

Contributing
- Fork the repository and create a feature branch.
- Write clear, focused commits.
- Follow PEP 8 and run local linters.
- Open a Pull Request against main, describing your changes.

License
This project is licensed under the MIT License. See LICENSE for details.

Contact
For questions or support, reach out to:
- Alvaro Dangond
- Email: alvaro_dangond@hotmail.com
- GitHub: https://github.com/adangond/django-rest

---

Beyond this README, you might consider adding:
- A GitHub Actions workflow for CI/CD including linting, migrations, and security scans
- Docker Compose files for local and staging environments
- Sentry or Prometheus integration for real-time monitoring
- A CONTRIBUTING.md with detailed guidelines on code reviews and testing
- A CHANGELOG.md to track breaking changes and versioned