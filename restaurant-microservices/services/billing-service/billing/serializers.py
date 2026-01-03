from rest_framework import serializers
from .models import Bill, BillItem


class BillItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = BillItem
        fields = ['id', 'menu_item_id', 'item_name', 'quantity', 'price', 'subtotal']


class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Bill
        fields = [
            'id', 'customer', 'phone', 'date', 'total', 'original_total',
            'staff_id', 'staff_name', 'notes', 'items',
            'customer_id', 'points_used', 'points_discount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BillCreateSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)
    id = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Bill
        fields = ['id', 'customer', 'phone', 'date', 'total', 'original_total',
                  'staff_id', 'staff_name', 'notes', 'items',
                  'customer_id', 'points_used', 'points_discount']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = Bill.objects.create(**validated_data)
        
        for item_data in items_data:
            BillItem.objects.create(bill=bill, **item_data)
        
        return bill
    
    def to_representation(self, instance):
        """Return full bill data including id after creation"""
        return BillSerializer(instance).data


class BillDetailSerializer(BillSerializer):
    """Detailed bill serializer with items"""
    items = BillItemSerializer(many=True, read_only=True)
