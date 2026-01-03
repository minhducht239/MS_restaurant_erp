from rest_framework import serializers
from .models import Staff

class StaffSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Staff
        fields = ['id', 'name', 'phone', 'role', 'role_display', 'salary', 'hire_date', 'is_active', 'created_at', 'updated_at']
