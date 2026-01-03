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
            'id', 'customer', 'phone', 'date', 'total',
            'staff_id', 'staff_name', 'notes', 'items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BillCreateSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True)
    
    class Meta:
        model = Bill
        fields = ['customer', 'phone', 'date', 'total', 'staff_id', 'staff_name', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        bill = Bill.objects.create(**validated_data)
        
        for item_data in items_data:
            BillItem.objects.create(bill=bill, **item_data)
        
        return bill


class BillDetailSerializer(BillSerializer):
    """Detailed bill serializer with items"""
    items = BillItemSerializer(many=True, read_only=True)
