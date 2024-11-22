# core/urls.py (App URLs)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FacultyViewSet, StudentViewSet, SubjectViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'faculty', FacultyViewSet, basename='faculty')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'subjects', SubjectViewSet, basename='subject')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]

"""
Available API Endpoints:

Authentication:
POST /api/token/ - Obtain JWT token pair
POST /api/token/refresh/ - Refresh JWT token

Faculty Endpoints:
GET /api/faculty/ - List all faculty
POST /api/faculty/ - Create new faculty
GET /api/faculty/{id}/ - Retrieve faculty details
PUT /api/faculty/{id}/ - Update faculty details
DELETE /api/faculty/{id}/ - Delete faculty
GET /api/faculty/{id}/my_students/ - Get faculty's students
POST /api/faculty/{id}/add_student/ - Add student to faculty's subject

Student Endpoints:
GET /api/students/ - List all students (faculty) or get own profile (student)
POST /api/students/ - Create new student
GET /api/students/{id}/ - Retrieve student details
PUT /api/students/{id}/ - Update student details
DELETE /api/students/{id}/ - Delete student
GET /api/students/{id}/my_subjects/ - Get student's subjects

Subject Endpoints:
GET /api/subjects/ - List subjects
POST /api/subjects/ - Create new subject
GET /api/subjects/{id}/ - Retrieve subject details
PUT /api/subjects/{id}/ - Update subject details
DELETE /api/subjects/{id}/ - Delete subject

Admin Interface:
/admin/ - Django admin interface
"""