from django.contrib import admin

# Register your models here.
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Faculty, Student, Subject

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin with additional fields
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser', 'groups')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'contact_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'contact_number', 'email', 
                      'first_name', 'last_name'),
        }),
    )

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """
    Faculty Admin configuration
    """
    list_display = ('get_full_name', 'department', 'qualification', 
                   'date_joined')
    search_fields = ('user__username', 'user__first_name', 
                    'user__last_name', 'department')
    list_filter = ('department', 'date_joined')

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """
    Student Admin configuration
    """
    list_display = ('get_full_name', 'gender', 'blood_group', 
                   'enrollment_date')
    list_filter = ('gender', 'blood_group', 'enrollment_date')
    search_fields = ('user__username', 'user__first_name', 
                    'user__last_name', 'address')
    filter_horizontal = ('subjects',)

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """
    Subject Admin configuration
    """
    list_display = ('code', 'name', 'faculty', 'get_students_count')
    search_fields = ('code', 'name', 'faculty__user__username')
    list_filter = ('faculty__department',)

    def get_students_count(self, obj):
        return obj.enrolled_students.count()
    get_students_count.short_description = 'Enrolled Students'