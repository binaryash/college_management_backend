# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Faculty, Student, Subject, User
from .serializers import (
    FacultySerializer, StudentSerializer, 
    SubjectSerializer, UserSerializer
)

class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users to edit their own profile
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Check if the object has a user attribute
        user_attr = getattr(obj, 'user', None)
        if user_attr:
            return obj.user == request.user
        return False

class IsFacultyUser(permissions.BasePermission):
    """
    Custom permission for faculty-only actions
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 'faculty'

class FacultyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Faculty operations
    """
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on user type:
        - Admin can see all faculty
        - Faculty can only see their own profile
        """
        user = self.request.user
        if user.is_superuser:
            return Faculty.objects.all()
        return Faculty.objects.filter(user=user)

    @action(detail=True, methods=['get'], permission_classes=[IsFacultyUser])
    def my_students(self, request, pk=None):
        """Get all students enrolled in faculty's subjects"""
        faculty = self.get_object()
        subjects = Subject.objects.filter(faculty=faculty)
        if subjects.exists():
            students = Student.objects.filter(subjects__in=subjects).distinct()
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)
        return Response(
            {"detail": "No subjects assigned"}, 
            status=status.HTTP_404_NOT_FOUND
        )

    @action(detail=True, methods=['post'], permission_classes=[IsFacultyUser])
    def add_student(self, request, pk=None):
        """Add student to faculty's subject"""
        faculty = self.get_object()
        subject_id = request.data.get('subject_id')
        student_id = request.data.get('student_id')

        if not subject_id or not student_id:
            return Response(
                {"detail": "Both subject_id and student_id are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subject = Subject.objects.get(id=subject_id, faculty=faculty)
            student = Student.objects.get(id=student_id)
            subject.enrolled_students.add(student)
            return Response(
                {"detail": "Student added successfully"}, 
                status=status.HTTP_200_OK
            )
        except Subject.DoesNotExist:
            return Response(
                {"detail": "Subject not found or not assigned to faculty"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Student.DoesNotExist:
            return Response(
                {"detail": "Student not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

class StudentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Student operations
    """
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, IsUserOrReadOnly]

    def get_queryset(self):
        """
        Filter queryset based on user type:
        - Faculty can see students in their subjects
        - Students can only see their own profile
        - Admin can see all students
        """
        user = self.request.user
        if user.is_superuser:
            return Student.objects.all()
        if user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=user)
            return Student.objects.filter(subjects__faculty=faculty).distinct()
        return Student.objects.filter(user=user)
    



    @action(detail=True, methods=['patch'], permission_classes=[IsUserOrReadOnly])
    def update_student(self, request, pk=None):
        """
        Custom action to update a student's details.
        """
        student = self.get_object()
        
        # Ensure that the requesting user is the student themselves or an admin
        if student.user != request.user and not request.user.is_superuser:
            return Response({"detail": "You do not have permission to edit this student."}, 
                            status=status.HTTP_403_FORBIDDEN)

        # Perform update
        serializer = StudentSerializer(student, data=request.data, partial=True)  # partial=True allows partial updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






    

    @action(detail=True, methods=['get'])
    def my_subjects(self, request, pk=None):
        """Get all subjects enrolled by student"""
        student = self.get_object()
        subjects = student.subjects.all()
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)

    '''def perform_create(self, serializer):
        """Ensure student user_type is set correctly"""
        serializer.save(user_type='student')'''

class SubjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Subject operations
    """
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter subjects based on user type:
        - Faculty sees their assigned subjects
        - Students see their enrolled subjects
        - Admin sees all subjects
        """
        user = self.request.user
        if user.is_superuser:
            return Subject.objects.all()
        if user.user_type == 'faculty':
            return Subject.objects.filter(faculty__user=user)
        return Subject.objects.filter(enrolled_students__user=user)

    def perform_create(self, serializer):
        """Set faculty automatically for faculty users"""
        if self.request.user.user_type == 'faculty':
            faculty = Faculty.objects.get(user=self.request.user)
            serializer.save(faculty=faculty)
        else:
            serializer.save()