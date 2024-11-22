# core/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Faculty, Student, Subject

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'contact_number', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }

class SubjectSerializer(serializers.ModelSerializer):
    faculty_name = serializers.CharField(source='faculty.user.get_full_name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ('id', 'name', 'code', 'description', 'faculty', 'faculty_name')
        read_only_fields = ('id',)

class FacultySerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subjects_taught = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Faculty
        fields = ('id', 'user', 'department', 'qualification', 'date_joined', 'subjects_taught')
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        
        # Create user instance with user_type
        user_data['user_type'] = 'faculty'
        user = User.objects.create_user(**user_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        # Create faculty instance
        faculty = Faculty.objects.create(user=user, **validated_data)
        return faculty

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            
            # Update user fields
            for attr, value in user_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()
            
        # Update faculty fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    subjects = SubjectSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = ('id', 'user', 'profile_pic', 'date_of_birth', 'gender',
                 'blood_group', 'address', 'subjects', 'enrollment_date')
        read_only_fields = ('id', 'enrollment_date')
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)
        
        # Create user instance with user_type
        user = User.objects.create_user(
            **user_data,
            user_type='student'  # Set user_type here
        )
        
        if password:
            user.set_password(password)
            user.save()
        
        # Create student instance
        student = Student.objects.create(user=user, **validated_data)
        return student

    def update(self, instance, validated_data):
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            
            # Update user fields
            for attr, value in user_data.items():
                if attr == 'password' and value:
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            user.save()
        
        # Update student fields (excluding user data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
