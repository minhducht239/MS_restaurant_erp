from rest_framework import serializers
from .models import Table, TableOrder, TableOrderItem


class TableOrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = TableOrderItem
        fields = ['id', 'menu_item_id', 'name', 'quantity', 'price', 'notes', 'subtotal', 'created_at']
    
    def get_subtotal(self, obj):
        return obj.get_subtotal()


class TableOrderSerializer(serializers.ModelSerializer):
    items = TableOrderItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = TableOrder
        fields = ['id', 'table', 'created_at', 'created_by_id', 'created_by_name', 'is_completed', 'notes', 'items', 'total']
    
    def get_total(self, obj):
        return obj.get_total()


class TableSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    floor_display = serializers.CharField(source='get_floor_display', read_only=True)
    current_order = serializers.SerializerMethodField()
    
    class Meta:
        model = Table
        fields = ['id', 'name', 'capacity', 'status', 'status_display', 'floor', 'floor_display', 'current_order', 'created_at', 'updated_at']
    
    def get_current_order(self, obj):
        order = obj.orders.filter(is_completed=False).first()
        if order:
            return TableOrderSerializer(order).data
        return None
