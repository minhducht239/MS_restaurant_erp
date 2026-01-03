from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    loyalty_tier = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'phone', 'loyalty_points', 'total_spent', 'last_visit', 'visit_count', 'loyalty_tier', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_loyalty_tier(self, obj):
        return obj.get_loyalty_tier()
