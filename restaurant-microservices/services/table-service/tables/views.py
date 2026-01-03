from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Table, TableOrder, TableOrderItem
from .serializers import TableSerializer, TableOrderSerializer, TableOrderItemSerializer
from .service_client import BillingServiceClient


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'floor']
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        table = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Table.STATUS_CHOICES):
            table.status = new_status
            table.save()
            return Response({'success': True, 'status': table.status})
        return Response({'error': 'Invalid status'}, status=400)
    
    @action(detail=True, methods=['post'])
    def create_order(self, request, pk=None):
        table = self.get_object()
        
        # Check if table already has active order
        if table.orders.filter(is_completed=False).exists():
            return Response({'error': 'Table already has active order'}, status=400)
        
        order = TableOrder.objects.create(
            table=table,
            created_by_id=request.user.id if hasattr(request.user, 'id') else None,
            created_by_name=getattr(request.user, 'username', ''),
            notes=request.data.get('notes', '')
        )
        
        # Update table status
        table.status = 'occupied'
        table.save()
        
        return Response(TableOrderSerializer(order).data, status=201)
    
    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        table = self.get_object()
        order = table.orders.filter(is_completed=False).first()
        
        if not order:
            return Response({'error': 'No active order'}, status=400)
        
        try:
            # Support both single item and array of items
            items_data = request.data if isinstance(request.data, list) else [request.data]
            created_items = []
            
            for item_data in items_data:
                # Ensure price is numeric
                price = item_data.get('price', 0)
                if isinstance(price, str):
                    price = float(price.replace(',', ''))
                
                item = TableOrderItem.objects.create(
                    order=order,
                    menu_item_id=item_data.get('menu_item_id'),
                    name=item_data.get('name', 'Unknown'),
                    quantity=int(item_data.get('quantity', 1)),
                    price=price,
                    notes=item_data.get('notes', '')
                )
                created_items.append(item)
            
            # Return single item or list based on input
            if len(created_items) == 1:
                return Response(TableOrderItemSerializer(created_items[0]).data, status=201)
            return Response(TableOrderItemSerializer(created_items, many=True).data, status=201)
        except Exception as e:
            return Response({'error': str(e)}, status=500)
    
    @action(detail=True, methods=['post'])
    def complete_order(self, request, pk=None):
        table = self.get_object()
        order = table.orders.filter(is_completed=False).first()
        
        if not order:
            return Response({'error': 'No active order'}, status=400)
        
        # Create bill in billing-service
        billing_client = BillingServiceClient()
        bill_result = billing_client.create_bill_from_order(order)
        
        if not bill_result['success']:
            return Response({
                'error': 'Failed to create bill',
                'details': bill_result.get('error')
            }, status=500)
        
        # Mark order as completed
        order.is_completed = True
        order.save()
        
        # Update table status
        table.status = 'available'
        table.save()
        
        return Response({
            'success': True,
            'message': 'Order completed and bill created',
            'order': TableOrderSerializer(order).data,
            'bill': bill_result['bill'],
            'total': order.get_total()
        })
    
    @action(detail=False, methods=['get'])
    def by_floor(self, request):
        result = {}
        for floor_code, floor_name in Table.FLOOR_CHOICES:
            tables = Table.objects.filter(floor=floor_code)
            result[floor_name] = TableSerializer(tables, many=True).data
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def orders(self, request, pk=None):
        """Get current active order items for a table"""
        table = self.get_object()
        order = table.orders.filter(is_completed=False).first()
        
        if not order:
            return Response([])
        
        # Return items of the current order
        return Response(TableOrderItemSerializer(order.items.all(), many=True).data)
    
    @action(detail=True, methods=['post'])
    def create_bill(self, request, pk=None):
        """Create a bill from table's current order"""
        table = self.get_object()
        order = table.orders.filter(is_completed=False).first()
        
        if not order:
            return Response({'error': 'Không có đơn hàng active'}, status=400)
        
        if order.items.count() == 0:
            return Response({'error': 'Đơn hàng không có món nào'}, status=400)
        
        # Get customer info from request
        customer_info = {
            'customer': request.data.get('customer', ''),
            'phone': request.data.get('phone', ''),
            'customer_id': request.data.get('customer_id'),
            'points_used': request.data.get('points_used', 0),
            'points_discount': request.data.get('points_discount', 0),
        }
        
        # Create bill in billing-service
        billing_client = BillingServiceClient()
        bill_result = billing_client.create_bill_from_order(order, customer_info)
        
        if not bill_result['success']:
            return Response({
                'error': 'Không thể tạo hóa đơn',
                'details': bill_result.get('error')
            }, status=500)
        
        # Mark order as completed
        order.is_completed = True
        order.save()
        
        # Update table status to available
        table.status = 'available'
        table.save()
        
        return Response({
            'success': True,
            'message': 'Hóa đơn đã được tạo thành công',
            'bill_id': bill_result['bill'].get('id'),
            'bill': bill_result['bill'],
            'total': order.get_total()
        })


class TableOrderViewSet(viewsets.ModelViewSet):
    queryset = TableOrder.objects.all()
    serializer_class = TableOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['table', 'is_completed']
